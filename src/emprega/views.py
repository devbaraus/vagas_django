from rest_framework import viewsets

from emprega.models import Empresa, User, Candidatura, ObjetivoProfissional, Idioma, CursoEspecializacao, \
    FormacaoAcademica, ExperienciaProfissional, Endereco, Vaga
from emprega.serializers import UsuarioSerializer, EmpresaSerializer, CandidaturaSerializer, \
    ObjetivoProfissionalSerializer, IdiomaSerializer, CursoEspecializacaoSerializer, FormacaoAcademicaSerializer, \
    ExperienciaProfissionalSerializer, EnderecoSerializer, VagaSerializer


# Create your views here
class UsuarioViews(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()
    # permission_classes = [UsuarioPermission | IsAdminUser]


class EmpresaViews(viewsets.ModelViewSet):
    # permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = EmpresaSerializer
    queryset = Empresa.objects.all()


class CandidaturaViews(viewsets.ModelViewSet):
    # permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = CandidaturaSerializer
    queryset = Candidatura.objects.all()


class ObjetivoProfissionalViews(viewsets.ModelViewSet):
    serializer_class = ObjetivoProfissionalSerializer
    queryset = ObjetivoProfissional.objects.all()


class IdiomaViews(viewsets.ModelViewSet):
    serializer_class = IdiomaSerializer
    queryset = Idioma.objects.all()


class CursoEspecializacaoViews(viewsets.ModelViewSet):
    serializer_class = CursoEspecializacaoSerializer
    queryset = CursoEspecializacao.objects.all()


class FormacaoAcademicaViews(viewsets.ModelViewSet):
    serializer_class = FormacaoAcademicaSerializer
    queryset = FormacaoAcademica.objects.all()


class ExperienciaProfissionalViews(viewsets.ModelViewSet):
    serializer_class = ExperienciaProfissionalSerializer
    queryset = ExperienciaProfissional.objects.all()


class EnderecoViews(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    queryset = Endereco.objects.all()


class VagaViews(viewsets.ModelViewSet):
    serializer_class = VagaSerializer
    queryset = Vaga.objects.all()
