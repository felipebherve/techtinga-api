# TechTinga — Projects & Tasks REST API (final challenge)

🇺🇸 English · 🇧🇷 [Português](README.pt-BR.md)

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
| `/projetos/`, `/projetos/<id>/` | Create, list, read, update and delete projects (requires a token) |
| `/projetos/por-linguagem/?inicio=&fim=&linguagem=` | Projects filtered by period and programming language |
| `/projetos/<id>/tarefas/` | Tasks of one project |
| `/tarefas/colaborador/?responsavel=` | Tasks of one team member |
| `/relatorio/ano/?ano=2026` | Report of projects and tasks for a year (the `ano` parameter is required) |

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

- **Token authentication isn't finished.** `/api/projetos/` uses `TokenAuthentication`, but `rest_framework.authtoken` is not in `INSTALLED_APPS` and there is no login/token endpoint yet, so today that CRUD answers `401`. The other endpoints work without login.
- **The CSV import rejects about half of the sample file.** In the included `techtinga.csv` (1,100 rows), 575 tasks are saved and about 518 are rejected. Some rows belong to inactive or finished projects (the model blocks tasks on those, by design), and some use language values that the enumeration doesn't accept yet (`CPLUSPLUS` and `RUBY`; the enumeration has `CPLUSP` and no Ruby).
- The `--csv` option of the import command isn't wired (the method is named `add_argument` instead of `add_arguments`), so it always reads `techtinga.csv`.
- No automated tests yet (`tests.py` is still the empty Django template).

## Next steps

- Add `rest_framework.authtoken`, a token endpoint and a superuser flow, so the project CRUD can be used.
- Align the language enumeration with the CSV values and report the rejected lines in a file.
- Fix the `--csv` option and write automated tests.
- Add pagination and filtering to the list endpoints.

> The Django `SECRET_KEY` is read from the `DJANGO_SECRET_KEY` environment variable. If it isn't set, an insecure development key is used, so never deploy this project as it is.
