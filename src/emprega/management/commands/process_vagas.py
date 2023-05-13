from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from emprega.models import Vaga
from recomendacao.tasks import process_vaga
from time import sleep


class Command(BaseCommand):
    help = _('Processes all vagas')

    def add_arguments(self, parser):
        parser.add_argument('--delay', type=int, help=_('Delay between each processing'))

    def handle(self, *args, **options):
        delay = options['delay']
        vagas = Vaga.objects.all()
    
        for vaga in vagas:
            process_vaga.delay(pk = vaga.pk)
            sleep(delay)
