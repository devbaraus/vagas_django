from django.db import transaction
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from emprega.models import Empresa, Candidatura, ObjetivoProfissional, Idioma, CursoEspecializacao, \
    FormacaoAcademica, ExperienciaProfissional, Endereco, Vaga, Candidato, Empregador, User, UsuarioNivelChoices
from emprega.permissions import AdminPermission, OwnedByPermission, CreatePermission
from emprega.serializers import EmpresaSerializer, CandidaturaSerializer, \
    ObjetivoProfissionalSerializer, IdiomaSerializer, CursoEspecializacaoSerializer, FormacaoAcademicaSerializer, \
    ExperienciaProfissionalSerializer, EnderecoSerializer, VagaSerializer, CandidatoSerializer, EmpregadorSerializer, \
    UserSerializer, CandidatoListSerializer, EmpregadorListSerializer, EmpregadorCreateSerializer


class AbstractViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission, OwnedByPermission]


class UserViews(AbstractViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, AdminPermission]

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data.setdefault('nivel_usuario', UsuarioNivelChoices.ADMIN)
        request.data._mutable = False

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CandidatoViews(AbstractViewSet):
    serializers = {'default': CandidatoSerializer, 'list': CandidatoListSerializer}
    queryset = Candidato.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission | CreatePermission | OwnedByPermission]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data.setdefault('nivel_usuario', UsuarioNivelChoices.CANDIDATO)
        request.data._mutable = False

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmpresaViews(AbstractViewSet):
    serializer_class = EmpresaSerializer
    queryset = Empresa.objects.all()
    filterset_fields = ['usuario']

    def create(self, request, *args, **kwargs):
        user = request.data.get('usuario', request.user)

        if user.nivel_usuario == UsuarioNivelChoices.EMPREGADOR:
            return Response({'detail': 'Usuário deve ser um empregador para cadastrar uma empresa'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmpregadorViews(AbstractViewSet):
    serializers = {
        'default': EmpregadorSerializer,
        'create': EmpregadorCreateSerializer,
        'list': EmpregadorListSerializer
    }
    queryset = Empregador.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly | CreatePermission, AdminPermission | OwnedByPermission]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def perform_create(self, serializer):
        with transaction.atomic():
            user_data = {
                'nome': serializer.validated_data.get('nome'),
                'cpf': serializer.validated_data.get('cpf'),
                'data_nascimento': serializer.validated_data.get('data_nascimento'),
                'sexo': serializer.validated_data.get('sexo'),
                'estado_civil': serializer.validated_data.get('estado_civil'),
                'tipo_deficiencia': serializer.validated_data.get('tipo_deficiencia'),
                'area_atuacao': serializer.validated_data.get('area_atuacao'),
                'cargo': serializer.validated_data.get('cargo'),
                'email': serializer.validated_data.get('email'),
                'telefone': serializer.validated_data.get('telefone'),
                'foto': serializer.validated_data.get('foto'),
                'curriculo': serializer.validated_data.get('curriculo'),
                'nivel_usuario': UsuarioNivelChoices.EMPREGADOR
            }

            user = Empregador(**user_data)
            user.save()

            endereco_data = {
                'cep': serializer.validated_data.get('cep'),
                'logradouro': serializer.validated_data.get('logradouro'),
                'numero': serializer.validated_data.get('numero'),
                'complemento': serializer.validated_data.get('complemento'),
                'bairro': serializer.validated_data.get('bairro'),
                'cidade': serializer.validated_data.get('cidade'),
                'estado': serializer.validated_data.get('estado'),
            }

            endereco = Endereco(**endereco_data)
            endereco.save()

            empresa_data = {
                'razao_social': serializer.validated_data.get('razao_social'),
                'cnpj': serializer.validated_data.get('cnpj'),
                'nome_fantasia': serializer.validated_data.get('nome_fantasia'),
                'ramo_atividade': serializer.validated_data.get('ramo_atividade'),
                'numero_funcionarios': serializer.validated_data.get('numero_funcionarios'),
                'telefone': serializer.validated_data.get('telefone'),
                'email': serializer.validated_data.get('email'),
                'site': serializer.validated_data.get('site'),
                'descricao': serializer.validated_data.get('descricao'),
            }

            empresa = Empresa(**empresa_data)
            empresa.usuario = user
            empresa.endereco = endereco
            empresa.save()


class CandidaturaViews(AbstractViewSet):
    serializer_class = CandidaturaSerializer
    queryset = Candidatura.objects.all()


class ObjetivoProfissionalViews(AbstractViewSet):
    serializer_class = ObjetivoProfissionalSerializer
    queryset = ObjetivoProfissional.objects.all()


class IdiomaViews(AbstractViewSet):
    serializer_class = IdiomaSerializer
    queryset = Idioma.objects.all()


class CursoEspecializacaoViews(AbstractViewSet):
    serializer_class = CursoEspecializacaoSerializer
    queryset = CursoEspecializacao.objects.all()


class FormacaoAcademicaViews(AbstractViewSet):
    serializer_class = FormacaoAcademicaSerializer
    queryset = FormacaoAcademica.objects.all()


class ExperienciaProfissionalViews(AbstractViewSet):
    serializer_class = ExperienciaProfissionalSerializer
    queryset = ExperienciaProfissional.objects.all()


class EnderecoViews(AbstractViewSet):
    serializer_class = EnderecoSerializer
    queryset = Endereco.objects.all()


class VagaViews(AbstractViewSet):
    serializer_class = VagaSerializer
    queryset = Vaga.objects.all()
