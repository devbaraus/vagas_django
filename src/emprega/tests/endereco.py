from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    EmpresaFactory,
)
from emprega.models import UsuarioNivelChoices


class AdminEnderecoTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/endereco/"
        self.create_status = 422
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_retrieve(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        EmpresaFactory.create_batch(2, usuario=self.user)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 2)

    def test_detail(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        item = EmpresaFactory(usuario=self.user)

        endereco = item.endereco

        response = self.client.get(f"{self.uri}{endereco.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["id"], endereco.id)
        self.assertEqual(json_response["cep"], endereco.cep)
        self.assertEqual(json_response["logradouro"], endereco.logradouro)
        self.assertEqual(json_response["numero"], endereco.numero)
        self.assertEqual(json_response["complemento"], endereco.complemento)
        self.assertEqual(json_response["bairro"], endereco.bairro)
        self.assertEqual(json_response["cidade"], endereco.cidade)
        self.assertEqual(json_response["estado"], endereco.estado)

    def test_update(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        item = EmpresaFactory(usuario=self.user)

        endereco = item.endereco

        data = {
            "cep": "12345678",
            "logradouro": "Rua 1",
            "numero": "123",
            "complemento": "Casa 1",
            "bairro": "Bairro 1",
            "cidade": "Cidade 1",
            "estado": "GO",
        }

        response = self.client.put(f"{self.uri}{endereco.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["id"], endereco.id)
        self.assertEqual(json_response["cep"], data["cep"])
        self.assertEqual(json_response["logradouro"], data["logradouro"])
        self.assertEqual(json_response["numero"], data["numero"])
        self.assertEqual(json_response["complemento"], data["complemento"])
        self.assertEqual(json_response["bairro"], data["bairro"])
        self.assertEqual(json_response["cidade"], data["cidade"])
        self.assertEqual(json_response["estado"], data["estado"])


class EmpregadorEnderecoTestCase(AdminEnderecoTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/endereco/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_detail(self):
        super().test_detail()


class CandidatoEnderecoTestCase(AdminEnderecoTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/endereco/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403

        self.client.force_authenticate(user=self.user)


class GuestEnderecoTestCase(AdminEnderecoTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/endereco/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 401
