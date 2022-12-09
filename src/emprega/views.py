from rest_framework import viewsets

from emprega.models import Empresa, User
from emprega.serializers import UsuarioSerializer, EmpresaSerializer


# Create your views here
class UsuarioViews(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()
    # permission_classes = [UsuarioPermission | IsAdminUser]


class EmpresaViews(viewsets.ModelViewSet):
    # permission_classes = [IsAdminUser | ReadOnly]
    serializer_class = EmpresaSerializer
    queryset = Empresa.objects.all()
