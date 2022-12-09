from rest_framework import serializers

from emprega.models import User, Empresa, Vaga, ObjetivoProfissional, FormacaoAcademica, ExperienciaProfissional, \
    Idioma, CursoEspecializacao


class UsuarioSerializer(serializers.ModelSerializer):
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fiels = '__all__'


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


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


class IdiomassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = '__all__'


class CursoEspecializacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CursoEspecializacao
        fields = '__all__'
