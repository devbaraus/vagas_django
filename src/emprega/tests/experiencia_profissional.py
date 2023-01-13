from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    ExperienciaProfissionalFactory,
)
from emprega.models import (
    UsuarioNivelChoices,
    ExperienciaProfissional,
)


class AdminExperienciaProfissionalTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/experiencia_profissional/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204
        self.detail_other_status = 200

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        item = ExperienciaProfissionalFactory.stub(usuario=self.user)

        data = {
            "empresa": item.empresa,
            "cargo": item.cargo,
            "data_inicio": item.data_inicio,
            "data_fim": item.data_fim,
            "atividades": item.atividades,
            "salario": item.salario,
            "usuario": self.user.id,
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["empresa"], item.empresa)
        self.assertEqual(json_response["cargo"], item.cargo)
        self.assertEqual(json_response["data_inicio"], item.data_inicio)
        self.assertEqual(json_response["data_fim"], item.data_fim)
        self.assertEqual(json_response["atividades"], item.atividades)
        self.assertEqual(json_response["salario"], str(item.salario))
        self.assertEqual(json_response["usuario"], self.user.id)

    def test_retrieve(self):
        ExperienciaProfissionalFactory.create_batch(2, usuario=self.user)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 2)

    def test_detail(self):
        item = ExperienciaProfissionalFactory(usuario=self.user)

        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["empresa"], item.empresa)
        self.assertEqual(json_response["cargo"], item.cargo)
        self.assertEqual(json_response["data_inicio"], item.data_inicio)
        self.assertEqual(json_response["data_fim"], item.data_fim)
        self.assertEqual(json_response["atividades"], item.atividades)
        self.assertEqual(json_response["salario"], str(item.salario))
        self.assertEqual(json_response["usuario"], self.user.id)

    def test_update(self):
        item = ExperienciaProfissionalFactory(usuario=self.user)

        item_stub = ExperienciaProfissionalFactory.stub(usuario=self.user)

        data = {
            "empresa": item_stub.empresa,
            "cargo": item_stub.cargo,
            "data_inicio": item_stub.data_inicio,
            "data_fim": item_stub.data_fim,
            "atividades": item_stub.atividades,
            "salario": item_stub.salario,
        }

        response = self.client.put(f"{self.uri}{item.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["empresa"], item_stub.empresa)
        self.assertEqual(json_response["cargo"], item_stub.cargo)
        self.assertEqual(json_response["data_inicio"], item_stub.data_inicio)
        self.assertEqual(json_response["data_fim"], item_stub.data_fim)
        self.assertEqual(json_response["atividades"], item_stub.atividades)
        self.assertEqual(json_response["salario"], str(item_stub.salario))
        self.assertEqual(json_response["usuario"], self.user.id)

    def test_delete(self):
        item = ExperienciaProfissionalFactory(usuario=self.user)

        response = self.client.delete(f"{self.uri}{item.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(ExperienciaProfissional.objects.count(), 0)

    def test_detail_other(self):
        item = ExperienciaProfissionalFactory()
        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(
            response.status_code, self.detail_other_status or status.HTTP_403_FORBIDDEN
        )


class EmpregadorExperienciaProfissionalTestCase(AdminExperienciaProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/experiencia_profissional/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403
        self.detail_other_status = 200

        self.client.force_authenticate(user=self.user)


class CandidatoExperienciaProfissionalTestCase(AdminExperienciaProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/experiencia_profissional/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204
        self.detail_other_status = 403

        self.client.force_authenticate(user=self.user)


class GuestExperienciaProfissionalTestCase(AdminExperienciaProfissionalTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/experiencia_profissional/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
        self.detail_other_status = 401
