import json
import os
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _
from faker import Faker
from faker.providers.address.pt_BR import Provider as address
from faker.providers.company.pt_BR import Provider as company
from faker.providers.internet.pt_BR import Provider as internet
from faker.providers.job.pt_BR import Provider as job
from faker.providers.person.pt_BR import Provider as person
from faker.providers.phone_number.pt_BR import Provider as phone_number
from faker.providers.ssn.pt_BR import Provider as ssn

from emprega.serializers import EmpregadorCreateInternalSerializer, VagaCreateInternalSerializer

fake = Faker(
    locales=['pt_BR'],
)
fake.add_provider(job)
fake.add_provider(phone_number)
fake.add_provider(ssn)
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(address)
fake.add_provider(company)

from emprega.models import UsuarioNivelChoices, SexoChoices, EstadoCivilChoices, JornadaTrabalhoChoices, Beneficio, \
    RegimeContratualChoices, ModeloTrabalhoChoices

FAKE_PASSWORD = os.getenv('FAKE_PASSWORD', '123456')


class Command(BaseCommand):
    help = _('Creates a new employer')

    def add_arguments(self, parser):
        parser.add_argument('number', type=int, help=_('The number of users to create'))
        parser.add_argument('--vagas', type=str, help=_('The number of jobs to create'))
        parser.add_argument("--vagas_input", type=str, help=_("The path to the file with the jobs to create"))

    def _gerar_vaga(self, **kwargs):
        beneficios = Beneficio.objects.all().values('id')
        beneficios = [beneficio['id'] for beneficio in beneficios]
        beneficios = random.sample(list(beneficios), random.randint(1, len(beneficios)))

        return {
            "cargo": fake.job(),
            "atividades": fake.text(),
            "requisitos": fake.text(),
            "pessoa_deficiente": random.choice([True, False]),
            "salario": fake.pyfloat(left_digits=4, right_digits=2, positive=True),
            "jornada_trabalho": random.choice(JornadaTrabalhoChoices.values),
            "regime_contratual": random.choice(RegimeContratualChoices.values),
            "modelo_trabalho": random.choice(ModeloTrabalhoChoices.values),
            "sexo": random.choice(SexoChoices.values),
            "idade_minima": fake.pyint(min_value=18, max_value=60),
            "idade_maxima": fake.pyint(min_value=18, max_value=60),
            "beneficios": beneficios,
            "quantidade_vagas": fake.pyint(min_value=1, max_value=100),
            **kwargs,
        }

    def _get_random_user(self):
        fake_email = f'{fake.user_name()}@tuamaeaquelaursa.com'

        return {
            "nome": fake.name(),
            "data_nascimento": fake.date_of_birth(),
            "cpf": fake.cpf().replace('.', '').replace('-', ''),
            "sexo": random.choice(SexoChoices.values),
            "estado_civil": random.choice(EstadoCivilChoices.values),
            "area_atuacao": fake.job(),
            "cargo": fake.job(),

            "email": fake_email,
            "telefone": fake.phone_number().replace(' ', '').replace('-', '').replace('(', '').replace(')', ''),
            "password": FAKE_PASSWORD,

            "nivel_usuario": UsuarioNivelChoices.EMPREGADOR,

            "cnpj": fake.cnpj().replace('.', '').replace('-', '').replace('/', ''),
            "razao_social": fake.company(),
            "nome_fantasia": fake.company(),
            "ramo_atividade": fake.job(),
            "numero_funcionarios": fake.pyint(min_value=1, max_value=1000),
            "empresa_telefone": fake.phone_number().replace(' ', '').replace('-', '').replace('(', '').replace(')', ''),
            "empresa_email": fake.email(),
            "site": fake.url(),
            "descricao": fake.text(),

            "cep": fake.postcode().replace('-', ''),
            "logradouro": fake.street_name(),
            "numero": fake.building_number(),
            "complemento": fake.secondary_address(),
            "bairro": fake.bairro(),
            "cidade": fake.city(),
            "estado": fake.estado_sigla(),
        }

    def handle(self, *args, **options):
        number_users = options['number'] or 1
        number_jobs = options['vagas'] or '0'
        i_vagas = options['vagas_input']
        l_vagas = []

        # Check if input is a json file
        if i_vagas:
            if not i_vagas.endswith('.json'):
                raise ValueError('Input file must be a json file')
            with open(i_vagas, 'r') as f:
                vagas = json.load(f)
                vagas_in = vagas

        if '~' in number_jobs:
            number_jobs = number_jobs.split('~')
            number_jobs = random.randint(int(number_jobs[0]), int(number_jobs[1]))
        else:
            number_jobs = int(number_jobs)

        for i in range(number_users):
            with transaction.atomic():
                empregador = self._get_random_user()

                empregador_serializer = EmpregadorCreateInternalSerializer(data=empregador)
                empregador_serializer.is_valid(raise_exception=True)
                empregador = empregador_serializer.save()

                for j in range(number_jobs):
                    r_vaga = {}

                    if vagas_in:
                        r_vaga = random.choice(vagas_in)

                    vaga = self._gerar_vaga(**r_vaga)
                    vaga['empresa'] = empregador.empresa.id
                    vaga_serializer = VagaCreateInternalSerializer(data=vaga)
                    vaga_serializer.is_valid(raise_exception=True)
                    vaga_serializer.save()

            self.stdout.write(self.style.SUCCESS(f'Created empregador {empregador.nome} - {empregador.cpf}'))
