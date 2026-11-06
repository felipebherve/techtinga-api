from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from gestao.views import (
    ProjetosPorLinguagemView,
    TarefasDoProjetoView,
    TarefasColaboradorView,
    ProjetoService,
    RelatorioAnoView
)

urlpatterns = [
    # Login: recebe username e password e devolve o token
    path('token/', obtain_auth_token, name='token'),

    # h) Endpoints do CRUD completo (ProjetoService)
    path('projetos/', ProjetoService.as_view(), name='projeto-list-create'),
    path('projetos/<int:pk>/', ProjetoService.as_view(), name='projeto-detail'),

    # g) Endpoints de consulta específicos
    path('projetos/por-linguagem/', ProjetosPorLinguagemView.as_view(), name='projetos-por-linguagem'),
    path('projetos/<int:projeto_id>/tarefas/', TarefasDoProjetoView.as_view(), name='tarefas-projeto'),
    path('tarefas/colaborador/', TarefasColaboradorView.as_view(), name='tarefas-colaborador'),

    # i) Endpoint de relatório anual
    path('relatorio/ano/', RelatorioAnoView.as_view(), name='relatorio_ano'),
]