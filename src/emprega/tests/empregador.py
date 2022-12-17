from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    EmpresaFactory,
    EnderecoFactory,
)
from emprega.models import UsuarioNivelChoices, Empregador


class AdminEmpregadorTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/empregador/"
        self.create_status = None
        self.update_status = None
        self.retrieve_status = None
        self.detail_status = None
        self.delete_status = None
        self.self_detail_status = 404
        self.self_update_status = 404
        self.self_delete_status = 404

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        user = UserFactory.stub(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        empresa = EmpresaFactory.stub()
        endereco = EnderecoFactory.stub()
        data = {
            "cnpj": empresa.cnpj,
            "nome_fantasia": empresa.nome_fantasia,
            "razao_social": empresa.razao_social,
            "ramo_atividade": empresa.ramo_atividade,
            "numero_funcionarios": empresa.numero_funcionarios,
            "empresa_telefone": empresa.telefone,
            "empresa_email": empresa.email,
            "site": empresa.site,
            "descricao": empresa.descricao,
            "cep": endereco.cep,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "complemento": endereco.complemento,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
            "password": user.password,
            "nome": user.nome,
            "cpf": user.cpf,
            "data_nascimento": user.data_nascimento.strftime("%Y-%m-%d"),
            "sexo": user.sexo,
            "estado_civil": user.estado_civil,
            "area_atuacao": user.area_atuacao,
            "cargo": user.cargo,
            "email": user.email,
            "telefone": user.telefone,
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
        self.assertEqual(json_response["sexo"], data["sexo"])
        self.assertEqual(json_response["estado_civil"], data["estado_civil"])
        self.assertEqual(json_response["area_atuacao"], data["area_atuacao"])
        self.assertEqual(json_response["cargo"], data["cargo"])
        self.assertEqual(json_response["telefone"], data["telefone"])
        self.assertEqual(json_response["cnpj"], data["cnpj"])
        self.assertEqual(json_response["nome_fantasia"], data["nome_fantasia"])
        self.assertEqual(json_response["razao_social"], data["razao_social"])
        self.assertEqual(json_response["ramo_atividade"], data["ramo_atividade"])
        self.assertEqual(
            json_response["numero_funcionarios"], data["numero_funcionarios"]
        )
        self.assertEqual(json_response["empresa_telefone"], data["empresa_telefone"])
        self.assertEqual(json_response["empresa_email"], data["empresa_email"])
        self.assertEqual(json_response["site"], data["site"])
        self.assertEqual(json_response["descricao"], data["descricao"])
        self.assertEqual(json_response["cep"], data["cep"])
        self.assertEqual(json_response["logradouro"], data["logradouro"])
        self.assertEqual(json_response["numero"], data["numero"])
        self.assertEqual(json_response["complemento"], data["complemento"])
        self.assertEqual(json_response["bairro"], data["bairro"])
        self.assertEqual(json_response["cidade"], data["cidade"])
        self.assertEqual(json_response["estado"], data["estado"])

    def test_retrieve(self):
        UserFactory.create_batch(2, nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

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

    def test_self_detail(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

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

    def test_update(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        data = {"email": "example@example.com"}

        response = self.client.patch(f"{self.uri}{user.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["email"], data["email"])

    def test_self_update(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        data = {"email": "teste@teste.com"}

        response = self.client.patch(f"{self.uri}{self.user.id}/", data=data)

        self.assertEqual(
            response.status_code, self.self_update_status or status.HTTP_200_OK
        )

        if self.self_update_status and self.self_update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["email"], data["email"])

    def test_delete(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        response = self.client.delete(f"{self.uri}{user.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Empregador.objects.count(), 0)

    def test_self_delete(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

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


class EmpregadorEmpregadorTestCase(AdminEmpregadorTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/empregador/"
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
        UserFactory.create_batch(2, nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        response = self.client.get(self.uri)

        self.assertEqual(
            response.status_code, self.retrieve_status or status.HTTP_200_OK
        )

        json_response = response.json()

        self.assertEqual(len(json_response), 3)


class CanditatoEmpregadorTestCase(AdminEmpregadorTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/empregador/"
        self.create_status = 201
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 403
        self.delete_status = 403
        self.self_detail_status = 404
        self.self_update_status = 404
        self.self_delete_status = 404

        self.client.force_authenticate(user=self.user)


class GuestEmpregadorTestCase(AdminEmpregadorTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/empregador/"
        self.create_status = 201
        self.update_status = 401
        self.retrieve_status = 401
        self.detail_status = 401
        self.delete_status = 401
        self.self_detail_status = 401
        self.self_update_status = 401
        self.self_delete_status = 401
