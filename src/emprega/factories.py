import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory

from emprega.models import User

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

    cpf = factory.lazy_attribute(lambda n: generate_cpf())
    email = factory.Faker('email')
    nome = factory.Faker('name')
    data_nascimento = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
    password = factory.Sequence(lambda p: 'mysuperpass%s' % p)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        kwargs['password'] = make_password(kwargs['password'])
        return super(UserFactory, cls)._create(model_class, *args, **kwargs)
