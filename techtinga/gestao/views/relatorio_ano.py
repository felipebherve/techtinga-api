from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from gestao.models import Projeto
from gestao.serializers import ProjetoSerializer, TarefaSerializer

class RelatorioAnoView(APIView):
    def get(self, request):
        ano = request.query_params.get('ano')
        
        if not ano:
            return Response(
                {"erro": "O parâmetro 'ano' é obrigatório. Exemplo: ?ano=2026"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ano = int(ano)
        except ValueError:
            return Response(
                {"erro": "O parâmetro 'ano' deve ser um número inteiro."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        projetos = Projeto.objects.relatorio_por_ano(ano)
        resultado_projetos = []

        for projeto in projetos:
            tarefas_do_ano = (
                projeto.tarefas.filter(criacao__year=ano) | 
                projeto.tarefas.filter(conclusao__year=ano)
            ).distinct()

            totalizadores = tarefas_do_ano.values('status').annotate(
                total_tarefas=Count('id'),
                horas_estimadas=Sum('estimativa_horas'),
                horas_registradas=Sum('horas_registradas')
            )

            dados_projeto = ProjetoSerializer(projeto).data
            dados_projeto['totalizador_status'] = list(totalizadores)
            dados_projeto['tarefas'] = TarefaSerializer(tarefas_do_ano, many=True).data

            resultado_projetos.append(dados_projeto)

        return Response({
            "ano": ano,
            "total_projetos": len(resultado_projetos),
            "projetos": resultado_projetos
        }, status=status.HTTP_200_OK)
    