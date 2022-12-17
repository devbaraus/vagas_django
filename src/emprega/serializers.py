from rest_framework import serializers

from emprega.models import (
    Empresa,
    Vaga,
    ObjetivoProfissional,
    FormacaoAcademica,
    ExperienciaProfissional,
    Idioma,
    CursoEspecializacao,
    Candidatura,
    Endereco,
    Empregador,
    Candidato,
    User,
    ModeloTrabalhoChoices,
    RegimeContratualChoices,
)


class UserSerializer(serializers.ModelSerializer):
    empresas = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class EmpregadorSerializer(UserSerializer):
    class Meta:
        model = Empregador
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "is_superuser": {"read_only": True},
        }


class EmpregadorCreateSerializer(UserSerializer):
    # EMPRESA
    cnpj = serializers.CharField(max_length=14, min_length=14, required=True, write_only=True)
    nome_fantasia = serializers.CharField(max_length=255, required=True, write_only=True)
    razao_social = serializers.CharField(max_length=255, required=True, write_only=True)
    ramo_atividade = serializers.CharField(max_length=255, required=True, write_only=True)
    numero_funcionarios = serializers.IntegerField(required=False, write_only=True)
    empresa_telefone = serializers.CharField(max_length=14, required=False, write_only=True)
    empresa_email = serializers.EmailField(required=True, write_only=True)
    site = serializers.URLField(required=False, write_only=True)
    descricao = serializers.CharField(required=False, write_only=True)

    # ENDERECO
    cep = serializers.CharField(max_length=8, min_length=8, required=False, write_only=True)
    logradouro = serializers.CharField(max_length=255, required=False, write_only=True)
    numero = serializers.CharField(max_length=255, required=False, write_only=True)
    complemento = serializers.CharField(max_length=255, required=False, write_only=True)
    bairro = serializers.CharField(max_length=255, required=False, write_only=True)
    cidade = serializers.CharField(max_length=255, required=False, write_only=True)
    estado = serializers.CharField(max_length=2, min_length=2, required=False, write_only=True)

    class Meta:
        model = Empregador
        fields = "__all__"
        extra_kwargs = {
            "last_login": {"read_only": True},
            "is_superuser": {"read_only": True},
            "nivel_usuario": {"read_only": True},
            "groups": {"read_only": True},
            "user_permissions": {"read_only": True},
            "habilitado": {"read_only": True},
            "foto": {"read_only": True},
            "tipo_deficiencia": {"read_only": True},
        }


class EmpregadorListSerializer(UserSerializer):
    class Meta:
        model = Empregador
        fields = ["id", "nome"]


class CandidatoSerializer(UserSerializer):
    class Meta:
        model = Candidato
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class CandidatoListSerializer(UserSerializer):
    class Meta:
        model = Candidato
        fields = ["id", "nome"]


class CandidatoCreateSerializer(UserSerializer):
    # OBJETIVO PROFISSIONAL
    cargo = serializers.CharField(max_length=255, required=False)
    salario = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    modelo_trabalho = serializers.ChoiceField(
        choices=ModeloTrabalhoChoices.choices, required=False
    )
    regime_contratual = serializers.ChoiceField(
        choices=RegimeContratualChoices.choices, required=False
    )
    jornada_trabalho = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Candidato
        fields = "__all__"
        extra_kwargs = {
            "last_login": {"read_only": True},
            "is_superuser": {"read_only": True},
            "nivel_usuario": {"read_only": True},
            "groups": {"read_only": True},
            "user_permissions": {"read_only": True},
            "habilitado": {"read_only": True},
            "foto": {"read_only": True},
            "area_atuacao": {"read_only": True},
            "cargo": {"write_only": True},
            "salario": {"write_only": True},
            "modelo_trabalho": {"write_only": True},
            "regime_contratual": {"write_only": True},
            "jornada_trabalho": {"write_only": True},
        }


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = "__all__"


class EmpresaCreateSerializer(serializers.ModelSerializer):
    cep = serializers.CharField(
        max_length=8, min_length=8, required=False, write_only=True
    )
    logradouro = serializers.CharField(max_length=255, required=False, write_only=True)
    numero = serializers.CharField(max_length=255, required=False, write_only=True)
    complemento = serializers.CharField(max_length=255, required=False, write_only=True)
    bairro = serializers.CharField(max_length=255, required=False, write_only=True)
    cidade = serializers.CharField(max_length=255, required=False, write_only=True)
    estado = serializers.CharField(
        max_length=2, min_length=2, required=False, write_only=True
    )

    class Meta:
        model = Empresa
        fields = "__all__"
        extra_kwargs = {
            "endereco": {"read_only": True},
        }


class VagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaga
        fields = "__all__"


class ObjetivoProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoProfissional
        fields = "__all__"


class FormacaoAcademicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormacaoAcademica
        fields = "__all__"


class ExperienciaProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienciaProfissional
        fields = "__all__"


class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = "__all__"


class CursoEspecializacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoEspecializacao
        fields = "__all__"


class CandidaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = "__all__"
