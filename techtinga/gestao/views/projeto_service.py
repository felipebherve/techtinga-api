from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from gestao.models import Projeto
from gestao.serializers import ProjetoSerializer

class ProjetoService(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Projeto.objects.get(pk=pk)
        except Projeto.DoesNotExist:
            return None

    def get(self, request, pk=None):
        """
        Exibe todos os registros (se pk for None) ou exibe um registro específico (se passar pk).
        """
        if pk:
            projeto = self.get_object(pk)
            if not projeto:
                return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProjetoSerializer(projeto)
            return Response(serializer.data)
        
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Criar um novo projeto"""
        serializer = ProjetoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """Atualizar um registro existente"""
        if not pk:
            return Response({"error": "Informe o ID do projeto para atualização."}, status=status.HTTP_400_BAD_REQUEST)
        
        projeto = self.get_object(pk)
        if not projeto:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjetoSerializer(projeto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """Deletar um registro"""
        if not pk:
            return Response({"error": "Informe o ID do projeto para exclusão."}, status=status.HTTP_400_BAD_REQUEST)
        
        projeto = self.get_object(pk)
        if not projeto:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        projeto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)