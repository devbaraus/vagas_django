import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory
from factory import fuzzy, faker

from emprega.models import (
    User,
    Empresa,
    Endereco,
    SexoChoices,
    EstadoCivilChoices,
    TipoDeficienciaChoices,
    ObjetivoProfissional,
    ModeloTrabalhoChoices,
    RegimeContratualChoices,
    Vaga,
)

import random


def generate_cpf():
    cpf = [random.randrange(10) for _ in range(9)]

    for _ in range(2):
        value = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(11 - value if value > 1 else 0)

    return "".join(str(x) for x in cpf)


def generate_cnpj():
    cnpj = [random.randrange(10) for _ in range(8)] + [0, 0, 0, 1]

    for _ in range(2):
        value = sum(v * (i % 8 + 2) for i, v in enumerate(reversed(cnpj)))
        digit = 11 - value % 11
        cnpj.append(digit if digit < 10 else 0)

    return "".join(str(x) for x in cnpj)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    nome = factory.Faker("name")
    cpf = factory.lazy_attribute(lambda n: generate_cpf())
    data_nascimento = factory.Faker("date_of_birth", minimum_age=18, maximum_age=65)
    sexo = factory.lazy_attribute(lambda _: random.choice(SexoChoices.choices)[0])
    estado_civil = factory.lazy_attribute(
        lambda _: random.choice(EstadoCivilChoices.choices)[0]
    )

    tipo_deficiencia = factory.lazy_attribute(
        lambda _: random.choice(TipoDeficienciaChoices.choices)[0]
    )

    area_atuacao = factory.Faker("job")
    cargo = factory.Faker("job")

    email = factory.Faker("email")
    telefone = fuzzy.FuzzyText(length=14, chars="0123456789")

    password = factory.Sequence(lambda p: "mysuperpass%s" % p)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        kwargs["password"] = make_password(kwargs["password"])
        return super(UserFactory, cls)._create(model_class, *args, **kwargs)


class ObjetivoProfissionalFactory(DjangoModelFactory):
    class Meta:
        model = ObjetivoProfissional

    cargo = factory.Faker("job")
    salario = fuzzy.FuzzyDecimal(1000, 10000, precision=2)
    modelo_trabalho = factory.lazy_attribute(
        lambda _: random.choice(ModeloTrabalhoChoices.choices)[0]
    )
    regime_contratual = factory.lazy_attribute(
        lambda _: random.choice(RegimeContratualChoices.choices)[0]
    )
    jornada_trabalho = factory.Faker("sentence", nb_words=5)
    usuario = factory.SubFactory(UserFactory)


class EnderecoFactory(DjangoModelFactory):
    class Meta:
        model = Endereco

    cep = factory.lazy_attribute(
        lambda n: f'{fuzzy.FuzzyText(length=8, chars="0123456789").fuzz()}'
    )
    logradouro = factory.Faker("street_name")
    numero = factory.Faker("building_number")
    complemento = factory.Faker("secondary_address")
    bairro = factory.Faker("street_name")
    cidade = factory.Faker("city")
    estado = factory.Faker("state_abbr")


class EmpresaFactory(DjangoModelFactory):
    class Meta:
        model = Empresa

    cnpj = factory.lazy_attribute(lambda n: generate_cnpj())
    nome_fantasia = factory.Faker("name")
    razao_social = factory.Faker("name")
    ramo_atividade = factory.Faker("name")
    numero_funcionarios = factory.Faker("random_int", min=1, max=1000)
    telefone = fuzzy.FuzzyText(length=14, chars="0123456789")
    email = factory.Faker("email")
    site = factory.lazy_attribute(
        lambda n: f"https://www.{fuzzy.FuzzyText().fuzz()}.com.br"
    )
    descricao = factory.Faker("text")
    usuario = factory.SubFactory(UserFactory)
    endereco = factory.SubFactory(EnderecoFactory)


class VagaFactory(DjangoModelFactory):
    class Meta:
        model = Vaga

    cargo = factory.Faker("job")
    atividades = factory.Faker("text")
    requisitos = factory.Faker("text")
    pessoa_deficiencia = factory.Faker("boolean")
    salario = fuzzy.FuzzyDecimal(1000, 10000, precision=2)
    jornada_trabalho = factory.Faker("sentence", nb_words=5)
    modelo_trabalho = factory.lazy_attribute(
        lambda _: random.choice(ModeloTrabalhoChoices.choices)[0]
    )
    regime_contratual = factory.lazy_attribute(
        lambda _: random.choice(RegimeContratualChoices.choices)[0]
    )
    sexo = factory.lazy_attribute(lambda _: random.choice(SexoChoices.choices)[0])
    idade_minima = factory.Faker("random_int", min=18, max=65)
    idade_maxima = factory.Faker("random_int", min=18, max=65)
    quantidade_vagas = factory.Faker("random_int", min=1, max=10)
    beneficios = factory.Faker("text")
    empresa = factory.SubFactory(EmpresaFactory)
