# school-api

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Docs-OpenAPI%20Swagger-blue)](https://sotonavarrojosue-creator.github.io/school-api/)

FastAPI REST API for school management with Obsidian sync and AI-powered endpoints.

## Features

- **CRUD Operations**: Subjects, tasks, exams with full REST endpoints
- **Obsidian Sync**: Import/export markdown notes with frontmatter
- **AI Endpoints**: Weekly summary, priorities, study recommendations via OpenRouter
- **Remote Access**: Tailscale/ngrok/Cloudflare tunnel script included
- **SQLite**: Zero-config database, easy to backup/migrate

## Quick Start

```bash
# Clone and enter
git clone https://github.com/sotonavarrojosue-creator/school-api.git
cd school-api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values (OPENROUTER_API_KEY required for AI endpoints)

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs at `http://localhost:8000/docs`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No | SQLite by default |
| `OPENROUTER_API_KEY` | **Yes** (for AI) | Get from [openrouter.ai/keys](https://openrouter.ai/keys) |
| `OPENROUTER_MODEL` | No | Default: `openai/gpt-4o-mini` |
| `SYNC_VAULT_PATH` | No | Path to Obsidian vault for sync |
| `CORS_ORIGINS` | No | Comma-separated origins |
| `HOST` / `PORT` | No | Server binding |

## API Endpoints

### Core CRUD
- `GET/POST /materias/` — Subjects
- `GET/POST /tareas/` — Tasks
- `GET/POST /examenes/` — Exams

### AI Endpoints
- `POST /ai/resumen-semana` — Weekly summary
- `POST /ai/prioridades` — Priority suggestions
- `POST /ai/estudio` — Study plan generator

### Obsidian Sync
- `POST /sync/import` — Import .md files from vault
- `POST /sync/export` — Export DB to .md files

## Remote Access

```bash
# Tailscale (recommended)
bash scripts/acceso_remoto.sh tailscale

# ngrok
bash scripts/acceso_remoto.sh ngrok

# Cloudflare Tunnel
bash scripts/acceso_remoto.sh cloudflare
```

## Project Structure

```
school-api/
├── main.py              # FastAPI app + routing
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic v2 schemas
├── database.py          # DB session management
├── requirements.txt
├── .env.example
├── routes/
│   ├── materias.py
│   ├── tareas.py
│   └── examenes.py
├── services/
│   ├── ai_service.py       # OpenRouter integration
│   └── obsidian_sync.py    # Markdown frontmatter sync
└── scripts/
    └── acceso_remoto.sh    # Tailscale/ngrok/Cloudflare
```

## Tech Stack

- **FastAPI** 0.115+ — Modern async Python web framework
- **SQLAlchemy** 2.0 — Async ORM
- **Pydantic** v2 — Data validation
- **OpenRouter** — Multi-model AI access
- **SQLite** — Embedded database

## License

MIT — Use freely for your own school management.
