from django.db import models
from gestao.enumerations import Status


class TarefaManager(models.Manager):

    def concluidas(self):
        """Retorna apenas tarefas com status concluído."""
        return self.filter(status=Status.DONE)

    def atrasadas(self):
        """Retorna tarefas marcadas como atrasadas."""
        return self.filter(status=Status.DELAYED)

    def listar_tarefas_projeto(self, projeto):
        """
        Retorna as tarefas associadas a um projeto específico,
        ordenadas por responsável, status e data de criação.
        Lança ValueError se o projeto não for informado.
        """
        if projeto is None or projeto == '':
            raise ValueError("O projeto deve ser informado.")
        return self.filter(projeto=projeto).order_by('responsavel', 'status', 'criacao')

    def listar_tarefas_colaborador(self, responsavel):
        """
        Retorna as tarefas atribuídas a um colaborador/responsável,
        agrupadas por status e ordenadas por data de criação.
        Lança ValueError se o responsável estiver vazio.
        """
        if responsavel is None or not str(responsavel).strip():
            raise ValueError("O parâmetro 'responsavel' não pode ser vazio.")
        return self.filter(responsavel=str(responsavel).strip()).order_by('status', 'criacao')
