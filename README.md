# TechTinga — Projects & Tasks REST API (final challenge)

🇺🇸 English · 🇧🇷 [Português](README.pt-BR.md)

🔗 **Portfolio:** this project and my others at [felipebherve.github.io](https://felipebherve.github.io/#projects).

## Where I was when I made this

This was the **final challenge** of the IFRS + Instituto Hardware backend course (August 2026). The class notes taught me the pieces one at a time (models, managers, serializers, URLs, views); the challenge asked me to put all of them together in a project I had not seen before, from a written brief about a fictional software company, **TechTinga**.

The brief describes a company that manages software **projects** and their **tasks**. I had to model the data with the rules from the text, expose it as a REST API, import a CSV file in bulk and produce a yearly report.

## What it does

- **Projects** with code, name, type (web, mobile, API, data science, AI…), client, manager, start / expected end / end dates, budget and active flag.
- **Tasks** linked to a project: title, description, programming language, estimated hours, logged hours, status, owner, creation and completion dates.
- **Validation** following the brief (for example: hours can't be negative and the completion date can't be earlier than the creation date).
- **CRUD** for projects and the queries below, all returning JSON. The project CRUD is protected with token authentication (see *Known limitations*).
- **Bulk import** from CSV with a Django management command.

### Endpoints

Base path: `/api/`

| Method and route | What it does |
|------------------|--------------|
| `POST /token/` | Returns the login token (send `username` and `password`) |
| `/projetos/`, `/projetos/<id>/` | Create, list, read, update and delete projects (requires a token) |
| `/projetos/por-linguagem/?inicio=&fim=&linguagem=` | Projects filtered by period and programming language |
| `/projetos/<id>/tarefas/` | Tasks of one project |
| `/tarefas/colaborador/?responsavel=` | Tasks of one team member |
| `/relatorio/ano/?ano=2026` | Report of projects and tasks for a year (the `ano` parameter is required) |

The query endpoints accept `GET` only (other methods answer `405`) and return `400` when a parameter is invalid, for example a language that doesn't exist or `fim` before `inicio`.

### Use the project CRUD with a token

The CRUD uses `TokenAuthentication` and Django's default permissions (`DjangoModelPermissions`): to create, update or delete, the user needs the `add`, `change` or `delete` permission on Projeto (a superuser has all of them).

```bash
python manage.py createsuperuser
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=admin" -d "password=YOUR_PASSWORD"
# {"token": "abc123..."}
curl http://127.0.0.1:8000/api/projetos/ -H "Authorization: Token abc123..."
```

### Import the CSV

```bash
python manage.py importar_csv
```

The command reads `techtinga.csv` (included), validates it line by line, reports the lines it couldn't import and saves the rest, linking each task to its project.

## Structure

```
techtinga/
├── manage.py
├── techtinga/            # project settings and root URLs
└── gestao/               # the app
    ├── models/           # Projeto, Tarefa (with a shared BaseModel)
    ├── enumerations/     # language, status and project type choices
    ├── managers/         # reusable queries (active, late, by year, by language…)
    ├── serializers/
    ├── views/            # API views and the report
    └── management/commands/importar_csv.py
```

The structure follows the order from the last class: **model → manager → serializer → URL → helper classes → view**.

## Run it

```bash
cd techtinga
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install django djangorestframework
python manage.py migrate
python manage.py importar_csv
python manage.py runserver
```

Then open `http://127.0.0.1:8000/api/relatorio/ano/?ano=2026` to see the yearly report. It uses SQLite and development settings (`DEBUG = True`), so it is for local study only.

## What I learned

Modeling two related entities with constraints, moving queries into custom managers, serializers and validation in Django REST Framework, class-based API views, reading and validating a CSV, and turning a written business brief into working code.

## Known limitations

I'm listing them on purpose: this is a learning project and I know what is still open.

- **The CSV import rejects part of the sample file.** In the included `techtinga.csv` (1,100 rows), 658 tasks are saved and 435 are rejected. Some rows belong to inactive or finished projects (the model blocks tasks on those, by design), and others carry invalid values on purpose (language `RUBY`, status `FINISHED`, priority outside 1 to 5, negative hours).
- The `--csv` option of the import command isn't wired (the method is named `add_argument` instead of `add_arguments`), so it always reads `techtinga.csv`.
- The automated tests only cover the managers, the token, the project CRUD and the queries so far (`python manage.py test gestao`).

## Next steps

- Report the rejected import lines in a file.
- Fix the `--csv` option and extend the automated tests.
- Add pagination and filtering to the list endpoints.

> The Django `SECRET_KEY` is read from the `DJANGO_SECRET_KEY` environment variable. If it isn't set, an insecure development key is used, so never deploy this project as it is.
