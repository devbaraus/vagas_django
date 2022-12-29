from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
)
from emprega.models import UsuarioNivelChoices, Usuario, Empregador


class AdminUserTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/usuario/"
        self.create_status = None
        self.update_status = None
        self.retrieve_status = None
        self.detail_status = None
        self.delete_status = None
        self.self_detail_status = None
        self.self_update_status = None
        self.self_delete_status = None

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        data = {
            "cpf": "72996592042",
            "email": "teste@teste.com",
            "nome": "Teste",
            "data_nascimento": "1990-01-01",
            "password": "123456",
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["cpf"], data["cpf"])
        self.assertEqual(json_response["email"], data["email"])
        self.assertEqual(json_response["nome"], data["nome"])
        self.assertEqual(json_response["data_nascimento"], data["data_nascimento"])

    def test_retrieve(self):
        UserFactory.create_batch(2)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        # 3 users: 1 created in setUp and 2 created in test_retrieve
        self.assertEqual(len(json_response), 3)

    def test_detail(self):
        user = UserFactory()

        response = self.client.get(f"{self.uri}{user.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cpf"], user.cpf)
        self.assertEqual(json_response["email"], user.email)
        self.assertEqual(json_response["nome"], user.nome)
        self.assertEqual(
            json_response["data_nascimento"], user.data_nascimento.strftime("%Y-%m-%d")
        )

    def test_update(self):
        user = UserFactory()

        data = {"email": "example@example.com"}

        response = self.client.patch(f"{self.uri}{user.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["email"], data["email"])

    def test_delete(self):
        user = UserFactory()

        response = self.client.delete(f"{self.uri}{user.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Usuario.objects.count(), 1)

    def test_self_detail(self):
        if not self.user:
            self.user = UserFactory()

        response = self.client.get(f"{self.uri}{self.user.id}/")

        self.assertEqual(
            response.status_code, self.self_detail_status or status.HTTP_200_OK
        )

        if self.self_detail_status and self.self_detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cpf"], self.user.cpf)
        self.assertEqual(json_response["email"], self.user.email)
        self.assertEqual(json_response["nome"], self.user.nome)
        self.assertEqual(
            json_response["data_nascimento"],
            self.user.data_nascimento.strftime("%Y-%m-%d"),
        )

    def test_self_update(self):
        if not self.user:
            self.user = UserFactory()

        data = {"email": "teste@teste.com"}

        response = self.client.patch(f"{self.uri}{self.user.id}/", data=data)

        self.assertEqual(
            response.status_code, self.self_update_status or status.HTTP_200_OK
        )

        if self.self_update_status and self.self_update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["email"], data["email"])

    def test_self_delete(self):
        if not self.user:
            self.user = UserFactory()

        response = self.client.delete(f"{self.uri}{self.user.id}/")

        self.assertEqual(
            response.status_code, self.self_delete_status or status.HTTP_204_NO_CONTENT
        )

        if (
            self.self_delete_status
            and self.self_delete_status != status.HTTP_204_NO_CONTENT
        ):
            return

        self.assertEqual(Empregador.objects.count(), 0)


class EmpregadorUserTestCase(AdminUserTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/usuario/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 403
        self.detail_status = 403
        self.delete_status = 403
        self.self_detail_status = 403
        self.self_update_status = 403
        self.self_delete_status = 403

        self.client.force_authenticate(user=self.user)


class CandidatoUserTestCase(AdminUserTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/usuario/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 403
        self.detail_status = 403
        self.delete_status = 403
        self.self_detail_status = 403
        self.self_update_status = 403
        self.self_delete_status = 403

        self.client.force_authenticate(user=self.user)


class GuestUserTestCase(AdminUserTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/usuario/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
        self.self_detail_status = 401
        self.self_update_status = 401
        self.self_delete_status = 401
