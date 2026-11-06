from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from gestao.models import Projeto
from gestao.serializers import ProjetoSerializer

class ProjetoService(APIView):
    """
    CRUD de projetos. Exige token (cabeçalho Authorization: Token <chave>)
    e as permissões padrão do Django para o modelo Projeto
    (add_projeto, change_projeto e delete_projeto).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Projeto.objects.all()

    def salvar(self, serializer, status_sucesso=status.HTTP_200_OK):
        """Salva o serializer e transforma erros de validação do model em 400."""
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, 'error_dict') else {'erro': erro.messages}
            return Response(detalhes, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status_sucesso)

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
        return self.salvar(serializer, status.HTTP_201_CREATED)

    def put(self, request, pk=None, parcial=False):
        """Atualizar um registro existente (PUT completo ou PATCH parcial)"""
        if not pk:
            return Response({"error": "Informe o ID do projeto para atualização."}, status=status.HTTP_400_BAD_REQUEST)
        
        projeto = self.get_object(pk)
        if not projeto:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjetoSerializer(projeto, data=request.data, partial=parcial)
        return self.salvar(serializer)

    def patch(self, request, pk=None):
        """Atualizar só os campos enviados"""
        return self.put(request, pk, parcial=True)

    def delete(self, request, pk=None):
        """Deletar um registro"""
        if not pk:
            return Response({"error": "Informe o ID do projeto para exclusão."}, status=status.HTTP_400_BAD_REQUEST)
        
        projeto = self.get_object(pk)
        if not projeto:
            return Response({"error": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        projeto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)