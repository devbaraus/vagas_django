from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from emprega.models import Empresa, Candidatura, ObjetivoProfissional, Idioma, CursoEspecializacao, \
    FormacaoAcademica, ExperienciaProfissional, Endereco, Vaga, Candidato, Empregador, User
from emprega.permissions import AdminPermission, OwnedByPermission, CreatePermission
from emprega.serializers import EmpresaSerializer, CandidaturaSerializer, \
    ObjetivoProfissionalSerializer, IdiomaSerializer, CursoEspecializacaoSerializer, FormacaoAcademicaSerializer, \
    ExperienciaProfissionalSerializer, EnderecoSerializer, VagaSerializer, CandidatoSerializer, EmpregadorSerializer, \
    UserSerializer, CandidatoListSerializer, EmpregadorListSerializer


class AbstractViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission, OwnedByPermission]


class UserViews(AbstractViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, AdminPermission]


class CandidatoViews(AbstractViewSet):
    serializers = {'default': CandidatoSerializer, 'list': CandidatoListSerializer}
    queryset = Candidato.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission | CreatePermission | OwnedByPermission]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])


class EmpregadorViews(AbstractViewSet):
    serializers = {'default': EmpregadorSerializer, 'list': EmpregadorListSerializer}
    queryset = Empregador.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, AdminPermission | CreatePermission | OwnedByPermission]

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmpresaViews(AbstractViewSet):
    serializer_class = EmpresaSerializer
    queryset = Empresa.objects.all()
    filterset_fields = ['usuario']


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
