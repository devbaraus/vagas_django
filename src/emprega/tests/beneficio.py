from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    BeneficioFactory,
)
from emprega.models import UsuarioNivelChoices, Beneficio


class AdminBeneficioTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/beneficio/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        data = BeneficioFactory.stub().__dict__

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["nome"], data["nome"])

    def test_retrieve(self):
        BeneficioFactory.create_batch(2)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response['results']), 2)

    def test_detail(self):
        beneficio = BeneficioFactory()

        response = self.client.get(f"{self.uri}{beneficio.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["nome"], beneficio.nome)

    def test_update(self):
        beneficio = BeneficioFactory()

        data = {"nome": "Super Beneficio"}

        response = self.client.patch(f"{self.uri}{beneficio.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["nome"], data["nome"])

    def test_delete(self):
        beneficio = BeneficioFactory()

        response = self.client.delete(f"{self.uri}{beneficio.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Beneficio.objects.count(), 0)


class EmpregadorBeneficioTestCase(AdminBeneficioTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/beneficio/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403

        self.client.force_authenticate(user=self.user)


class CandidatoBeneficioTestCase(AdminBeneficioTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/beneficio/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403

        self.client.force_authenticate(user=self.user)


class GuestBeneficioTestCase(AdminBeneficioTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/beneficio/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
