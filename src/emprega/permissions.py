from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from emprega.models import UsuarioNivelChoices, Vaga, Endereco


class OwnedByPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if bool(request.user) and not request.user.is_anonymous:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True

        if hasattr(obj, "usuario") and obj.usuario == request.user:
            return True

        if isinstance(obj, Vaga) and obj.empresa.usuario == request.user:
            return True

        if (
            isinstance(obj, Endereco)
            and request.user.empresas_usuario.filter(endereco=obj).exists()
        ):
            return True

        return False


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user) or request.user.is_anonymous:
            return False

        if request.user.nivel_usuario <= UsuarioNivelChoices.ADMIN:
            return True

        if request.user.is_superuser:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not bool(request.user):
            return False

        if request.user.nivel_usuario <= UsuarioNivelChoices.ADMIN:
            return True

        return False


class IsEmpregadorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user) or request.user.is_anonymous:
            return False

        if request.user.nivel_usuario == UsuarioNivelChoices.EMPREGADOR:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not bool(request.user) or request.user.is_anonymous:
            return False

        if request.user.nivel_usuario == UsuarioNivelChoices.EMPREGADOR:
            return True

        return False


class IsCandidatoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user) or request.user.is_anonymous:
            return False

        if request.user.nivel_usuario == UsuarioNivelChoices.CANDIDATO:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not bool(request.user) or request.user.is_anonymous:
            return False

        if (
            request.user.nivel_usuario == UsuarioNivelChoices.CANDIDATO
            and obj.usuario == request.user
        ):
            return True

        return False


class CreatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return False


class UpdatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "PUT":
            return True
        return False


class DeletePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return True
        return False


class DetailPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET" and view.action == "retrieve":
            return True
        return False


class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return False
