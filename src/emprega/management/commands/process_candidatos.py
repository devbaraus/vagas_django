from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from emprega.models import Candidato
from recomendacao.tasks import process_candidato
from time import sleep


class Command(BaseCommand):
    help = _('Processes all users profiles')

    def add_arguments(self, parser):
        parser.add_argument('--delay', type=int, help=_('Delay between each processing'))

    def handle(self, *args, **options):
        delay = options['delay']
        candidatos = Candidato.objects.all()
    
        for candidato in candidatos:
            process_candidato.delay(pk = candidato.pk)
            sleep(delay)
