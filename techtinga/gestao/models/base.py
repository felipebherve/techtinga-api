from django.db import models

class BaseModel(models.Model):
    """
    Classe base para todos os modelos do sistema.
    """
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = 'gestao'