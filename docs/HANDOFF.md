# LUX Handoff Guide

## SCAFFOLD: Initial repo structure, migrations, logging, env config

### REPO + DEPLOY

* Repo: `jaiaFoster/lux-core`
* Branch: `feat/initial-scaffold`
* No Railway deploy — this is structure only

### Structure

```
lux/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
├── core/
│   ├── api/app.py
│   ├── matching/engine.py
│   ├── models/entities.py
│   ├── scoring/engine.py
│   ├── crm/
│   └── db/
├── adapters/
│   └── real_estate/
│       ├── classification/entity_classifier.py
│       ├── ingestion/downloader.py
│       ├── normalization/to_core.py
│       ├── parsing/
│       └── sources/
│           ├── hillsborough.py
│           └── pinellas.py
├── ui/
│   └── src/
└── data/
    ├── raw/
    └── output/
```

### Scaffold Additions

1. `.gitignore` — excludes `.env`, `data/raw/`, `data/output/`
2. `.env.example` — template with DATABASE_URL, Flask, API key placeholders
3. Alembic — initialized at `core/db/migrations/`, `env.py` reads `DATABASE_URL` from environment
4. `core/logger.py` — canonical logger using `get_logger(name)`, replaces all `print()` calls
5. `docs/` — PRD.md, ARCHITECTURE.md (placeholders), HANDOFF.md (this file)
6. `requirements.txt` — added `alembic`
7. All `print()` calls replaced with logger in adapters

### Hard Constraints

* No database models yet — Alembic init only, no migrations
* No UI scaffolding beyond existing empty `ui/src/` folders
* No test files yet — testing structure comes in next handoff
* No Railway deployment
* Do not modify logic in `core/models/entities.py`, `core/scoring/engine.py`, or `core/matching/engine.py`
* `.env` must never be committed — `.env.example` only
* Jaia merges — never self-merge
