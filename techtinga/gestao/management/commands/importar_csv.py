import csv
from datetime import datetime, date
from django.core.management.base import BaseCommand
from gestao.models.projeto import Projeto
from gestao.models.tarefa import Tarefa


class Command(BaseCommand):
    help = 'Importa projetos e tarefas a partir do arquivo CSV'

    def add_argument(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='techtinga.csv',
            help='Caminho para o arquivo CSV'
        )

    def handle(self, *args, **options):
        caminho_csv = options.get('csv', 'techtinga.csv')
        sucesso = 0
        erros = 0

        # Opções do Enum aceitas pelo model Projeto
        MAPEAMENTO_TIPO = {
            'DESKTOP': 'WEB',  # Ajuste para uma opção válida do seu Enum caso DESKTOP não exista
        }

        with open(caminho_csv, mode='r', encoding='utf-8-sig') as arquivo:
            reader = csv.DictReader(arquivo)

            for idx, linha in enumerate(reader, start=2):
                try:
                    # Validar e obter os dados básicos do projeto
                    codigo_proj = linha.get('projeto_codigo', '').strip()
                    if not codigo_proj:
                        self.stdout.write(self.style.WARNING(f"Linha {idx}: Código do projeto ausente."))
                        erros += 1
                        continue

                    tipo_proj = linha.get('projeto_tipo_projeto', '').strip()
                    tipo_proj = MAPEAMENTO_TIPO.get(tipo_proj, tipo_proj)

                    # Tratar datas do Projeto
                    inicio_proj = date.fromisoformat(linha['projeto_inicio'].strip()) if linha.get('projeto_inicio') else None
                    previsao_proj = date.fromisoformat(linha['projeto_previsao_termino'].strip()) if linha.get('projeto_previsao_termino') else None
                    fim_proj = date.fromisoformat(linha['projeto_fim'].strip()) if linha.get('projeto_fim') else None

                    # Tratar orçamento e ativo
                    orcamento = float(linha['projeto_orcamento']) if linha.get('projeto_orcamento') else 0.0
                    ativo = str(linha.get('projeto_ativo', 'True')).strip().lower() in ['true', '1', 't', 'sim']

                    # Inserção/Busca do Projeto (bypassa validações do ModelForm)
                    projeto, _ = Projeto.objects.get_or_create(
                        codigo=codigo_proj,
                        defaults={
                            'nome': linha.get('projeto_nome', '').strip(),
                            'tipo_projeto': tipo_proj,
                            'cliente': linha.get('projeto_cliente', '').strip(),
                            'gerente': linha.get('projeto_gerente', '').strip(),
                            'inicio': inicio_proj,
                            'previsao_termino': previsao_proj,
                            'fim': fim_proj,
                            'orcamento': orcamento,
                            'ativo': ativo,
                        }
                    )

                    # Tratar dados da Tarefa
                    titulo_tar = linha.get('tarefa_titulo', '').strip()
                    if not titulo_tar:
                        continue  # Se for apenas registro de projeto sem tarefa

                    criacao_tar = datetime.fromisoformat(linha['tarefa_criacao'].strip()) if linha.get('tarefa_criacao') else None
                    conclusao_tar = datetime.fromisoformat(linha['tarefa_conclusao'].strip()) if linha.get('tarefa_conclusao') else None

                    # Tratar inteiros com segurança contra valores vazios ou decimais
                    est_horas = int(float(linha['tarefa_estimativa_horas'])) if linha.get('tarefa_estimativa_horas') else 0
                    reg_horas = int(float(linha['tarefa_horas_registradas'])) if linha.get('tarefa_horas_registradas') else 0
                    prioridade = int(float(linha['tarefa_prioridade'])) if linha.get('tarefa_prioridade') else None

                    # Criação da Tarefa
                    Tarefa.objects.create(
                        projeto=projeto,
                        titulo=titulo_tar,
                        descricao=linha.get('tarefa_descricao', '').strip() or None,
                        linguagem=linha.get('tarefa_linguagem', '').strip(),
                        estimativa_horas=est_horas,
                        horas_registradas=reg_horas,
                        prioridade=prioridade,
                        status=linha.get('tarefa_status', '').strip(),
                        responsavel=linha.get('tarefa_responsavel', '').strip(),
                        criacao=criacao_tar,
                        conclusao=conclusao_tar,
                    )
                    sucesso += 1

                except Exception as e:
                    erros += 1
                    # Imprime o erro exato que impediu o cadastro na linha
                    self.stdout.write(self.style.ERROR(f"Linha {idx}: Falha na importação -> {type(e).__name__}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nFinalizado! Tarefas salvas: {sucesso} | Erros: {erros}"))