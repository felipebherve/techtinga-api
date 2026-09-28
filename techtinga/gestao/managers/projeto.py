from django.db import models
from django.db.models import Count, Sum, Q

class ProjetoManager(models.Manager):

    def por_ano(self, ano):
        """Retorna os projetos que iniciaram no ano especificado."""
        return self.filter(inicio__year=ano)

    def ativos(self):
        """Retorna apenas projetos ativos e que ainda não foram finalizados."""
        return self.filter(ativo=True, fim__isnull=True)

    def listar_projetos_linguagem(self, inicio, fim, linguagem):
        """
        Retorna os projetos que possuem tarefas criadas/iniciadas no período
        informado e desenvolvidas na linguagem especificada.
        """
        return self.filter(
            tarefas__criacao__date__gte=inicio,
            tarefas__criacao__date__lte=fim,
            tarefas__linguagem=linguagem
        ).distinct()

    def relatorio_por_ano(self, ano):
        """
        Retorna os projetos com tarefas desenvolvidas no ano informado,
        filtrando as tarefas do ano e agrupando totalizadores por status.
        """
        return self.get_queryset().filter(
            Q(tarefas__criacao__year=ano) | Q(tarefas__conclusao__year=ano)
        ).distinct().prefetch_related('tarefas')