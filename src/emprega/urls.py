from rest_framework.routers import DefaultRouter

from emprega.views import EmpresaViews, CandidaturaViews, ObjetivoProfissionalViews, IdiomaViews, \
    CursoEspecializacaoViews, FormacaoAcademicaViews, ExperienciaProfissionalViews, EnderecoViews, VagaViews, \
    EmpregadorViews, CandidatoViews, UserViews, AvaliacaoViews

app_name = 'emprega_api'

router = DefaultRouter()

router.register('usuario', UserViews, basename='user')
router.register('candidato', CandidatoViews, basename='candidato')
router.register('empregador', EmpregadorViews, basename='empregador')
router.register('empresa', EmpresaViews, basename='empresa')
router.register('candidatura', CandidaturaViews, basename='candidatura')
router.register('objetivo_profissional', ObjetivoProfissionalViews, basename='objetivo_profissional')
router.register('idioma', IdiomaViews, basename='idioma')
router.register('curso_especializacao', CursoEspecializacaoViews, basename='curso_especializacao')
router.register('formacao_academica', FormacaoAcademicaViews, basename='formacao_academica')
router.register('experiencia_profissional', ExperienciaProfissionalViews, basename='experiencia_profissional')
router.register('endereco', EnderecoViews, basename='endereco')
router.register('vaga', VagaViews, basename='vaga')
router.register('avaliacao', AvaliacaoViews, basename='avaliacao')

urlpatterns = router.urls
