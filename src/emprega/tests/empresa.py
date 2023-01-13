from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from emprega.factories import (
    UserFactory,
    EmpresaFactory,
    EnderecoFactory,
)
from emprega.models import UsuarioNivelChoices, Vaga, Empregador


class AdminEmpresaTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.ADMIN)
        self.client = APIClient()
        self.uri = "/empresa/"
        self.create_status = 422
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        endereco = EnderecoFactory.stub()
        item = EmpresaFactory.stub(usuario=self.user)

        data = {
            "cnpj": item.cnpj,
            "razao_social": item.razao_social,
            "nome_fantasia": item.nome_fantasia,
            "ramo_atividade": item.ramo_atividade,
            "numero_funcionarios": item.numero_funcionarios,
            "descricao": item.descricao,
            "telefone": item.telefone,
            "email": item.email,
            "site": item.site,
            "usuario": item.usuario.id,
            "cep": endereco.cep,
            "logradouro": endereco.logradouro,
            "numero": endereco.numero,
            "complemento": endereco.complemento,
            "bairro": endereco.bairro,
            "cidade": endereco.cidade,
            "estado": endereco.estado,
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_status or status.HTTP_201_CREATED
        )

        if self.create_status and self.create_status != status.HTTP_201_CREATED:
            return

        json_response = response.json()

        self.assertEqual(json_response["cnpj"], item.cnpj)
        self.assertEqual(json_response["razao_social"], item.razao_social)
        self.assertEqual(json_response["nome_fantasia"], item.nome_fantasia)
        self.assertEqual(json_response["ramo_atividade"], item.ramo_atividade)
        self.assertEqual(json_response["numero_funcionarios"], item.numero_funcionarios)
        self.assertEqual(json_response["descricao"], item.descricao)
        self.assertEqual(json_response["telefone"], item.telefone)
        self.assertEqual(json_response["email"], item.email)
        self.assertEqual(json_response["site"], item.site)
        self.assertEqual(json_response["usuario"], item.usuario.id)

        empregador = Empregador.objects.get(pk=item.usuario.id)
        empresas_empregador = empregador.empresas_usuario.all()

        self.assertEqual(len(empresas_empregador), 1)

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

        response = self.client.get(f"{self.uri}{item.id}/")

        self.assertEqual(response.status_code, self.detail_status or status.HTTP_200_OK)

        if self.detail_status and self.detail_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["id"], item.id)
        self.assertEqual(json_response["cnpj"], item.cnpj)
        self.assertEqual(json_response["razao_social"], item.razao_social)
        self.assertEqual(json_response["nome_fantasia"], item.nome_fantasia)
        self.assertEqual(json_response["ramo_atividade"], item.ramo_atividade)
        self.assertEqual(json_response["numero_funcionarios"], item.numero_funcionarios)
        self.assertEqual(json_response["descricao"], item.descricao)
        self.assertEqual(json_response["telefone"], item.telefone)
        self.assertEqual(json_response["email"], item.email)
        self.assertEqual(json_response["site"], item.site)
        self.assertEqual(json_response["endereco"], item.endereco.id)
        self.assertEqual(json_response["usuario"], item.usuario.id)

    def test_update(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        item = EmpresaFactory(usuario=self.user)

        data = {
            "cnpj": item.cnpj,
            "razao_social": item.razao_social,
            "nome_fantasia": item.nome_fantasia,
            "ramo_atividade": item.ramo_atividade,
            "numero_funcionarios": item.numero_funcionarios,
            "descricao": item.descricao,
            "telefone": item.telefone,
            "email": item.email,
            "site": item.site,
            "endereco": item.endereco.id,
            "usuario": item.usuario.id,
        }

        response = self.client.put(f"{self.uri}{item.id}/", data=data)

        self.assertEqual(response.status_code, self.update_status or status.HTTP_200_OK)

        if self.update_status and self.update_status != status.HTTP_200_OK:
            return

        json_response = response.json()

        self.assertEqual(json_response["id"], item.id)
        self.assertEqual(json_response["cnpj"], item.cnpj)
        self.assertEqual(json_response["razao_social"], item.razao_social)
        self.assertEqual(json_response["nome_fantasia"], item.nome_fantasia)
        self.assertEqual(json_response["ramo_atividade"], item.ramo_atividade)
        self.assertEqual(json_response["numero_funcionarios"], item.numero_funcionarios)
        self.assertEqual(json_response["descricao"], item.descricao)
        self.assertEqual(json_response["telefone"], item.telefone)
        self.assertEqual(json_response["email"], item.email)
        self.assertEqual(json_response["site"], item.site)
        self.assertEqual(json_response["endereco"], item.endereco.id)
        self.assertEqual(json_response["usuario"], item.usuario.id)

    def test_delete(self):
        if not self.user:
            self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)

        item = EmpresaFactory(usuario=self.user)

        response = self.client.delete(f"{self.uri}{item.id}/")

        self.assertEqual(
            response.status_code, self.delete_status or status.HTTP_204_NO_CONTENT
        )

        if self.delete_status and self.delete_status != status.HTTP_204_NO_CONTENT:
            return

        self.assertEqual(Vaga.objects.count(), 0)


class EmpregadorEmpresaTestCase(AdminEmpresaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        self.client = APIClient()
        self.uri = "/empresa/"
        self.create_status = 201
        self.update_status = 200
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 204

        self.client.force_authenticate(user=self.user)

    def test_create(self):
        return super().test_create()


class CandidatoEmpresaTestCase(AdminEmpresaTestCase):
    def setUp(self):
        self.user = UserFactory(nivel_usuario=UsuarioNivelChoices.CANDIDATO)
        self.client = APIClient()
        self.uri = "/empresa/"
        self.create_status = 403
        self.update_status = 403
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 403
        self.create_fail_status = 403

        self.client.force_authenticate(user=self.user)

    def test_create_fail(self):
        user = UserFactory(nivel_usuario=UsuarioNivelChoices.EMPREGADOR)
        endereco = EnderecoFactory()
        item = EmpresaFactory.stub(usuario=user)

        data = {
            "cnpj": item.cnpj,
            "razao_social": item.razao_social,
            "nome_fantasia": item.nome_fantasia,
            "ramo_atividade": item.ramo_atividade,
            "numero_funcionarios": item.numero_funcionarios,
            "descricao": item.descricao,
            "telefone": item.telefone,
            "email": item.email,
            "site": item.site,
            "endereco": endereco.id,
            "usuario": item.usuario.id,
        }

        response = self.client.post(self.uri, data=data)

        self.assertEqual(
            response.status_code, self.create_fail_status or status.HTTP_403_FORBIDDEN
        )

        if (
            self.create_fail_status
            and self.create_fail_status != status.HTTP_403_FORBIDDEN
        ):
            return


class GuestEmpresaTestCase(CandidatoEmpresaTestCase):
    def setUp(self):
        self.user = None
        self.client = APIClient()
        self.uri = "/empresa/"
        self.create_status = 401
        self.update_status = 401
        self.retrieve_status = 200
        self.detail_status = 200
        self.delete_status = 401
        self.create_fail_status = 401
