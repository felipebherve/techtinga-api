from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from gestao.models import BaseModel
from gestao.models.projeto import Projeto
from gestao.enumerations import LinguagemProgramacao, Status
from gestao.managers import TarefaManager


class Tarefa(BaseModel):

    objects = TarefaManager()

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='tarefas',
        verbose_name="Projeto"
    )

    titulo = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(5)],
        help_text='Informe o título da tarefa',
        verbose_name='Título da Tarefa',
        blank=False,
        null=False
    )

    descricao = models.TextField(
        max_length=1000,
        help_text='Informe a descrição da tarefa',
        verbose_name='Descrição da Tarefa',
        blank=True,
        null=True
    )

    linguagem = models.CharField(
        max_length=50,
        choices=LinguagemProgramacao.choices,
        help_text='Informe a linguagem da tarefa',
        verbose_name='Linguagem da Tarefa',
        blank=False,
        null=False
    )

    estimativa_horas = models.PositiveIntegerField(
        help_text='Informe a estimativa de horas da tarefa',
        verbose_name='Estimativa de Horas da Tarefa',
        blank=False,
        null=False,
        validators=[MinValueValidator(0)]
    )

    horas_registradas = models.PositiveIntegerField(
        default=0,
        help_text='Informe as horas registradas da tarefa',
        verbose_name='Horas Registradas da Tarefa',
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    prioridade = models.PositiveIntegerField(
        help_text='Informe a prioridade da tarefa',
        verbose_name='Prioridade da Tarefa',
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        help_text='Informe o status da tarefa',
        verbose_name='Status da Tarefa',
        blank=False,
        null=False
    )

    responsavel = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(3)],
        help_text='Informe o responsável pela tarefa',
        verbose_name='Responsável pela Tarefa',
        blank=False,
        null=False
    )

    criacao = models.DateTimeField(
        help_text='Informe a data e hora de criação da tarefa',
        verbose_name='Data de Criação da Tarefa',
        blank=False,
        null=False
    )

    conclusao = models.DateTimeField(
        help_text='Informe a data e hora de conclusão da tarefa',
        verbose_name='Data de Conclusão da Tarefa',
        blank=True,
        null=True
    )

    def clean(self):
        super().clean()

        if self.projeto:
            if not self.projeto.ativo or self.projeto.fim is not None:
                raise ValidationError(
                    "Não é possível adicionar ou alterar tarefas em um projeto inativo ou já finalizado."
                )

            if self.criacao:
                criacao_date = self.criacao.date() if hasattr(self.criacao, 'date') else self.criacao
                if criacao_date < self.projeto.inicio:
                    raise ValidationError({
                        'criacao': 'A data de criação da tarefa não pode ser anterior à data de início do projeto.'
                    })

        if self.criacao and self.conclusao:
            if self.conclusao < self.criacao:
                raise ValidationError({
                    'conclusao': 'A data de conclusão não pode ser anterior à data de criação.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        criacao_str = self.criacao.strftime('%d/%m/%Y') if self.criacao else ''
        conclusao_str = self.conclusao.strftime('%d/%m/%Y') if self.conclusao else 'N/A'
        
        return (f"{self.responsavel} | {self.linguagem} | {self.titulo} | "
                f"Criado em: {criacao_str} | Concluído em: {conclusao_str} | "
                f"Horas: {self.estimativa_horas}h | Status: {self.status}")