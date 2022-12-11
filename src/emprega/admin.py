from django.contrib import admin

from emprega.models import Empresa, Candidatura, ObjetivoProfissional, Idioma, CursoEspecializacao, FormacaoAcademica, \
    ExperienciaProfissional, Endereco, Vaga, Candidato, Empregador, User

# Register your models here.

admin.site.register(User)
admin.site.register(Candidato)
admin.site.register(Empregador)
admin.site.register(Empresa)
admin.site.register(Vaga)
admin.site.register(Candidatura)
admin.site.register(ObjetivoProfissional)
admin.site.register(Idioma)
admin.site.register(CursoEspecializacao)
admin.site.register(FormacaoAcademica)
admin.site.register(ExperienciaProfissional)
admin.site.register(Endereco)
