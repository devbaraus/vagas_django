from rest_framework import serializers, status
from rest_framework.response import Response

from emprega.models import Empresa, Vaga, ObjetivoProfissional, FormacaoAcademica, ExperienciaProfissional, \
    Idioma, CursoEspecializacao, Candidatura, Endereco, Empregador, Candidato, User
from emprega.validators import validate_cnpj


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
            },
            'is_superuser': {
                'read_only': True
            }
        }


class EmpregadorCreateSerializer(UserSerializer):
    # EMPRESA
    cnpj = serializers.CharField(max_length=14, min_length=14, required=True)
    nome_fantasia = serializers.CharField(max_length=255, required=True)
    razao_social = serializers.CharField(max_length=255, required=True)
    ramo_atividade = serializers.CharField(max_length=255, required=True)
    numero_funcionarios = serializers.IntegerField(required=False)
    empresa_telefone = serializers.CharField(max_length=14, required=False)
    empresa_email = serializers.EmailField(required=True)
    site = serializers.URLField(required=False)
    descricao = serializers.CharField(required=False)

    # ENDERECO
    cep = serializers.CharField(max_length=8, min_length=8, required=False)
    logradouro = serializers.CharField(max_length=255, required=False)
    numero = serializers.CharField(max_length=255, required=False)
    complemento = serializers.CharField(max_length=255, required=False)
    bairro = serializers.CharField(max_length=255, required=False)
    cidade = serializers.CharField(max_length=255, required=False)
    estado = serializers.CharField(max_length=2, min_length=2, required=False)

    class Meta:
        model = Empregador
        fields = '__all__'
        extra_kwargs = {
            'last_login': {
                'read_only': True
            },
            'is_superuser': {
                'read_only': True
            },
            'nivel_usuario': {
                'read_only': True
            },
            'groups': {
                'read_only': True
            },
            'user_permissions': {
                'read_only': True
            },
            'habilitado': {
                'read_only': True
            },
            'foto': {
                'read_only': True
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
