from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from emprega.models import (
    Empresa,
    Candidatura,
    ObjetivoProfissional,
    Idioma,
    CursoEspecializacao,
    FormacaoAcademica,
    ExperienciaProfissional,
    Endereco,
    Vaga,
    Candidato,
    Empregador,
    Usuario,
    UsuarioNivelChoices,
    Avaliacao,
    Beneficio, Token, TokenTypeChoices,
)
from emprega.permissions import (
    AdminPermission,
    OwnedByPermission,
    CreatePermission,
    IsCandidatoPermission,
    IsEmpregadorPermission,
    ReadOnlyPermission,
    DetailPermission,
)
from emprega.serializers import (
    EmpresaSerializer,
    CandidaturaSerializer,
    ObjetivoProfissionalSerializer,
    IdiomaSerializer,
    CursoEspecializacaoSerializer,
    FormacaoAcademicaSerializer,
    ExperienciaProfissionalSerializer,
    EnderecoSerializer,
    VagaSerializer,
    CandidatoSerializer,
    EmpregadorSerializer,
    UsuarioSerializer,
    EmpregadorListSerializer,
    EmpregadorCreateSerializer,
    CandidatoCreateSerializer,
    EmpresaCreateSerializer,
    AvaliacaoSerializer,
    CandidatoPerfilSerializer,
    EmpregadorPerfilSerializer,
    BeneficioSerializer,
    VagaCreateSerializer, CPFPasswordResetSerializer, PasswordTokenSerializer, TokenSerializer,
)
from emprega.tasks import send_email_confirmation
from recomendacao.recommendation import recommend_vagas_tfidf, recommend_vagas_bert, recommend_candidatos_tfidf, \
    recommend_candidatos_bert

RECOMMENDATION_ALGORITHM = 'tfidf'


class AbstractViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission, OwnedByPermission]

    def check_empresa(self, request):
        empresa = request.data.get("empresa", request.user.empresa.id)
        empresa = Empresa.objects.get(id=empresa)

        if request.user.is_staff:
            return empresa

        if empresa.usuario != request.user:
            raise PermissionDenied

        return empresa

    def check_usuario(self, request):
        usuario = self.request.data.get("usuario", request.user.id)
        usuario = Usuario.objects.get(id=usuario)

        if request.user.is_staff:
            return usuario

        if usuario != request.user:
            raise PermissionDenied

        return usuario


