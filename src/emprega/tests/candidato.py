import os
from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    ObjetivoProfissionalFactory,
)
from emprega.models import UsuarioNivelChoices, Candidato


class AdminCandidatoTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/candidato/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204
        self.self_detail_status = 404
        self.self_update_status = 404
        self.self_delete_status = 404

        self.client.force_authenticate(user=self.user)

    @mock.patch.dict(os.environ, {"RECAPTCHA_TESTING": "True"})
    def test_create(self):
        user = UserFactory.stub(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        objetivo_profisional = ObjetivoProfissionalFactory.stub(usuario=None)

        data = {
            "g-recaptcha-response": "passed",
            "password": user.password,
            "nome": user.nome,
            "cpf": user.cpf,
            "data_nascimento": user.data_nascimento.strftime("%Y-%m-%d"),
            "sexo": user.sexo,
            "estado_civil": user.estado_civil,
            "tipo_deficiencia": user.tipo_deficiencia,
            "email": user.email,
            "telefone": user.telefone,
            "cargo": objetivo_profisional.cargo,
            "salario": objetivo_profisional.salario,
            "modelo_trabalho": objetivo_profisional.modelo_trabalho,
            "regime_contratual": objetivo_profisional.regime_contratual,
            "jornada_trabalho": objetivo_profisional.jornada_trabalho,
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
        UserFactory.create_batch(2, nivel_usuario=UsuarioNivelChoices.CANDIDATO)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 2)

    def test_detail(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

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
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

        data = {"email": "example@example.com"}

        response = self.client.patch(f"{self.uri}{user.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["email"], data["email"])

    def test_delete(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

        response = self.client.delete(f"{self.uri}{user.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Candidato.objects.count(), 0)

    def test_self_detail(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

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
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

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
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)

        response = self.client.delete(f"{self.uri}{self.user.id}/")

        self.assertEqual(
            response.status_code, self.self_delete_status or status.HTTP_204_NO_CONTENT
        )

        if (
            self.self_delete_status
            and self.self_delete_status != status.HTTP_204_NO_CONTENT
        ):
            return

        self.assertEqual(Candidato.objects.count(), 0)


class EmpregadorCandidatoTestCase(AdminCandidatoTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/candidato/"
        self.create_status = 201
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 403
        self.delete_status = 403
        self.self_detail_status = 404
        self.self_update_status = 404
        self.self_delete_status = 404

        self.client.force_authenticate(user=self.user)


class CandidatoCandidatoTestCase(AdminCandidatoTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/candidato/"
        self.create_status = 201
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 403
        self.delete_status = 403
        self.self_detail_status = 200
        self.self_update_status = 200
        self.self_delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_retrieve(self):
        UserFactory.create_batch(2, nivel_usuario=UsuarioNivelChoices.CANDIDATO)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        json_response = response.json()

        self.assertEqual(len(json_response), 3)


class GuestCandidatoTestCase(AdminCandidatoTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/candidato/"
        self.create_status = 201
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
        self.self_detail_status = 401
        self.self_update_status = 401
        self.self_delete_status = 401
