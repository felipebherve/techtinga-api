from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestao.models import Projeto, Tarefa
from gestao.serializers import TarefaSerializer

class TarefasDoProjetoView(APIView):
    def get(self, request, projeto_id):
        try:
            projeto = Projeto.objects.get(pk=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        tarefas = Tarefa.objects.listar_tarefas_projeto(projeto=projeto)
        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)