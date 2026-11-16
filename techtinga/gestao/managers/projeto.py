from datetime import date, datetime
from django.db import models
from django.db.models import Count, Sum, Q

from gestao.enumerations import LinguagemProgramacao


def _converter_data(valor, nome):
    """Aceita date, datetime ou texto no formato YYYY-MM-DD e devolve um date."""
    if valor is None or valor == '':
        raise ValueError(f"O parâmetro '{nome}' é obrigatório.")
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"O parâmetro '{nome}' deve estar no formato YYYY-MM-DD.")


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
        Lança ValueError se algum parâmetro for inválido.
        """
        inicio = _converter_data(inicio, 'inicio')
        fim = _converter_data(fim, 'fim')
        if fim < inicio:
            raise ValueError("A data 'fim' não pode ser anterior à data 'inicio'.")

        if not linguagem or not str(linguagem).strip():
            raise ValueError("O parâmetro 'linguagem' é obrigatório.")
        linguagem = str(linguagem).strip().upper()
        if linguagem not in LinguagemProgramacao.values:
            opcoes = ', '.join(LinguagemProgramacao.values)
            raise ValueError(f"Linguagem '{linguagem}' inválida. Opções: {opcoes}.")

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
