from django.contrib import admin
from gestao.models.projeto import Projeto
from gestao.models.tarefa import Tarefa

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'cliente', 'gerente', 'ativo')

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'projeto', 'responsavel', 'status', 'linguagem')