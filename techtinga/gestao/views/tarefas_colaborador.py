from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestao.models import Tarefa
from gestao.serializers import TarefaSerializer

class TarefasColaboradorView(APIView):
    def get(self, request):
        responsavel = request.query_params.get('responsavel')
        if not responsavel:
            return Response({"error": "Informe o parâmetro 'responsavel'."}, status=status.HTTP_400_BAD_REQUEST)

        tarefas = Tarefa.objects.listar_tarefas_colaborador(responsavel=responsavel)
        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)