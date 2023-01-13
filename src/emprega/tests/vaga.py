from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    EmpresaFactory,
    VagaFactory,
)
from emprega.models import UsuarioNivelChoices, Vaga


class AdminVagaTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.empresa = EmpresaFactory(usuario=self.user)
        self.client = APIClient()
        self.uri = "/vaga/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        if not self.empresa:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
            self.empresa = EmpresaFactory(usuario=self.user)

        vaga = VagaFactory.stub(empresa=self.empresa)

        data = {
            "cargo": vaga.cargo,
            "atividades": vaga.atividades,
            "requisitos": vaga.requisitos,
            "pessoa_deficiencia": vaga.pessoa_deficiencia,
            "salario": vaga.salario,
            "jornada_trabalho": vaga.jornada_trabalho,
            "modelo_trabalho": vaga.modelo_trabalho,
            "regime_contratual": vaga.regime_contratual,
            "sexo": vaga.sexo,
            "idade_minima": vaga.idade_minima,
            "idade_maxima": vaga.idade_maxima,
            "quantidade_vagas": vaga.quantidade_vagas,
            "beneficios": vaga.beneficios,
            "empresa": self.empresa.id,
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["cargo"], data["cargo"])
        self.assertEqual(json_response["atividades"], data["atividades"])
        self.assertEqual(json_response["requisitos"], data["requisitos"])
        self.assertEqual(
            json_response["pessoa_deficiencia"], data["pessoa_deficiencia"]
        )
        self.assertEqual(json_response["salario"], str(data["salario"]))
        self.assertEqual(json_response["jornada_trabalho"], data["jornada_trabalho"])
        self.assertEqual(json_response["modelo_trabalho"], data["modelo_trabalho"])
        self.assertEqual(json_response["regime_contratual"], data["regime_contratual"])
        self.assertEqual(json_response["sexo"], data["sexo"])
        self.assertEqual(json_response["idade_minima"], data["idade_minima"])
        self.assertEqual(json_response["idade_maxima"], data["idade_maxima"])
        self.assertEqual(json_response["quantidade_vagas"], data["quantidade_vagas"])
        self.assertEqual(json_response["beneficios"], data["beneficios"])
        self.assertEqual(json_response["empresa"], data["empresa"])

    def test_retrieve(self):
        if not self.empresa:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
            self.empresa = EmpresaFactory(usuario=self.user)

        VagaFactory.create_batch(2, empresa=self.empresa)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        if self.retrieve_status and self.retrieve_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(len(json_response), 2)

    def test_detail(self):
        if not self.empresa:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
            self.empresa = EmpresaFactory(usuario=self.user)

        vaga = VagaFactory(empresa=self.empresa)

        response = self.client.get(f"{self.uri}{vaga.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cargo"], vaga.cargo)
        self.assertEqual(json_response["atividades"], vaga.atividades)
        self.assertEqual(json_response["requisitos"], vaga.requisitos)
        self.assertEqual(json_response["pessoa_deficiencia"], vaga.pessoa_deficiencia)
        self.assertEqual(json_response["salario"], str(vaga.salario))
        self.assertEqual(json_response["jornada_trabalho"], vaga.jornada_trabalho)
        self.assertEqual(json_response["modelo_trabalho"], vaga.modelo_trabalho)
        self.assertEqual(json_response["regime_contratual"], vaga.regime_contratual)
        self.assertEqual(json_response["sexo"], vaga.sexo)
        self.assertEqual(json_response["idade_minima"], vaga.idade_minima)
        self.assertEqual(json_response["idade_maxima"], vaga.idade_maxima)
        self.assertEqual(json_response["quantidade_vagas"], vaga.quantidade_vagas)
        self.assertEqual(json_response["beneficios"], vaga.beneficios)
        self.assertEqual(json_response["empresa"], vaga.empresa.id)

    def test_update(self):
        if not self.empresa:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
            self.empresa = EmpresaFactory(usuario=self.user)

        vaga = VagaFactory(empresa=self.empresa)

        data = {
            "cargo": vaga.cargo,
            "atividades": vaga.atividades,
            "requisitos": vaga.requisitos,
            "pessoa_deficiencia": vaga.pessoa_deficiencia,
            "salario": vaga.salario,
            "jornada_trabalho": vaga.jornada_trabalho,
            "modelo_trabalho": vaga.modelo_trabalho,
            "regime_contratual": vaga.regime_contratual,
            "sexo": vaga.sexo,
            "idade_minima": vaga.idade_minima,
            "idade_maxima": vaga.idade_maxima,
            "quantidade_vagas": vaga.quantidade_vagas,
            "beneficios": vaga.beneficios,
        }

        response = self.client.patch(f"{self.uri}{vaga.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["cargo"], data["cargo"])
        self.assertEqual(json_response["atividades"], data["atividades"])
        self.assertEqual(json_response["requisitos"], data["requisitos"])
        self.assertEqual(
            json_response["pessoa_deficiencia"], data["pessoa_deficiencia"]
        )
        self.assertEqual(json_response["salario"], str(data["salario"]))
        self.assertEqual(json_response["jornada_trabalho"], data["jornada_trabalho"])
        self.assertEqual(json_response["modelo_trabalho"], data["modelo_trabalho"])
        self.assertEqual(json_response["regime_contratual"], data["regime_contratual"])
        self.assertEqual(json_response["sexo"], data["sexo"])
        self.assertEqual(json_response["idade_minima"], data["idade_minima"])
        self.assertEqual(json_response["idade_maxima"], data["idade_maxima"])
        self.assertEqual(json_response["quantidade_vagas"], data["quantidade_vagas"])
        self.assertEqual(json_response["beneficios"], data["beneficios"])
        self.assertEqual(json_response["empresa"], vaga.empresa.id)

    def test_delete(self):
        if not self.empresa:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
            self.empresa = EmpresaFactory(usuario=self.user)

        vaga = VagaFactory(empresa=self.empresa)

        response = self.client.delete(f"{self.uri}{vaga.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Vaga.objects.count(), 0)


class EmpregadorVagaTestCase(AdminVagaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.empresa = EmpresaFactory(usuario=self.user)
        self.client = APIClient()
        self.uri = "/vaga/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)


class CandidatoVagaTestCase(AdminVagaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.empresa = EmpresaFactory(usuario=self.user)
        self.client = APIClient()
        self.uri = "/vaga/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403

        self.client.force_authenticate(user=self.user)


class GuestVagaTestCase(AdminVagaTestCase):
    def setUp(self):
        self.user = None
        self.empresa = None
        self.client = APIClient()
        self.uri = "/vaga/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 401
