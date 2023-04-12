import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from knox import views as knox_views
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from core.views import LoginView
from emprega import urls as emprega_urls
from emprega.views import EmailVerificationView, ResetPasswordView

router = routers.DefaultRouter()

router.registry.extend(emprega_urls.router.registry)

urlpatterns = [
    path(r"login/", LoginView.as_view(), name="knox_login"),
    path(r"logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(r"logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path(r"verificar-email/", EmailVerificationView.as_view(), name="email_confirmation"),
    path(r"recuperar-senha/", ResetPasswordView.as_view(), name="password_reset"),
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path(
        "docs/",
        include_docs_urls(
            title="Emprega Anápolis API", public=os.getenv("DJANGO_DEBUG", False)
        ),
    ),
    # path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
