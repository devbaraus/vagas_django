from django.db import transaction
from rest_framework import mixins, viewsets, status
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
    User,
    UsuarioNivelChoices,
    Avaliacao,
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
    UserSerializer,
    CandidatoListSerializer,
    EmpregadorListSerializer,
    EmpregadorCreateSerializer,
    CandidatoCreateSerializer,
    EmpresaCreateSerializer,
    AvaliacaoSerializer,
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

    def update(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["usuario"] = request.data.get("usuario", request.user.id)
        request.data._mutable = False

        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["usuario"] = request.data.get("usuario", request.user.id)
        request.data._mutable = False

        return super().create(request, *args, **kwargs)


class UserViews(AbstractViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
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
    }
    queryset = Candidato.objects.all()
    permission_classes = [
        CreatePermission | OwnedByPermission | AdminPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def perform_create(self, serializer):
        with transaction.atomic():
            user_data = {
                "nome": serializer.validated_data.get("nome"),
                "cpf": serializer.validated_data.get("cpf"),
                "data_nascimento": serializer.validated_data.get("data_nascimento"),
                "sexo": serializer.validated_data.get("sexo"),
                "estado_civil": serializer.validated_data.get("estado_civil"),
                "tipo_deficiencia": serializer.validated_data.get("tipo_deficiencia"),
                "email": serializer.validated_data.get("email"),
                "telefone": serializer.validated_data.get("telefone"),
                # 'foto': serializer.validated_data.get('foto'),
                # 'curriculo': serializer.validated_data.get('curriculo'),
                "nivel_usuario": UsuarioNivelChoices.CANDIDATO,
            }

            user = Candidato(**user_data)
            user.save()

            objetivo_profissional_data = {
                "cargo": serializer.validated_data.get("cargo"),
                "salario": serializer.validated_data.get("salario"),
                "modelo_trabalho": serializer.validated_data.get("modelo_trabalho"),
                "jornada_trabalho": serializer.validated_data.get("jornada_trabalho"),
                "regime_contratual": serializer.validated_data.get("regime_contratual"),
            }

            objetivo_profissional = ObjetivoProfissional(**objetivo_profissional_data)
            objetivo_profissional.usuario = user
            objetivo_profissional.save()


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
        # ADMIN CRIANDO EMPRESA
        user = request.data.get("usuario", request.user.id)
        user = User.objects.get(id=user)

        if user.nivel_usuario != UsuarioNivelChoices.EMPREGADOR:
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


class EmpregadorViews(AbstractViewSet):
    serializers = {
        "default": EmpregadorSerializer,
        "create": EmpregadorCreateSerializer,
        "list": EmpregadorListSerializer,
    }
    queryset = Empregador.objects.all()
    permission_classes = [
        CreatePermission | AdminPermission | OwnedByPermission,
    ]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def perform_create(self, serializer):
        with transaction.atomic():
            user_data = {
                "nome": serializer.validated_data.get("nome"),
                "cpf": serializer.validated_data.get("cpf"),
                "data_nascimento": serializer.validated_data.get("data_nascimento"),
                "sexo": serializer.validated_data.get("sexo"),
                "estado_civil": serializer.validated_data.get("estado_civil"),
                "area_atuacao": serializer.validated_data.get("area_atuacao"),
                "cargo": serializer.validated_data.get("cargo"),
                "email": serializer.validated_data.get("email"),
                "telefone": serializer.validated_data.get("telefone"),
                "foto": serializer.validated_data.get("foto"),
                "curriculo": serializer.validated_data.get("curriculo"),
                "nivel_usuario": UsuarioNivelChoices.EMPREGADOR,
            }

            user = Empregador(**user_data)
            user.save()

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
                "numero_funcionarios": serializer.validated_data.get(
                    "numero_funcionarios"
                ),
                "telefone": serializer.validated_data.get("telefone"),
                "email": serializer.validated_data.get("email"),
                "site": serializer.validated_data.get("site"),
                "descricao": serializer.validated_data.get("descricao"),
            }

            empresa = Empresa(**empresa_data)
            empresa.usuario = user
            empresa.endereco = endereco
            empresa.save()


class CandidaturaViews(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
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


class ObjetivoProfissionalViews(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
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

    def update(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["usuario"] = request.data.get("usuario", request.user.id)
        request.data._mutable = False

        return super().update(request, *args, **kwargs)


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


class VagaViews(AbstractViewSet):
    serializer_class = VagaSerializer
    queryset = Vaga.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AdminPermission
        | (IsEmpregadorPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]


class AvaliacaoViews(AbstractViewSet):
    serializer_class = AvaliacaoSerializer
    queryset = Avaliacao.objects.all()
    permission_classes = [
        IsAuthenticated,
        AdminPermission
        | (IsCandidatoPermission & OwnedByPermission)
        | ReadOnlyPermission,
    ]
