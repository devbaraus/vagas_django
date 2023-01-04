from auditlog.models import LogEntry
from django.db import transaction
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
    Usuario,
    ModeloTrabalhoChoices,
    RegimeContratualChoices,
    Avaliacao,
    UsuarioNivelChoices,
    Beneficio,
)


class UsuarioSerializer(serializers.ModelSerializer):
    empresas = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class EmpregadorSerializer(UsuarioSerializer):
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Empregador
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "is_superuser": {"read_only": True},
        }

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        return super().update(instance, validated_data)


class EmpregadorCreateSerializer(UsuarioSerializer):
    # EMPRESA
    cnpj = serializers.CharField(
        max_length=14, min_length=14, required=True, write_only=True
    )
    nome_fantasia = serializers.CharField(
        max_length=255, required=True, write_only=True
    )
    razao_social = serializers.CharField(max_length=255, required=True, write_only=True)
    ramo_atividade = serializers.CharField(
        max_length=255, required=True, write_only=True
    )
    numero_funcionarios = serializers.IntegerField(required=False, write_only=True)
    empresa_telefone = serializers.CharField(
        max_length=14, required=False, write_only=True
    )
    empresa_email = serializers.EmailField(required=True, write_only=True)
    site = serializers.URLField(required=False, write_only=True)
    descricao = serializers.CharField(required=False, write_only=True)

    # ENDERECO
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

    def create(self, validated_data):
        with transaction.atomic():
            user_data = {
                "nome": validated_data.get("nome"),
                "cpf": validated_data.get("cpf"),
                "data_nascimento": validated_data.get("data_nascimento"),
                "sexo": validated_data.get("sexo"),
                "estado_civil": validated_data.get("estado_civil"),
                "atuacao": validated_data.get("atuacao"),
                "cargo": validated_data.get("cargo"),
                "email": validated_data.get("email"),
                "telefone": validated_data.get("telefone"),
                "foto": validated_data.get("foto"),
                "curriculo": validated_data.get("curriculo"),
                "nivel_usuario": UsuarioNivelChoices.EMPREGADOR,
            }

            user = Empregador(**user_data)
            user.set_password(validated_data.get("password"))
            user.save()

            endereco_data = {
                "cep": validated_data.get("cep"),
                "logradouro": validated_data.get("logradouro"),
                "numero": validated_data.get("numero"),
                "complemento": validated_data.get("complemento"),
                "bairro": validated_data.get("bairro"),
                "cidade": validated_data.get("cidade"),
                "estado": validated_data.get("estado"),
            }

            endereco = Endereco(**endereco_data)
            endereco.save()

            empresa_data = {
                "razao_social": validated_data.get("razao_social"),
                "cnpj": validated_data.get("cnpj"),
                "nome_fantasia": validated_data.get("nome_fantasia"),
                "ramo_atividade": validated_data.get("ramo_atividade"),
                "numero_funcionarios": validated_data.get("numero_funcionarios"),
                "telefone": validated_data.get("telefone"),
                "email": validated_data.get("email"),
                "site": validated_data.get("site"),
                "descricao": validated_data.get("descricao"),
            }

            empresa = Empresa(**empresa_data)
            empresa.usuario = user
            empresa.endereco = endereco
            empresa.save()

            return user


class EmpregadorListSerializer(UsuarioSerializer):
    class Meta:
        model = Empregador
        fields = ["id", "nome"]


class CandidatoSerializer(UsuarioSerializer):
    class Meta:
        model = Candidato
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },
            "is_superuser": {"read_only": True},
        }

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        return super().update(instance, validated_data)


class CandidatoListSerializer(UsuarioSerializer):
    class Meta:
        model = Candidato
        fields = ["id", "nome"]


class CandidatoCreateSerializer(UsuarioSerializer):
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
            "atuacao": {"read_only": True},
            "cargo": {"write_only": True},
            "salario": {"write_only": True},
            "modelo_trabalho": {"write_only": True},
            "regime_contratual": {"write_only": True},
            "jornada_trabalho": {"write_only": True},
        }

    def create(self, validated_data):
        with transaction.atomic():
            user_data = {
                "nome": validated_data.get("nome"),
                "cpf": validated_data.get("cpf"),
                "data_nascimento": validated_data.get("data_nascimento"),
                "sexo": validated_data.get("sexo"),
                "estado_civil": validated_data.get("estado_civil"),
                "tipo_deficiencia": validated_data.get("tipo_deficiencia"),
                "email": validated_data.get("email"),
                "telefone": validated_data.get("telefone"),
                # 'foto': validated_data.get('foto'),
                # 'curriculo': validated_data.get('curriculo'),
                "nivel_usuario": UsuarioNivelChoices.CANDIDATO,
            }

            user = Candidato(**user_data)
            user.set_password(validated_data.get("password"))
            user.save()

            objetivo_profissional_data = {
                "cargo": validated_data.get("cargo"),
                "salario": validated_data.get("salario"),
                "modelo_trabalho": validated_data.get("modelo_trabalho"),
                "jornada_trabalho": validated_data.get("jornada_trabalho"),
                "regime_contratual": validated_data.get("regime_contratual"),
            }

            objetivo_profissional = ObjetivoProfissional(**objetivo_profissional_data)
            objetivo_profissional.usuario = user
            objetivo_profissional.save()

            return user


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


class BeneficioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficio
        fields = "__all__"


class EmpresaVagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ["id", "nome_fantasia", "razao_social", "cnpj"]


class VagaHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = "__all__"


class VagaSerializer(serializers.ModelSerializer):
    beneficios = BeneficioSerializer(many=True, read_only=True)
    empresa = EmpresaVagaSerializer(read_only=True)
    history = serializers.SerializerMethodField()

    class Meta:
        model = Vaga
        fields = "__all__"
        extra_kwargs = {
            "empresa": {
                "required": False,
            },
        }

    def get_history(self, obj):
        return VagaHistoricoSerializer(obj.history.all(), many=True).data


class VagaCreateSerializer(serializers.ModelSerializer):
    beneficios = serializers.ListSerializer(
        "beneficios", child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Vaga
        fields = "__all__"
        extra_kwargs = {
            "empresa": {
                "required": False,
            },
        }

    def create(self, validated_data):
        with transaction.atomic():
            beneficios = validated_data.pop("beneficios", [])
            vaga = Vaga.objects.create(**validated_data)
            for beneficio in beneficios:
                vaga.beneficios.add(beneficio)
            return vaga

    def update(self, instance, validated_data):
        with transaction.atomic():
            beneficios = validated_data.pop("beneficios", [])
            instance = super().update(instance, validated_data)
            instance.beneficios.clear()
            for beneficio in beneficios:
                instance.beneficios.add(beneficio)
            return instance


class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = "__all__"


class ObjetivoProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoProfissional
        fields = "__all__"
        extra_kwargs = {
            "usuario": {"required": False},
        }


class FormacaoAcademicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormacaoAcademica
        fields = "__all__"
        extra_kwargs = {
            "usuario": {"required": False},
        }


class ExperienciaProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienciaProfissional
        fields = "__all__"
        extra_kwargs = {
            "usuario": {"required": False},
        }


class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = "__all__"
        extra_kwargs = {
            "usuario": {"required": False},
        }


class CursoEspecializacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoEspecializacao
        fields = "__all__"
        extra_kwargs = {
            "usuario": {"required": False},
        }


class CandidaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidatura
        fields = "__all__"


class CandidatoPerfilSerializer(UsuarioSerializer):
    objetivo_profissional = serializers.SerializerMethodField()
    formacao_academica = serializers.SerializerMethodField()
    experiencia_profissional = serializers.SerializerMethodField()
    idioma = serializers.SerializerMethodField()
    curso_especializacao = serializers.SerializerMethodField()

    class Meta:
        model = Candidato
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def get_objetivo_profissional(self, obj):
        item = ObjetivoProfissional.objects.filter(usuario=obj).first()
        return ObjetivoProfissionalSerializer(item).data

    def get_formacao_academica(self, obj):
        items = FormacaoAcademica.objects.filter(usuario=obj)
        return FormacaoAcademicaSerializer(items, many=True).data

    def get_experiencia_profissional(self, obj):
        items = ExperienciaProfissional.objects.filter(usuario=obj)
        return ExperienciaProfissionalSerializer(items, many=True).data

    def get_idioma(self, obj):
        items = Idioma.objects.filter(usuario=obj)
        return IdiomaSerializer(items, many=True).data

    def get_curso_especializacao(self, obj):
        items = CursoEspecializacao.objects.filter(usuario=obj)
        return CursoEspecializacaoSerializer(items, many=True).data


class EmpregadorPerfilSerializer(UsuarioSerializer):
    empresa = serializers.SerializerMethodField()
    endereco = serializers.SerializerMethodField()

    class Meta:
        model = Empregador
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def get_empresa(self, obj):
        item = Empresa.objects.filter(usuario=obj).first()
        return EmpresaSerializer(item).data

    def get_endereco(self, obj):
        item = Endereco.objects.filter(empresa_endereco__usuario=obj).first()
        return EnderecoSerializer(item).data
