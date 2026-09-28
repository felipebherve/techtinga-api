from rest_framework import serializers
from gestao.models import Projeto

class ProjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = '__all__'