class CandidatoPropertiesViewSet(AbstractViewSet):
    permission_classes = [
        IsAuthenticated,
        AdminPermission
        | (IsCandidatoPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [
                IsAuthenticated,
                AdminPermission | OwnedByPermission | IsEmpregadorPermission,
            ]
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve", "list"] and not self.request.user.is_staff:
            return self.queryset.filter(usuario=self.request.user)
        return self.queryset

    def perform_update(self, serializer):
        usuario = self.check_usuario(self.request)

        serializer.save(usuario=usuario)

    def perform_create(self, serializer):
        usuario = self.check_usuario(self.request)

        serializer.save(usuario=usuario)


class UserViews(AbstractViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated, AdminPermission]

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data.setdefault("nivel_usuario", UsuarioNivelChoices.ADMIN)
        request.data._mutable = False

        return super().create(request, *args, **kwargs)


class CandidatoViews(AbstractViewSet):
    serializers = {
        "default": CandidatoSerializer,
        "list": CandidatoPerfilSerializer,
        "create": CandidatoCreateSerializer,
        "perfil": CandidatoPerfilSerializer,
        "vaga": CandidatoPerfilSerializer,
    }
    queryset = Candidato.objects.all()
    permission_classes = [
        CreatePermission | OwnedByPermission | AdminPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    @action(
        detail=False, methods=["get"], url_path="vaga/(?P<vaga_id>[^/.]+)"
    )
    def vaga(self, request, vaga_id, *args, **kwargs):
        recomendacao = request.query_params.get('recomendacao', 'false') == 'true'

        vaga = get_object_or_404(Vaga, id=vaga_id)
        queryset = Candidato.objects.filter(candidaturas_usuario__vaga=vaga, esta_ativo=True)

        if recomendacao and vaga:
            if RECOMMENDATION_ALGORITHM == 'bert':
                queryset = recommend_candidatos_bert(queryset, vaga)
            if RECOMMENDATION_ALGORITHM == 'tfidf':
                queryset = recommend_candidatos_tfidf(queryset, vaga)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def curriculo(self, *args, **kwargs):
        candidato = self.get_object()
        return FileResponse(candidato.curriculo)

    @action(detail=False, methods=["GET"])
    def perfil(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(request.user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        selecionado = request.query_params.get("selecionado")
        termo = request.query_params.get("formacao_academica")
        salario = request.query_params.get("salario")
        modelo_trabalho = request.query_params.get("modelo_trabalho")
        jornada_trabalho = request.query_params.get("jornada_trabalho")
        regime_contratual = request.query_params.get("regime_contratual")
        vaga = request.query_params.get("vaga")
        recomendacao = request.query_params.get("recomendacao", False)

        vaga_obj = None

        if vaga:
            vaga_obj = get_object_or_404(Vaga, id=vaga)

        filtering = Q()

        if termo:
            filtering &= Q(objetivo_profissional_usuario__cargo__icontains=termo)

        if salario:
            filtering &= Q(objetivo_profissional_usuario__salario__gte=salario)

        if modelo_trabalho:
            filtering &= Q(objetivo_profissional_usuario__modelo_trabalho=modelo_trabalho)

        if jornada_trabalho:
            filtering &= Q(objetivo_profissional_usuario__jornada_trabalho=jornada_trabalho)

        if regime_contratual:
            filtering &= Q(objetivo_profissional_usuario__regime_contratual=regime_contratual)

        if vaga_obj:
            filtering &= Q(candidaturas_usuario__vaga=vaga_obj)

        selected_candidato = None

        if selecionado:
            selected_candidato = Candidato.objects.get(id=selecionado)
            filtering = filtering & ~Q(id=selecionado)

        queryset = Candidato.objects.filter(filtering)

        if recomendacao and vaga_obj:
            if RECOMMENDATION_ALGORITHM == 'bert':
                queryset = recommend_candidatos_bert(queryset, vaga_obj)
            if RECOMMENDATION_ALGORITHM == 'tfidf':
                queryset = recommend_candidatos_tfidf(queryset, vaga_obj)

        if selected_candidato:
            queryset = [selected_candidato] + list(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class EmpresaViews(AbstractViewSet):
    serializers = {
        "default": EmpresaSerializer,
        "create": EmpresaCreateSerializer,
    }
    queryset = Empresa.objects.all()
    filterset_fields = ["usuario"]
    permission_classes = [
        AdminPermission
        | (IsEmpregadorPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def create(self, request, *args, **kwargs):
        usuario = self.check_usuario(request)

        if usuario.nivel_usuario != UsuarioNivelChoices.EMPREGADOR:
            return Response(
                {"detail": "Usuário deve ser um empregador para cadastrar uma empresa"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        endereco_data = {
            "cep": serializer.validated_data.get("cep"),
            "logradouro": serializer.validated_data.get("logradouro"),
            "numero": serializer.validated_data.get("numero"),
            "complemento": serializer.validated_data.get("complemento"),
            "bairro": serializer.validated_data.get("bairro"),
            "cidade": serializer.validated_data.get("cidade"),
            "estado": serializer.validated_data.get("estado"),
        }

        endereco = Endereco(**endereco_data)
        endereco.save()

        empresa_data = {
            "razao_social": serializer.validated_data.get("razao_social"),
            "cnpj": serializer.validated_data.get("cnpj"),
            "nome_fantasia": serializer.validated_data.get("nome_fantasia"),
            "ramo_atividade": serializer.validated_data.get("ramo_atividade"),
            "numero_funcionarios": serializer.validated_data.get("numero_funcionarios"),
            "telefone": serializer.validated_data.get("telefone"),
            "email": serializer.validated_data.get("email"),
            "site": serializer.validated_data.get("site"),
            "descricao": serializer.validated_data.get("descricao"),
        }

        empresa = Empresa(**empresa_data)
        empresa.usuario = serializer.validated_data.get("usuario")
        empresa.endereco = endereco
        empresa.save()


class CandidaturaViews(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CandidaturaSerializer
    queryset = Candidatura.objects.all()
    permission_classes = [
        IsAuthenticated,
        AdminPermission
        | (IsCandidatoPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]

    def get_queryset(self):
        if self.action in ["retrieve", "list"] and self.request.user.is_candidato:
            return self.queryset.filter(usuario=self.request.user)
        if self.action in ["retrieve", "list"] and self.request.user.is_empregador:
            return self.queryset.filter(usuario=self.request.user.empresa)
        return self.queryset

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
            else:
                instance = get_object_or_404(
                    Candidatura,
                    vaga_id=request.data.get("vaga"),
                    usuario=request.data.get("usuario"),
                )
                instance.esta_ativo = True
                instance.save()
                serializer = self.get_serializer(instance)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def list(self, request, *args, **kwargs):
        ativo = request.query_params.get("esta_ativo", True)
        queryset = self.filter_queryset(self.get_queryset().filter(esta_ativo=ativo))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        candidatura = self.get_object()
        candidatura.esta_ativo = False
        candidatura.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ObjetivoProfissionalViews(
    AbstractViewSet,
):
    serializer_class = ObjetivoProfissionalSerializer
    queryset = ObjetivoProfissional.objects.all()
    permission_classes = [
        IsAuthenticated,
        AdminPermission
        | (IsCandidatoPermission & OwnedByPermission)
        | DetailPermission,
    ]

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [
                IsAuthenticated,
                AdminPermission | OwnedByPermission | IsEmpregadorPermission,
            ]
        return super().get_permissions()

    def perform_update(self, serializer):
        usuario = self.check_usuario(self.request)

        serializer.save(usuario=usuario)

    def perform_create(self, serializer):
        usuario = self.check_usuario(self.request)

        serializer.save(usuario=usuario)


class IdiomaViews(CandidatoPropertiesViewSet):
    serializer_class = IdiomaSerializer
    queryset = Idioma.objects.all()


class CursoEspecializacaoViews(CandidatoPropertiesViewSet):
    serializer_class = CursoEspecializacaoSerializer
    queryset = CursoEspecializacao.objects.all()


class FormacaoAcademicaViews(CandidatoPropertiesViewSet):
    serializer_class = FormacaoAcademicaSerializer
    queryset = FormacaoAcademica.objects.all()


class ExperienciaProfissionalViews(CandidatoPropertiesViewSet):
    serializer_class = ExperienciaProfissionalSerializer
    queryset = ExperienciaProfissional.objects.all()


class EnderecoViews(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EnderecoSerializer
    queryset = Endereco.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AdminPermission
        | (IsEmpregadorPermission & OwnedByPermission)
        | DetailPermission,
    ]


class BeneficioViews(AbstractViewSet):
    serializer_class = BeneficioSerializer
    queryset = Beneficio.objects.all()
    permission_classes = [IsAuthenticated, AdminPermission | ReadOnlyPermission]


class VagaViews(AbstractViewSet):
    serializers = {
        "default": VagaSerializer,
        "create": VagaCreateSerializer,
        "update": VagaCreateSerializer,
    }

    queryset = Vaga.objects.all()
    permission_classes = [
        AdminPermission
        | (IsEmpregadorPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    @action(
        detail=False, methods=["get"], url_path="candidaturas/(?P<candidato_id>[^/.]+)"
    )
    def candidaturas(self, request, candidato_id, *args, **kwargs):
        ativo = request.query_params.get("esta_ativo", True)

        candidato = get_object_or_404(Candidato, pk=candidato_id)
        queryset = self.get_queryset().filter(
            candidaturas_vaga__usuario=candidato, candidaturas_vaga__esta_ativo=ativo
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="empresa/(?P<empresa_id>[^/.]+)")
    def empresa(self, request, empresa_id, *args, **kwargs):
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        queryset = self.get_queryset().filter(empresa=empresa)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        selecionado = request.query_params.get("selecionado")
        termo = request.query_params.get("termo")
        empresa = request.query_params.get("empresa")
        salario = request.query_params.get("salario")
        modelo_trabalho = request.query_params.get("modelo_trabalho")
        jornada_trabalho = request.query_params.get("jornada_trabalho")
        regime_contratual = request.query_params.get("regime_contratual")
        recomendacao = request.query_params.get("recomendacao", "")

        filtering = Q()

        if termo:
            filtering &= (
                    Q(cargo__icontains=termo)
                    | Q(atividades__icontains=termo)
                    | Q(requisitos__icontains=termo)
            )

        if empresa:
            filtering &= Q(empresa__nome_fantasia__icontains=empresa) | Q(
                empresa__razao_social__icontains=empresa
            )

        if salario:
            filtering &= Q(salario__gte=salario)

        if modelo_trabalho:
            filtering &= Q(modelo_trabalho=modelo_trabalho)

        if jornada_trabalho:
            filtering &= Q(jornada_trabalho=jornada_trabalho)

        if regime_contratual:
            filtering &= Q(regime_contratual=regime_contratual)

        selected_vaga = None

        if selecionado:
            selected_vaga = Vaga.objects.get(id=selecionado)
            filtering = filtering & ~Q(id=selecionado)

        queryset = self.get_queryset().filter(filtering)

        if recomendacao:
            if RECOMMENDATION_ALGORITHM == "tfidf":
                queryset = recommend_vagas_tfidf(queryset, request.user)
            if RECOMMENDATION_ALGORITHM == "bert":
                queryset = recommend_vagas_bert(queryset, request.user)

        if selected_vaga:
            queryset = [selected_vaga] + list(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        empresa = self.check_empresa(self.request)

        serializer.save(empresa=empresa)

    def perform_create(self, serializer):
        empresa = self.check_empresa(self.request)

        serializer.save(empresa=empresa)

    @action(detail=True, methods=["GET"])
    def candidatos(self, request, *args, **kwargs):
        vaga = self.get_object()
        serializer = CandidatoSerializer(vaga.candidatos.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["PUT"], url_path="(?P<vaga_id>[^/.]+)/arquivar")
    def arquivar(self, request, vaga_id):
        vaga = get_object_or_404(Vaga, pk=vaga_id)
        vaga.esta_ativo = not vaga.esta_ativo
        vaga.save()
        serializer = VagaSerializer(vaga)
        return Response(serializer.data)

class AvaliacaoViews(AbstractViewSet):
    serializer_class = AvaliacaoSerializer
    queryset = Avaliacao.objects.all()
    permission_classes = [
        IsAuthenticated,
        AdminPermission
        | (IsCandidatoPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]


class EmpregadorViews(AbstractViewSet):
    serializers = {
        "default": EmpregadorSerializer,
        "create": EmpregadorCreateSerializer,
        "list": EmpregadorListSerializer,
        "perfil": EmpregadorPerfilSerializer,
    }
    queryset = Empregador.objects.all()
    permission_classes = [
        CreatePermission | AdminPermission | OwnedByPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    @action(detail=False, methods=["GET"])
    def perfil(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def empresa(self, request, *args, **kwargs):
        empregador = self.get_object()
        serializer = EmpresaSerializer(empregador.empresa)
        return Response(serializer.data)


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializers = {
        'post': CPFPasswordResetSerializer,
        'put': PasswordTokenSerializer
    }

    @property
    def serializer_class(self):
        return self.serializers.get(self.request.method.lower(), TokenSerializer)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(None, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get('token')
        password = serializer.validated_data.get('password')
        token_obj = get_object_or_404(Token, token=token, type=TokenTypeChoices.PASSWORD_RESET)

        user = token_obj.user

        if not token_obj.is_valid():
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({'success': 'Senha alterada'}, status=status.HTTP_200_OK)


class EmailVerificationView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        user = request.user

        if user.esta_verificado:
            return Response({'error': 'Email já verificado'}, status=status.HTTP_400_BAD_REQUEST)

        send_email_confirmation('email/confirmar_email.html', user.id)
        return Response({'success': 'Email enviado'}, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        token_obj = get_object_or_404(Token, token=token, type=TokenTypeChoices.EMAIL_CONFIRMATION)

        user = token_obj.user

        if not token_obj.is_valid():
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)

        user.esta_verificado = True
        user.save()

        return Response({'success': 'Email verificado'}, status=status.HTTP_200_OK)
