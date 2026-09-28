from datetime import date
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator

from gestao.models import BaseModel
from gestao.enumerations import TipoProjeto
from gestao.managers import ProjetoManager


class Projeto(BaseModel):

    objects = ProjetoManager()

    codigo = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(5)],
        unique=True,
        verbose_name='Código do Projeto',
        help_text='Informe o código do projeto'
    )

    nome = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(5)],
        help_text='Informe o nome do projeto',
        verbose_name='Nome do Projeto'
    )

    tipo_projeto = models.CharField(
        max_length=20,
        choices=TipoProjeto.choices,
        verbose_name='Tipo do Projeto',
        help_text='Informe o tipo do projeto',
        null=False,
        blank=False
    )

    cliente = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(3)],
        help_text='Informe o nome do cliente',
        verbose_name='Cliente',
        blank=False,
        null=False
    )

    gerente = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(3)],
        help_text='Informe o nome do gerente',
        verbose_name='Gerente',
        blank=False,
        null=False
    )

    inicio = models.DateField(
        help_text='Informe a data de início do projeto',
        verbose_name='Data de Início',
        blank=False,
        null=False
    )

    previsao_termino = models.DateField(
        help_text='Informe a data de previsão de término do projeto',
        verbose_name='Previsão de Término',
        blank=False,
        null=False
    )

    fim = models.DateField(
        help_text='Informe a data real de término do projeto',
        verbose_name='Data de Fim',
        blank=True,
        null=True
    )

    orcamento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Informe o orçamento do projeto',
        verbose_name='Orçamento',
        blank=False,
        null=False
    )

    ativo = models.BooleanField(
        default=True
    )

    def clean(self):
        super().clean()

        if self.inicio and self.previsao_termino:
            if self.previsao_termino < self.inicio:
                raise ValidationError({
                    'previsao_termino': 'A previsão de término não pode ser anterior à data de início.'
                })

        if self.inicio and self.fim:
            if self.fim < self.inicio:
                raise ValidationError({
                    'fim': 'A data de fim real não pode ser anterior à data de início.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        inicio_str = self.inicio.strftime('%d/%m/%Y') if self.inicio else ''
        previsao_str = self.previsao_termino.strftime('%d/%m/%Y') if self.previsao_termino else ''
        tipo_str = self.get_tipo_projeto_display() if hasattr(self, 'get_tipo_projeto_display') else self.tipo_projeto

        return f"{self.cliente} | {self.nome} | {tipo_str} | R$ {self.orcamento} | Início: {inicio_str} | Previsão: {previsao_str}"