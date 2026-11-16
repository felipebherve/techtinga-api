from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestao.models import Projeto
from gestao.serializers import ProjetoSerializer


class ProjetosPorLinguagemView(APIView):
    def get(self, request):
        try:
            projetos = Projeto.objects.listar_projetos_linguagem(
                request.query_params.get('inicio'),
                request.query_params.get('fim'),
                request.query_params.get('linguagem'),
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjetoSerializer(projetos, many=True)
        return Response(serializer.data)
