# Generated by Django 4.1.4 on 2023-03-10 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emprega', '0002_remove_usuario_habilitado_remove_vaga_habilitado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='curriculo_processado',
            field=models.TextField(blank=True, null=True, verbose_name='Currículo Processado'),
        ),
    ]
