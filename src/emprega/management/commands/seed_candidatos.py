import os
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext as _
from faker import Faker
from faker.providers.internet.pt_BR import Provider as internet
from faker.providers.job.pt_BR import Provider as job
from faker.providers.person.pt_BR import Provider as person
from faker.providers.phone_number.pt_BR import Provider as phone_number
from faker.providers.ssn.pt_BR import Provider as ssn

from emprega.serializers import CandidatoCreateInternalSerializer, FormacaoAcademicaInternalSerializer, \
    ExperienciaProfissionalInternalSerializer, CursoEspecializacaoInternalSerializer, IdiomaInternalSerializer

fake = Faker(
    locales=['pt_BR'],
)
fake.add_provider(job)
fake.add_provider(phone_number)
fake.add_provider(ssn)
fake.add_provider(internet)
fake.add_provider(person)

from emprega.models import UsuarioNivelChoices, SexoChoices, EstadoCivilChoices, TipoDeficienciaChoices, \
    ModeloTrabalhoChoices, RegimeContratualChoices, JornadaTrabalhoChoices, FormacaoNivelChoices, IdiomaNivelChoices

FAKE_PASSWORD = os.getenv('FAKE_PASSWORD', '123456')


class Command(BaseCommand):
    help = _('Creates a new user')

    def add_arguments(self, parser):
        parser.add_argument('number', type=int, help=_('The number of users to create'))
        parser.add_argument('--formacao', type=str, help=_('Generate academic formation'))
        parser.add_argument('--experiencia', type=str, help=_('Generate professional experience'))
        parser.add_argument('--curso', type=str, help=_('Generate specialization course'))
        parser.add_argument('--idioma', type=str, help=_('Generate language'))

    def _gerar_formacao_academica(self, usuario_id):
        return {
            "curso": fake.job(),
            "instituicao": fake.company(),
            "nivel": random.choice(FormacaoNivelChoices.values),
            "data_inicio": fake.date_of_birth(),
            "data_conclusao": fake.date_of_birth(),
            "usuario": usuario_id
        }

    def _gerar_experiencia_profissional(self, usuario_id):
        return {
            "cargo": fake.job(),
            "empresa": fake.company(),
            "salario": fake.pyfloat(left_digits=4, right_digits=2, positive=True),
            "atividades": fake.text(),
            "data_inicio": fake.date_of_birth(),
            "data_fim": fake.date_of_birth(),
            "usuario": usuario_id
        }

    def _gerar_curso_especializacao(self, usuario_id):
        return {
            "curso": fake.job(),
            "instituicao": fake.company(),
            "duracao_horas": fake.pyint(min_value=1, max_value=4000),
            "data_conclusao": fake.date_of_birth(),
            "usuario": usuario_id
        }

    def _gerar_idioma(self, usuario_id):
        return {
            "nome": random.choice(
                ['Inglês', 'Espanhol', 'Francês', 'Alemão', 'Italiano', 'Japonês', 'Chinês', 'Russo']),
            "nivel": random.choice(IdiomaNivelChoices.values),
            "usuario": usuario_id
        }

    def _get_random_user(self):
        return {
            "nome": fake.name(),
            "data_nascimento": fake.date_of_birth(),
            "cpf": fake.cpf().replace('.', '').replace('-', ''),
            "sexo": random.choice(SexoChoices.values),
            "estado_civil": random.choice(EstadoCivilChoices.values),
            "tipo_deficiencia": random.choice([*TipoDeficienciaChoices.values, None]),

            "email": fake.email(),
            "telefone": fake.phone_number().replace(' ', '').replace('-', '').replace('(', '').replace(')', ''),
            "password": FAKE_PASSWORD,

            "nivel_usuario": UsuarioNivelChoices.CANDIDATO,

            "cargo": fake.job(),
            "salario": fake.pyfloat(left_digits=4, right_digits=2, positive=True),
            "modelo_trabalho": random.choice(ModeloTrabalhoChoices.values),
            "regime_contratual": random.choice(RegimeContratualChoices.values),
            "jornada_trabalho": random.choice(JornadaTrabalhoChoices.values),
        }

    def handle(self, *args, **options):
        number_of_candidatos = options['number'] or 1
        n_formacao = options['formacao'] or '0'
        n_curso = options['curso'] or '0'
        n_experiencia = options['experiencia'] or '0'
        n_idioma = options['idioma'] or '0'

        if '~' in n_formacao:
            n_formacao = n_formacao.split('~')
            n_formacao = random.randint(int(n_formacao[0]), int(n_formacao[1]))
        else:
            n_formacao = int(n_formacao)

        if '~' in n_curso:
            n_curso = n_curso.split('~')
            n_curso = random.randint(int(n_curso[0]), int(n_curso[1]))
        else:
            n_curso = int(n_curso)

        if '~' in n_experiencia:
            n_experiencia = n_experiencia.split('~')
            n_experiencia = random.randint(int(n_experiencia[0]), int(n_experiencia[1]))
        else:
            n_experiencia = int(n_experiencia)

        if '~' in n_idioma:
            n_idioma = n_idioma.split('~')
            n_idioma = random.randint(int(n_idioma[0]), int(n_idioma[1]))
        else:
            n_idioma = int(n_idioma)

        for i in range(number_of_candidatos):
            with transaction.atomic():
                candidato = self._get_random_user()

                candidato_serializer = CandidatoCreateInternalSerializer(data=candidato)
                candidato_serializer.is_valid(raise_exception=True)
                candidato_serializer.save()

                for _ in range(n_formacao):
                    formacao = self._gerar_formacao_academica(candidato_serializer.data['id'])
                    formacao_serializer = FormacaoAcademicaInternalSerializer(data=formacao)
                    formacao_serializer.is_valid(raise_exception=True)
                    formacao_serializer.save()

                for _ in range(n_experiencia):
                    experiencia = self._gerar_experiencia_profissional(candidato_serializer.data['id'])
                    experiencia_serializer = ExperienciaProfissionalInternalSerializer(data=experiencia)
                    experiencia_serializer.is_valid(raise_exception=True)
                    experiencia_serializer.save()

                for _ in range(n_curso):
                    curso = self._gerar_curso_especializacao(candidato_serializer.data['id'])
                    curso_serializer = CursoEspecializacaoInternalSerializer(data=curso)
                    curso_serializer.is_valid(raise_exception=True)
                    curso_serializer.save()

                for _ in range(n_idioma):
                    idioma = self._gerar_idioma(candidato_serializer.data['id'])
                    idioma_serializer = IdiomaInternalSerializer(data=idioma)
                    idioma_serializer.is_valid(raise_exception=True)
                    idioma_serializer.save()

            self.stdout.write(self.style.SUCCESS(f'Created candidato {candidato["nome"]} - {candidato["cpf"]}'))
