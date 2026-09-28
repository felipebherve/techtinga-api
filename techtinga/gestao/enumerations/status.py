from django.db import models


class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pendente'
    DOING = 'DOING', 'Em andamento'
    DONE = 'DONE', 'Concluída'
    BLOCKED = 'BLOCKED', 'Bloqueada'
    DELAYED = 'DELAYED', 'Atrasada'