import os
import tempfile
from datetime import date, datetime
from io import StringIO

from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from gestao.enumerations import LinguagemProgramacao, Status, TipoProjeto
from gestao.models import Projeto, Tarefa


def criar_projeto(codigo='PRJ-TESTE-01', **campos):
    dados = {
        'codigo': codigo,
        'nome': 'Projeto de teste',
        'tipo_projeto': TipoProjeto.API,
        'cliente': 'Cliente Teste',
        'gerente': 'Gerente Teste',
        'inicio': date(2026, 1, 10),
        'previsao_termino': date(2026, 12, 20),
        'orcamento': '1000.00',
    }
    dados.update(campos)
    return Projeto.objects.create(**dados)


def criar_tarefa(projeto, **campos):
    dados = {
        'projeto': projeto,
        'titulo': 'Tarefa de teste',
        'linguagem': LinguagemProgramacao.PYTHON,
        'estimativa_horas': 10,
        'horas_registradas': 5,
        'prioridade': 3,
        'status': Status.DOING,
        'responsavel': 'Ana Souza',
        'criacao': timezone.make_aware(datetime(2026, 3, 1, 9, 0)),
    }
    dados.update(campos)
    return Tarefa.objects.create(**dados)


class EnumeracoesTests(TestCase):

    def test_tipo_projeto_aceita_desktop(self):
        projeto = criar_projeto(tipo_projeto=TipoProjeto.DESKTOP)
        self.assertEqual(projeto.tipo_projeto, 'DESKTOP')

    def test_linguagem_aceita_cplusplus(self):
        tarefa = criar_tarefa(criar_projeto(), linguagem=LinguagemProgramacao.CPLUSPLUS)
        self.assertEqual(tarefa.linguagem, 'CPLUSPLUS')


class ManagersTests(TestCase):

    def setUp(self):
        self.projeto = criar_projeto()
        criar_tarefa(self.projeto, titulo='Tarefa em Python')
        criar_tarefa(self.projeto, titulo='Tarefa em Java', linguagem=LinguagemProgramacao.JAVA,
                     responsavel='Bruno Lima')

    def test_listar_projetos_linguagem(self):
        projetos = Projeto.objects.listar_projetos_linguagem(
            date(2026, 1, 1), date(2026, 12, 31), LinguagemProgramacao.PYTHON)
        self.assertEqual(list(projetos), [self.projeto])

    def test_listar_projetos_linguagem_recusa_linguagem_invalida(self):
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem(date(2026, 1, 1), date(2026, 12, 31), 'COBOL')

    def test_listar_projetos_linguagem_recusa_periodo_invertido(self):
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem(
                date(2026, 12, 31), date(2026, 1, 1), LinguagemProgramacao.PYTHON)

    def test_listar_projetos_linguagem_recusa_texto_no_lugar_de_data(self):
        with self.assertRaises(ValueError):
            Projeto.objects.listar_projetos_linguagem('2026-01-01', date(2026, 12, 31), 'PYTHON')

    def test_listar_tarefas_projeto_ordena_por_responsavel(self):
        tarefas = Tarefa.objects.listar_tarefas_projeto(self.projeto)
        self.assertEqual([t.responsavel for t in tarefas], ['Ana Souza', 'Bruno Lima'])

    def test_listar_tarefas_projeto_recusa_projeto_invalido(self):
        with self.assertRaises(ValueError):
            Tarefa.objects.listar_tarefas_projeto(None)

    def test_listar_tarefas_colaborador(self):
        tarefas = Tarefa.objects.listar_tarefas_colaborador('Bruno Lima')
        self.assertEqual([t.titulo for t in tarefas], ['Tarefa em Java'])

    def test_listar_tarefas_colaborador_recusa_nome_vazio(self):
        with self.assertRaises(ValueError):
            Tarefa.objects.listar_tarefas_colaborador('  ')


class ConsultasApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.projeto = criar_projeto()
        criar_tarefa(self.projeto)

    def test_projetos_por_linguagem(self):
        resposta = self.client.get('/api/projetos/por-linguagem/',
                                   {'inicio': '2026-01-01', 'fim': '2026-12-31', 'linguagem': 'PYTHON'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.json()), 1)

    def test_projetos_por_linguagem_invalida_devolve_400(self):
        resposta = self.client.get('/api/projetos/por-linguagem/',
                                   {'inicio': '2026-01-01', 'fim': '2026-12-31', 'linguagem': 'COBOL'})
        self.assertEqual(resposta.status_code, 400)

    def test_consultas_aceitam_somente_get(self):
        resposta = self.client.post('/api/tarefas/colaborador/?responsavel=Ana Souza')
        self.assertEqual(resposta.status_code, 405)

    def test_tarefas_do_projeto_inexistente_devolve_404(self):
        resposta = self.client.get('/api/projetos/99999/tarefas/')
        self.assertEqual(resposta.status_code, 404)

    def test_tarefas_colaborador_com_nome_curto_devolve_400(self):
        resposta = self.client.get('/api/tarefas/colaborador/', {'responsavel': 'A'})
        self.assertEqual(resposta.status_code, 400)


class CrudProjetoComTokenTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user('gerente', password='senha-forte-123')
        self.dados = {
            'codigo': 'PRJ-API-01',
            'nome': 'Projeto pela API',
            'tipo_projeto': 'DESKTOP',
            'cliente': 'Cliente API',
            'gerente': 'Gerente API',
            'inicio': '2026-02-01',
            'previsao_termino': '2026-10-01',
            'orcamento': '2500.00',
        }

    def autenticar(self, *permissoes):
        for codigo in permissoes:
            self.usuario.user_permissions.add(Permission.objects.get(codename=codigo))
        resposta = self.client.post('/api/token/',
                                    {'username': 'gerente', 'password': 'senha-forte-123'})
        self.assertEqual(resposta.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {resposta.json()['token']}")

    def test_sem_token_devolve_401(self):
        self.assertEqual(self.client.get('/api/projetos/').status_code, 401)

    def test_token_com_senha_errada_devolve_400(self):
        resposta = self.client.post('/api/token/', {'username': 'gerente', 'password': 'errada'})
        self.assertEqual(resposta.status_code, 400)

    def test_sem_permissao_nao_cria(self):
        self.autenticar()
        self.assertEqual(self.client.post('/api/projetos/', self.dados).status_code, 403)

    def test_crud_completo(self):
        self.autenticar('add_projeto', 'change_projeto', 'delete_projeto')

        criado = self.client.post('/api/projetos/', self.dados)
        self.assertEqual(criado.status_code, 201)
        pk = criado.json()['id']

        self.assertEqual(self.client.get('/api/projetos/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/projetos/{pk}/').json()['codigo'], 'PRJ-API-01')

        alterado = dict(self.dados, nome='Projeto alterado')
        self.assertEqual(self.client.put(f'/api/projetos/{pk}/', alterado).json()['nome'], 'Projeto alterado')

        self.assertEqual(self.client.delete(f'/api/projetos/{pk}/').status_code, 204)
        self.assertFalse(Projeto.objects.filter(pk=pk).exists())

    def test_previsao_antes_do_inicio_devolve_400(self):
        self.autenticar('add_projeto')
        dados = dict(self.dados, previsao_termino='2026-01-01')
        resposta = self.client.post('/api/projetos/', dados)
        self.assertEqual(resposta.status_code, 400)
        self.assertIn('previsao_termino', resposta.json())

    def test_patch_altera_so_o_campo_enviado(self):
        self.autenticar('change_projeto')
        projeto = criar_projeto()
        resposta = self.client.patch(f'/api/projetos/{projeto.pk}/', {'nome': 'Nome novo do projeto'})
        self.assertEqual(resposta.status_code, 200)
        projeto.refresh_from_db()
        self.assertEqual(projeto.nome, 'Nome novo do projeto')
        self.assertEqual(projeto.cliente, 'Cliente Teste')

    def test_token_e_unico_por_usuario(self):
        self.autenticar()
        self.assertEqual(Token.objects.filter(user=self.usuario).count(), 1)


class ImportarCsvTests(TestCase):

    CABECALHO = ('projeto_codigo,projeto_nome,projeto_tipo_projeto,projeto_cliente,projeto_gerente,'
                 'projeto_inicio,projeto_previsao_termino,projeto_fim,projeto_orcamento,projeto_ativo,'
                 'tarefa_titulo,tarefa_descricao,tarefa_linguagem,tarefa_estimativa_horas,'
                 'tarefa_horas_registradas,tarefa_prioridade,tarefa_status,tarefa_responsavel,'
                 'tarefa_criacao,tarefa_conclusao\n')

    def importar(self, *linhas):
        with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8') as arquivo:
            arquivo.write(self.CABECALHO + ''.join(linhas))
        self.addCleanup(os.remove, arquivo.name)
        saida = StringIO()
        call_command('importar_csv', csv=arquivo.name, stdout=saida)
        return saida.getvalue()

    def test_opcao_csv_e_desktop_e_cplusplus(self):
        saida = self.importar(
            'PRJ-CSV-01,Sistema desktop,DESKTOP,Cliente CSV,Gerente CSV,2026-01-05,2026-09-30,,'
            '5000.00,True,Tela de cadastro,,CPLUSPLUS,8,4,2,DOING,Carla Dias,2026-02-01T10:00:00,\n'
        )
        self.assertIn('Tarefas salvas: 1', saida)
        self.assertEqual(Projeto.objects.get().tipo_projeto, 'DESKTOP')
        self.assertEqual(Tarefa.objects.get().linguagem, 'CPLUSPLUS')

    def test_descarta_linhas_invalidas(self):
        base = ('PRJ-CSV-02,Sistema web,WEB,Cliente CSV,Gerente CSV,2026-01-05,2026-09-30,,'
                '5000.00,True,')
        saida = self.importar(
            base + 'Tarefa em Ruby,,RUBY,8,4,2,DOING,Carla Dias,2026-02-01T10:00:00,\n',
            base + 'Tarefa finalizada,,PYTHON,8,4,2,FINISHED,Carla Dias,2026-02-01T10:00:00,\n',
            base + 'Prioridade alta,,PYTHON,8,4,9,DOING,Carla Dias,2026-02-01T10:00:00,\n',
            base + 'Horas negativas,,PYTHON,-3,4,2,DOING,Carla Dias,2026-02-01T10:00:00,\n',
            base + 'Tarefa correta,,PYTHON,8,4,2,DOING,Carla Dias,2026-02-01T10:00:00,\n',
        )
        self.assertIn('Tarefas salvas: 1 | Erros: 4', saida)
        self.assertEqual(Tarefa.objects.get().titulo, 'Tarefa correta')
