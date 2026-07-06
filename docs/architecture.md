# InsightAgent Documentation

## Overview

InsightAgent is an AI-powered data analyst that translates natural-language business questions into SQL queries against a PostgreSQL database, executes them safely, and presents results with charts and narrative insights.

## Architecture (Planned)

```
┌─────────────┐     HTTP      ┌─────────────┐     SQL      ┌─────────────┐
│   React UI  │ ────────────► │   FastAPI   │ ───────────► │ PostgreSQL  │
│  (Vite/TS)  │ ◄──────────── │   Backend   │ ◄─────────── │  Database   │
└─────────────┘               └──────┬──────┘               └─────────────┘
                                   │
                                   │ OpenAI API
                                   ▼
                            ┌─────────────┐
                            │  LLM Agent  │
                            └─────────────┘
```

## Directory Layout

| Path | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application factory and middleware |
| `backend/app/api/` | HTTP route handlers (to be added) |
| `backend/app/services/` | Business logic and AI orchestration |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/app/schemas/` | Pydantic request/response schemas |
| `backend/app/core/` | Configuration, database session |
| `backend/app/utils/` | Shared helpers |
| `frontend/src/` | React components and pages |
| `database/` | Schema initialization and seed data |

## Development Conventions

- **Backend**: Layered architecture — routes call services, services use models/schemas.
- **Frontend**: Component-based React with TypeScript strict mode.
- **Database**: Migrations tracked via `schema_migrations` table until Alembic is introduced.
- **Environment**: All secrets and connection strings live in `.env` (never committed).

## Next Steps

1. Define domain models and seed data for a sample business dataset.
2. Implement query and chat API endpoints.
3. Integrate OpenAI for natural-language-to-SQL generation.
4. Build the chat UI with Recharts visualizations.
