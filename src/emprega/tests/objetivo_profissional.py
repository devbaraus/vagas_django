from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    ObjetivoProfissionalFactory,
)
from emprega.models import UsuarioNivelChoices


class AdminObjetivoProfissionalTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/objetivo_profissional/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204
        self.detail_other_status = 200

        self.client.force_authenticate(user=self.user)

    def test_retrieve(self):
        ObjetivoProfissionalFactory.create_batch(1, usuario=self.user)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 1)

    def test_detail(self):
        item = ObjetivoProfissionalFactory(usuario=self.user)

        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cargo"], item.cargo)
        self.assertEqual(json_response["salario"], str(item.salario))
        self.assertEqual(json_response["modelo_trabalho"], item.modelo_trabalho)
        self.assertEqual(json_response["regime_contratual"], item.regime_contratual)
        self.assertEqual(json_response["jornada_trabalho"], item.jornada_trabalho)
        self.assertEqual(json_response["usuario"], self.user.id)

    def test_update(self):
        item = ObjetivoProfissionalFactory(usuario=self.user)

        item_stub = ObjetivoProfissionalFactory.stub(usuario=self.user)

        data = {
            "cargo": item_stub.cargo,
            "salario": item_stub.salario,
            "modelo_trabalho": item_stub.modelo_trabalho,
            "regime_contratual": item_stub.regime_contratual,
            "jornada_trabalho": item_stub.jornada_trabalho,
        }

        response = self.client.put(f"{self.uri}{item.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cargo"], item_stub.cargo)
        self.assertEqual(json_response["salario"], str(item_stub.salario))
        self.assertEqual(json_response["modelo_trabalho"], item_stub.modelo_trabalho)
        self.assertEqual(json_response["regime_contratual"], item_stub.regime_contratual)
        self.assertEqual(json_response["jornada_trabalho"], item_stub.jornada_trabalho)
        self.assertEqual(json_response["usuario"], self.user.id)

    def test_detail_other(self):
        item = ObjetivoProfissionalFactory()
        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(
            response.status_code, self.detail_other_status or status.HTTP_403_FORBIDDEN
        )


class EmpregadorObjetivoProfissionalTestCase(AdminObjetivoProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/objetivo_profissional/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 403
        self.detail_status = 200
        self.delete_status = 403
        self.detail_other_status = 200

        self.client.force_authenticate(user=self.user)


class CandidatoObjetivoProfissionalTestCase(AdminObjetivoProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/objetivo_profissional/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204
        self.detail_other_status = 403

        self.client.force_authenticate(user=self.user)


class GuestObjetivoProfissionalTestCase(AdminObjetivoProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/objetivo_profissional/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
        self.detail_other_status = 401
