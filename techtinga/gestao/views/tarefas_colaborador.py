from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestao.models import Tarefa
from gestao.serializers import TarefaSerializer


class TarefasColaboradorView(APIView):
    def get(self, request):
        try:
            tarefas = Tarefa.objects.listar_tarefas_colaborador(
                responsavel=request.query_params.get('responsavel')
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)
