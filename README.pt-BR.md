# TechTinga — API REST de Projetos e Tarefas (desafio final)

🇧🇷 Português · 🇺🇸 [English](README.md)

## Em que momento eu fiz isto

Este foi o **desafio final** do curso de backend do IFRS + Instituto Hardware (agosto de 2026). As anotações de aula me ensinaram as peças uma a uma (models, managers, serializers, URLs, views); o desafio pedia que eu juntasse todas em um projeto que eu ainda não tinha visto, a partir de um enunciado escrito sobre uma empresa de software fictícia, a **TechTinga**.

O enunciado descreve uma empresa que gerencia **projetos** de software e suas **tarefas**. Eu tinha que modelar os dados com as regras do texto, expor tudo como uma API REST, importar um arquivo CSV em lote e gerar um relatório anual.

## O que ele faz

- **Projetos** com código, nome, tipo (web, mobile, API, ciência de dados, IA…), cliente, gerente, datas de início / previsão de término / fim, orçamento e indicador de ativo.
- **Tarefas** ligadas a um projeto: título, descrição, linguagem de programação, horas estimadas, horas registradas, status, responsável, datas de criação e conclusão.
- **Validação** seguindo o enunciado (por exemplo: horas não podem ser negativas e a data de conclusão não pode ser anterior à de criação).
- **CRUD** de projetos e as consultas abaixo, tudo retornando JSON. O CRUD de projetos é protegido com autenticação por token (veja *Limitações conhecidas*).
- **Importação em lote** de CSV com um comando de gerenciamento do Django.

### Endpoints

Caminho base: `/api/`

| Método e rota | O que faz |
|---------------|-----------|
| `/projetos/`, `/projetos/<id>/` | Criar, listar, ler, atualizar e excluir projetos (exige token) |
| `/projetos/por-linguagem/?inicio=&fim=&linguagem=` | Projetos filtrados por período e linguagem de programação |
| `/projetos/<id>/tarefas/` | Tarefas de um projeto |
| `/tarefas/colaborador/?responsavel=` | Tarefas de um colaborador |
| `/relatorio/ano/?ano=2026` | Relatório de projetos e tarefas de um ano (o parâmetro `ano` é obrigatório) |

### Importar o CSV

```bash
python manage.py importar_csv
```

O comando lê o `techtinga.csv` (incluído), valida linha por linha, informa as linhas que não conseguiu importar e salva o resto, ligando cada tarefa ao seu projeto.

## Estrutura

```
techtinga/
├── manage.py
├── techtinga/            # configurações do projeto e URLs principais
└── gestao/               # o app
    ├── models/           # Projeto, Tarefa (com um BaseModel compartilhado)
    ├── enumerations/     # opções de linguagem, status e tipo de projeto
    ├── managers/         # consultas reutilizáveis (ativos, atrasadas, por ano, por linguagem…)
    ├── serializers/
    ├── views/            # views da API e o relatório
    └── management/commands/importar_csv.py
```

A estrutura segue a ordem da última aula: **model → manager → serializer → URL → classes auxiliares → view**.

## Como rodar

```bash
cd techtinga
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install django djangorestframework
python manage.py migrate
python manage.py importar_csv
python manage.py runserver
```

Depois abra `http://127.0.0.1:8000/api/relatorio/ano/?ano=2026` para ver o relatório anual. Usa SQLite e configurações de desenvolvimento (`DEBUG = True`), então serve só para estudo local.

## O que aprendi

Modelar duas entidades relacionadas com restrições, mover consultas para managers personalizados, serializers e validação no Django REST Framework, views baseadas em classe, leitura e validação de CSV, e transformar um enunciado de negócio escrito em código funcionando.

## Limitações conhecidas

Listo de propósito: é um projeto de aprendizado e sei o que ainda está em aberto.

- **A autenticação por token não está terminada.** O `/api/projetos/` usa `TokenAuthentication`, mas o `rest_framework.authtoken` não está em `INSTALLED_APPS` e ainda não há endpoint de login/token, então hoje esse CRUD responde `401`. Os outros endpoints funcionam sem login.
- **A importação do CSV rejeita cerca de metade do arquivo de exemplo.** No `techtinga.csv` incluído (1.100 linhas), 575 tarefas são salvas e cerca de 518 são rejeitadas. Algumas linhas pertencem a projetos inativos ou finalizados (o model bloqueia tarefas nesses casos, de propósito) e outras usam valores de linguagem que a enumeração ainda não aceita (`CPLUSPLUS` e `RUBY`; a enumeração tem `CPLUSP` e não tem Ruby).
- A opção `--csv` do comando de importação não está ligada (o método se chama `add_argument` em vez de `add_arguments`), então ele sempre lê o `techtinga.csv`.
- Ainda não há testes automatizados (`tests.py` é o modelo vazio do Django).

## Próximos passos

- Adicionar `rest_framework.authtoken`, um endpoint de token e um fluxo de superusuário, para o CRUD de projetos poder ser usado.
- Alinhar a enumeração de linguagens com os valores do CSV e registrar as linhas rejeitadas em um arquivo.
- Corrigir a opção `--csv` e escrever testes automatizados.
- Adicionar paginação e filtros nos endpoints de listagem.

> A `SECRET_KEY` do Django é lida da variável de ambiente `DJANGO_SECRET_KEY`. Se ela não estiver definida, é usada uma chave de desenvolvimento insegura, então nunca publique este projeto em produção como está.
