from django.db import models

class TipoProjeto(models.TextChoices):
    WEB = 'WEB', 'Web'
    MOBILE = 'MOBILE', 'Mobile'
    DESKTOP = 'DESKTOP', 'Desktop'
    API = 'API', 'API'
    LIBRARY = 'LIBRARY', 'Library'
    DATA_SCIENCE = 'DATA_SCIENCE', 'Data Science'
    AI = 'AI', 'Inteligência Artificial'