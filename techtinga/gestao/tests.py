from datetime import date, datetime

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from gestao.models import Projeto, Tarefa


def criar_projeto(codigo='PRJ-TESTE-01', **extra):
    dados = dict(
        codigo=codigo,
        nome='Projeto de teste',
        tipo_projeto='DESKTOP',
        cliente='Cliente X',
        gerente='Gerente Y',
        inicio=date(2026, 1, 10),
        previsao_termino=date(2026, 12, 20),
        orcamento='1000.00',
    )
    dados.update(extra)
    return Projeto.objects.create(**dados)


def criar_tarefa(projeto, **extra):
    dados = dict(
        projeto=projeto,
        titulo='Tarefa de teste',
        linguagem='CPLUSPLUS',
        estimativa_horas=5,
        status='DOING',
        responsavel='Ana Lima',
        criacao=timezone.make_aware(datetime(2026, 3, 1, 10, 0)),
    )
    dados.update(extra)
    return Tarefa.objects.create(**dados)


class EnumsTest(TestCase):
    def test_aceita_desktop_e_cplusplus(self):
        projeto = criar_projeto()
        tarefa = criar_tarefa(projeto)
        self.assertEqual(projeto.tipo_projeto, 'DESKTOP')
        self.assertEqual(tarefa.linguagem, 'CPLUSPLUS')


class ManagersTest(TestCase):
    def setUp(self):
        self.projeto = criar_projeto()
        criar_tarefa(self.projeto)

    def test_listar_projetos_linguagem_valido(self):
        qs = Projeto.objects.listar_projetos_linguagem('2026-01-01', '2026-12-31', 'cplusplus')
        self.assertEqual(list(qs), [self.projeto])

    def test_listar_projetos_linguagem_invalida(self):
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem('2026-01-01', '2026-12-31', 'RUBY')

    def test_listar_projetos_datas_invalidas(self):
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem('01/01/2026', '2026-12-31', 'PYTHON')
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem('2026-12-31', '2026-01-01', 'PYTHON')
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem(None, '2026-01-01', 'PYTHON')

    def test_listar_tarefas_colaborador_vazio(self):
        for valor in (None, '', '   '):
            with self.assertRaises(ValueError):
                Tarefa.objects.listar_tarefas_colaborador(valor)
        self.assertEqual(Tarefa.objects.listar_tarefas_colaborador(' Ana Lima ').count(), 1)

    def test_listar_tarefas_projeto_sem_projeto(self):
        with self.assertRaises(ValueError):
            Tarefa.objects.listar_tarefas_projeto(None)


class CrudProjetoComTokenTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user('aluno', password='senha-forte-123')
        perms = Permission.objects.filter(
            content_type__app_label='gestao', content_type__model='projeto'
        )
        self.usuario.user_permissions.set(perms)
        self.sem_perm = User.objects.create_user('visitante', password='senha-forte-123')

    def pegar_token(self, username):
        resp = self.client.post('/api/token/', {'username': username, 'password': 'senha-forte-123'})
        self.assertEqual(resp.status_code, 200)
        return resp.data['token']

    def test_endpoint_de_token(self):
        token = self.pegar_token('aluno')
        self.assertEqual(token, Token.objects.get(user=self.usuario).key)
        resp = self.client.post('/api/token/', {'username': 'aluno', 'password': 'errada'})
        self.assertEqual(resp.status_code, 400)

    def test_sem_token_responde_401(self):
        self.assertEqual(self.client.get('/api/projetos/').status_code, 401)

    def test_crud_completo(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.pegar_token('aluno'))
        dados = {
            'codigo': 'PRJ-CRUD-01', 'nome': 'Projeto CRUD', 'tipo_projeto': 'DESKTOP',
            'cliente': 'Cliente Z', 'gerente': 'Gerente W', 'inicio': '2026-02-01',
            'previsao_termino': '2026-10-01', 'orcamento': '5000.00',
        }
        resp = self.client.post('/api/projetos/', dados, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)
        pk = resp.data['id']

        resp = self.client.get('/api/projetos/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

        resp = self.client.get(f'/api/projetos/{pk}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['codigo'], 'PRJ-CRUD-01')

        dados['nome'] = 'Projeto CRUD alterado'
        resp = self.client.put(f'/api/projetos/{pk}/', dados, format='json')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(Projeto.objects.get(pk=pk).nome, 'Projeto CRUD alterado')

        resp = self.client.delete(f'/api/projetos/{pk}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Projeto.objects.filter(pk=pk).exists())

    def test_usuario_sem_permissao_nao_altera(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.pegar_token('visitante'))
        resp = self.client.post('/api/projetos/', {'codigo': 'PRJ-X-0001'}, format='json')
        self.assertEqual(resp.status_code, 403)
        projeto = criar_projeto()
        self.assertEqual(self.client.delete(f'/api/projetos/{projeto.pk}/').status_code, 403)


class ConsultasSoGetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.projeto = criar_projeto()
        criar_tarefa(self.projeto)
        self.urls = [
            '/api/projetos/por-linguagem/?inicio=2026-01-01&fim=2026-12-31&linguagem=CPLUSPLUS',
            f'/api/projetos/{self.projeto.pk}/tarefas/',
            '/api/tarefas/colaborador/?responsavel=Ana Lima',
            '/api/relatorio/ano/?ano=2026',
        ]

    def test_get_funciona(self):
        for url in self.urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_outros_metodos_405(self):
        for url in self.urls:
            for metodo in ('post', 'put', 'patch', 'delete'):
                resp = getattr(self.client, metodo)(url)
                self.assertEqual(resp.status_code, 405, f'{metodo.upper()} {url}')

    def test_parametros_invalidos_400(self):
        self.assertEqual(self.client.get(
            '/api/projetos/por-linguagem/?inicio=2026-01-01&fim=2026-12-31&linguagem=RUBY').status_code, 400)
        self.assertEqual(self.client.get('/api/tarefas/colaborador/?responsavel=').status_code, 400)
