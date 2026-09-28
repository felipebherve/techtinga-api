from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gestao.models import Projeto
from gestao.serializers import ProjetoSerializer

class ProjetosPorLinguagemView(APIView):
    def get(self, request):
        inicio_str = request.query_params.get('inicio')
        fim_str = request.query_params.get('fim')
        linguagem = request.query_params.get('linguagem')

        if not all([inicio_str, fim_str, linguagem]):
            return Response(
                {"error": "Informe os parâmetros 'inicio', 'fim' e 'linguagem'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inicio = datetime.strptime(inicio_str, '%Y-%m-%d').date()
            fim = datetime.strptime(fim_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de data inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        projetos = Projeto.objects.listar_projetos_linguagem(inicio, fim, linguagem)
        serializer = ProjetoSerializer(projetos, many=True)
        return Response(serializer.data)