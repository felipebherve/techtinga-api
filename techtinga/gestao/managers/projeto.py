from datetime import date

from django.db import models
from django.db.models import Q

from gestao.enumerations import LinguagemProgramacao


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
        if not isinstance(inicio, date) or not isinstance(fim, date):
            raise ValueError("Os parâmetros 'inicio' e 'fim' devem ser datas.")
        if fim < inicio:
            raise ValueError("A data 'fim' não pode ser anterior à data 'inicio'.")
        if linguagem not in LinguagemProgramacao.values:
            opcoes = ', '.join(LinguagemProgramacao.values)
            raise ValueError(f"Linguagem inválida. Use uma destas: {opcoes}.")

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
