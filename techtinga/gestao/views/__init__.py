from gestao.views.projeto_service import ProjetoService
from gestao.views.projetos_por_linguagem import ProjetosPorLinguagemView
from gestao.views.tarefas_do_projeto import TarefasDoProjetoView
from gestao.views.tarefas_colaborador import TarefasColaboradorView
from .relatorio_ano import RelatorioAnoView

__all__ = [
    'ProjetoService',
    'ProjetosPorLinguagemView',
    'TarefasDoProjetoView',
    'TarefasColaboradorView',
    'RelatorioAnoView'
]