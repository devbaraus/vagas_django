from django.db.models import Q
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

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
    Beneficio,
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
    CandidatoListSerializer,
    EmpregadorListSerializer,
    EmpregadorCreateSerializer,
    CandidatoCreateSerializer,
    EmpresaCreateSerializer,
    AvaliacaoSerializer,
    CandidatoPerfilSerializer,
    EmpregadorPerfilSerializer,
    BeneficioSerializer,
    VagaCreateSerializer,
)


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
        "list": CandidatoListSerializer,
        "create": CandidatoCreateSerializer,
        "perfil": CandidatoPerfilSerializer,
    }
    queryset = Candidato.objects.all()
    permission_classes = [
        CreatePermission | OwnedByPermission | AdminPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

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

        selected_vaga = None

        if selecionado:
            selected_vaga = Candidato.objects.get(id=selecionado)
            filtering = filtering & ~Q(id=selecionado)

        queryset = Candidato.objects.filter(filtering)

        if selected_vaga:
            queryset = [selected_vaga] + list(queryset)

        queryset = self.filter_queryset(queryset)

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

        if selected_vaga:
            queryset = [selected_vaga] + list(queryset)

        queryset = self.filter_queryset(queryset)

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
