# TechTinga — Projects & Tasks REST API (final challenge)

🇺🇸 English · 🇧🇷 [Português](README.pt-BR.md)

🔗 **Portfolio:** this project and my others at [felipebherve.github.io](https://felipebherve.github.io/#projects).

## Where I was when I made this

This was the **final challenge** of the IFRS + Instituto Hardware backend course (August 2026). The class notes taught me the pieces one at a time (models, managers, serializers, URLs, views); the challenge asked me to put all of them together in a project I had not seen before, from a written brief about a fictional software company, **TechTinga**.

The brief describes a company that manages software **projects** and their **tasks**. I had to model the data with the rules from the text, expose it as a REST API, import a CSV file in bulk and produce a yearly report.

## What it does

- **Projects** with code, name, type (web, mobile, desktop, API, data science, AI…), client, manager, start / expected end / end dates, budget and active flag.
- **Tasks** linked to a project: title, description, programming language, estimated hours, logged hours, status, owner, creation and completion dates.
- **Validation** following the brief (for example: hours can't be negative and the completion date can't be earlier than the creation date).
- **CRUD** for projects and the queries below, all returning JSON. The project CRUD is protected with token authentication and Django's default model permissions.
- **Bulk import** from CSV with a Django management command.

### Endpoints

Base path: `/api/`

| Method and route | What it does |
|------------------|--------------|
| `POST /token/` | Takes `username` and `password` and returns the access token |
| `/projetos/`, `/projetos/<id>/` | Create, list, read, update and delete projects (requires a token) |
| `/projetos/por-linguagem/?inicio=&fim=&linguagem=` | Projects filtered by period and programming language |
| `/projetos/<id>/tarefas/` | Tasks of one project |
| `/tarefas/colaborador/?responsavel=` | Tasks of one team member |
| `/relatorio/ano/?ano=2026` | Report of projects and tasks for a year (the `ano` parameter is required) |

The queries only accept `GET` and answer `400` when a parameter is invalid (for example, a language that doesn't exist or a period whose end is before its start).

### Token login

The project CRUD requires a token and Django's default permissions (`add_projeto`, `change_projeto` and `delete_projeto`). A superuser already has all of them.

```bash
python manage.py createsuperuser

# 1. Get the token
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=admin&password=YOUR_PASSWORD"
# answer: {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}

# 2. Use the token
curl http://127.0.0.1:8000/api/projetos/ -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

Without a token the API answers `401`. With a token but without the needed permission, it answers `403`.

### Import the CSV

```bash
python manage.py importar_csv                 # reads the included techtinga.csv
python manage.py importar_csv --csv other.csv # or another file
```

The command reads the CSV, validates it line by line, reports the lines it couldn't import and saves the rest, linking each task to its project.

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
pip install -r requirements.txt
python manage.py migrate
python manage.py importar_csv
python manage.py runserver
```

To run the automated tests:

```bash
python manage.py test gestao
```

Then open `http://127.0.0.1:8000/api/relatorio/ano/?ano=2026` to see the yearly report. It uses SQLite and development settings (`DEBUG = True`), so it is for local study only.

## What I learned

Modeling two related entities with constraints, moving queries into custom managers, serializers and validation in Django REST Framework, class-based API views, reading and validating a CSV, and turning a written business brief into working code.

## Known limitations

I'm listing them on purpose: this is a learning project and I know what is still open.

- **The import discards about 40% of the sample file, on purpose.** In the included `techtinga.csv` (1,100 rows), 658 tasks are saved and 435 are discarded. Most belong to inactive or finished projects (the brief forbids tasks on those); the rest carry values outside the rules, such as language `RUBY`, status `FINISHED`, priority 0 or 9, negative hours and empty required fields. The reason for each discarded line is printed in the terminal.
- The yearly report doesn't follow the exact format of the brief's sample JSON yet.

## Next steps

- Make the yearly report match the sample JSON (summary by status with count, hours and tasks).
- Save the discarded import lines to a file.
- Add pagination and filtering to the list endpoints.
- Interactive API documentation (OpenAPI).

> The Django `SECRET_KEY` is read from the `DJANGO_SECRET_KEY` environment variable. If it isn't set, an insecure development key is used, so never deploy this project as it is.
