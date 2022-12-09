from rest_framework.routers import DefaultRouter

from emprega.views import UsuarioViews, EmpresaViews

app_name = 'emprega_api'

router = DefaultRouter()

router.register('usuario', UsuarioViews, basename='usuario')
router.register('empresa', EmpresaViews, basename='empresa')

urlpatterns = router.urls
