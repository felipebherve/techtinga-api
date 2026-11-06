# TechTinga — API REST de Projetos e Tarefas (desafio final)

🇧🇷 Português · 🇺🇸 [English](README.md)

🔗 **Portfólio:** este e os meus outros projetos em [felipebherve.github.io](https://felipebherve.github.io/#projects).

## Em que momento eu fiz isto

Este foi o **desafio final** do curso de backend do IFRS + Instituto Hardware (agosto de 2026). As anotações de aula me ensinaram as peças uma a uma (models, managers, serializers, URLs, views); o desafio pedia que eu juntasse todas em um projeto que eu ainda não tinha visto, a partir de um enunciado escrito sobre uma empresa de software fictícia, a **TechTinga**.

O enunciado descreve uma empresa que gerencia **projetos** de software e suas **tarefas**. Eu tinha que modelar os dados com as regras do texto, expor tudo como uma API REST, importar um arquivo CSV em lote e gerar um relatório anual.

## O que ele faz

- **Projetos** com código, nome, tipo (web, mobile, desktop, API, ciência de dados, IA…), cliente, gerente, datas de início / previsão de término / fim, orçamento e indicador de ativo.
- **Tarefas** ligadas a um projeto: título, descrição, linguagem de programação, horas estimadas, horas registradas, status, responsável, datas de criação e conclusão.
- **Validação** seguindo o enunciado (por exemplo: horas não podem ser negativas e a data de conclusão não pode ser anterior à de criação).
- **CRUD** de projetos e as consultas abaixo, tudo retornando JSON. O CRUD de projetos é protegido com autenticação por token e com as permissões padrão do Django.
- **Importação em lote** de CSV com um comando de gerenciamento do Django.

### Endpoints

Caminho base: `/api/`

| Método e rota | O que faz |
|---------------|-----------|
| `POST /token/` | Recebe `username` e `password` e devolve o token de acesso |
| `/projetos/`, `/projetos/<id>/` | Criar, listar, ler, atualizar e excluir projetos (exige token) |
| `/projetos/por-linguagem/?inicio=&fim=&linguagem=` | Projetos filtrados por período e linguagem de programação |
| `/projetos/<id>/tarefas/` | Tarefas de um projeto |
| `/tarefas/colaborador/?responsavel=` | Tarefas de um colaborador |
| `/relatorio/ano/?ano=2026` | Relatório de projetos e tarefas de um ano (o parâmetro `ano` é obrigatório) |

As consultas aceitam só `GET` e respondem `400` quando um parâmetro é inválido (por exemplo, uma linguagem que não existe ou um período com o fim antes do início).

### Login por token

O CRUD de projetos exige um token e as permissões padrão do Django (`add_projeto`, `change_projeto` e `delete_projeto`). Um superusuário já tem todas.

```bash
python manage.py createsuperuser

# 1. Pegar o token
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=admin&password=SUA_SENHA"
# resposta: {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}

# 2. Usar o token
curl http://127.0.0.1:8000/api/projetos/ -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

Sem token a API responde `401`. Com token, mas sem a permissão necessária, responde `403`.

### Importar o CSV

```bash
python manage.py importar_csv                 # lê o techtinga.csv incluído
python manage.py importar_csv --csv outro.csv # ou outro arquivo
```

O comando lê o CSV, valida linha por linha, informa as linhas que não conseguiu importar e salva o resto, ligando cada tarefa ao seu projeto.

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
pip install -r requirements.txt
python manage.py migrate
python manage.py importar_csv
python manage.py runserver
```

Para rodar os testes automatizados:

```bash
python manage.py test gestao
```

Depois abra `http://127.0.0.1:8000/api/relatorio/ano/?ano=2026` para ver o relatório anual. Usa SQLite e configurações de desenvolvimento (`DEBUG = True`), então serve só para estudo local.

## O que aprendi

Modelar duas entidades relacionadas com restrições, mover consultas para managers personalizados, serializers e validação no Django REST Framework, views baseadas em classe, leitura e validação de CSV, e transformar um enunciado de negócio escrito em código funcionando.

## Limitações conhecidas

Listo de propósito: é um projeto de aprendizado e sei o que ainda está em aberto.

- **A importação descarta cerca de 40% do arquivo de exemplo, de propósito.** No `techtinga.csv` incluído (1.100 linhas), 658 tarefas são salvas e 435 são descartadas. A maioria pertence a projetos inativos ou finalizados (o enunciado proíbe tarefas nesses projetos); o resto traz valores fora das regras, como linguagem `RUBY`, status `FINISHED`, prioridade 0 ou 9, horas negativas e campos obrigatórios vazios. O motivo de cada linha descartada aparece no terminal.
- O relatório anual ainda não segue exatamente o formato do JSON de exemplo do enunciado.

## Próximos passos

- Deixar o relatório anual no formato do JSON de exemplo (resumo por status com quantidade, horas e tarefas).
- Gravar as linhas descartadas da importação em um arquivo.
- Adicionar paginação e filtros nos endpoints de listagem.
- Documentação interativa da API (OpenAPI).

> A `SECRET_KEY` do Django é lida da variável de ambiente `DJANGO_SECRET_KEY`. Se ela não estiver definida, é usada uma chave de desenvolvimento insegura, então nunca publique este projeto em produção como está.
