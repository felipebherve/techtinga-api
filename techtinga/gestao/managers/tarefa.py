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
        """
        return self.filter(projeto=projeto).order_by('responsavel', 'status', 'criacao')

    def listar_tarefas_colaborador(self, responsavel):
        """
        Retorna as tarefas atribuídas a um colaborador/responsável,
        agrupadas por status e ordenadas por data de criação.
        """
        return self.filter(responsavel=responsavel).order_by('status', 'criacao')