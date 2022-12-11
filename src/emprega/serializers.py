from rest_framework import serializers, status
from rest_framework.response import Response

from emprega.models import Empresa, Vaga, ObjetivoProfissional, FormacaoAcademica, ExperienciaProfissional, \
    Idioma, CursoEspecializacao, Candidatura, Endereco, Empregador, Candidato, User


class UserSerializer(serializers.ModelSerializer):
    empresas = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class EmpregadorSerializer(UserSerializer):
    class Meta:
        model = Empregador
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class EmpregadorListSerializer(UserSerializer):
    class Meta:
        model = Empregador
        fields = ['id', 'nome']


class CandidatoSerializer(UserSerializer):
    class Meta:
        model = Candidato
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class CandidatoListSerializer(UserSerializer):
    class Meta:
        model = Candidato
        fields = ['id', 'nome']


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

    def create(self, validated_data):
        empregador = Empregador.objects.get(pk=validated_data['usuario'])
        empresa = Empresa.objects.create(**validated_data)
        empregador.empresa = empresa
        empregador.save()
        return empresa


class VagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaga
        fields = '__all__'


class ObjetivoProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoProfissional
        fields = '__all__'


class FormacaoAcademicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormacaoAcademica
        fields = '__all__'


class ExperienciaProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienciaProfissional
        fields = '__all__'


class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = '__all__'


class CursoEspecializacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoEspecializacao
        fields = '__all__'


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'


class CandidaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = '__all__'
