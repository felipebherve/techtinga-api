from django.db import models

class LinguagemProgramacao(models.TextChoices):
    PYTHON = 'PYTHON', 'Python'
    JS = 'JS', 'JavaScript'
    JAVA = 'JAVA', 'Java'
    CSHARP = 'CSHARP', 'C#'
    CPLUSP = 'CPLUSP', 'C++'
    C = 'C', 'C'
    PHP = 'PHP', 'PHP'
    DART = 'DART', 'Dart'