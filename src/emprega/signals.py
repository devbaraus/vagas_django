from django.db.models.signals import post_save
from django.dispatch import receiver

from emprega.models import Vaga, Candidatura


@receiver(post_save, sender=Vaga)
def vaga_post_save(sender, instance, created, **kwargs):
    if not created and not instance.esta_ativo:
        Candidatura.objects.filter(vaga=instance).update(esta_ativo=False)

    return None
