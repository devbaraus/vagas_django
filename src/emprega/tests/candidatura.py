from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    EmpresaFactory,
    VagaFactory,
    CandidaturaFactory,
)
from emprega.models import UsuarioNivelChoices, Candidatura


class AdminCandidaturaTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)

        self.client = APIClient()
        self.uri = "/candidatura/"
        self.create_status = 201
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        empresa = EmpresaFactory(usuario=user)
        vaga = VagaFactory(empresa=empresa)

        data = {
            "usuario": self.user.id,
            "vaga": vaga.id,
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["usuario"], data["usuario"])
        self.assertEqual(json_response["vaga"], data["vaga"])

    def test_retrieve(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        empresa = EmpresaFactory(usuario=user)
        vaga1 = VagaFactory(empresa=empresa)
        vaga2 = VagaFactory(empresa=empresa)

        CandidaturaFactory(vaga=vaga1, usuario=self.user)
        CandidaturaFactory(vaga=vaga2, usuario=self.user)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 2)

    def test_detail(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        empresa = EmpresaFactory(usuario=user)
        vaga = VagaFactory(empresa=empresa)

        item = CandidaturaFactory(vaga=vaga, usuario=self.user)

        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["id"], item.id)
        self.assertEqual(json_response["vaga"], item.vaga.id)
        self.assertEqual(json_response["usuario"], item.usuario.id)

    def test_delete(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        empresa = EmpresaFactory(usuario=user)
        vaga = VagaFactory(empresa=empresa)

        item = CandidaturaFactory(vaga=vaga, usuario=self.user)

        response = self.client.delete(f"{self.uri}{item.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Candidatura.objects.count(), 0)


class EmpregadorCandidaturaTestCase(AdminCandidaturaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/candidatura/"
        self.create_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403

        self.client.force_authenticate(user=self.user)


class CandidatoCandidaturaTestCase(AdminCandidaturaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/candidatura/"
        self.create_status = 201
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_delete(self):
        super().test_delete()


class GuestCandidaturaTestCase(AdminCandidaturaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/candidatura/"
        self.create_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
