# InsightAgent

InsightAgent is an AI data analyst that lets users ask business questions in natural language. It generates read-only PostgreSQL queries, executes them safely, summarizes the results with a second LLM call, and presents answers, tables, charts, and debug SQL through a React dashboard.

## Main Features

### Backend

- **`POST /ask`** — End-to-end pipeline: metadata selection → SQL generation (LLM) → validation → execution → insight generation → chart selection
- **Metadata engine** — Profiles the database at startup (column types, categorical values, numeric/date ranges) and selects relevant tables per question
- **Chart selection** — Rule-based `ChartSelector` returns bar, line, pie, KPI, or `none` in the `/ask` response
- **`POST /generate-sql`** — Debug-only SQL generation (no validation or execution)
- **`GET /schema`** — Raw schema introspection (tables and columns)
- **`GET /metadata`** / **`POST /metadata/refresh`** — Read or rebuild the metadata cache
- **`GET /health`** / **`GET /db-health`** — API and database health checks
- **SQL safety** — Read-only query validation before execution

### Frontend

- Dashboard UI with collapsible sidebar, dark/light theme, and example questions
- Chat-style question input connected to `POST /ask`
- Displays AI answer, dynamic results table, query metadata, and collapsible generated SQL
- Automatic chart rendering (Recharts): bar, line, pie, and KPI views driven by backend `chart` config

### Database

- PostgreSQL 16 with a SaaS analytics schema (7 business tables + seed data)
- Optional **pgAdmin** service for database inspection

## Tech Stack

| Layer | Technology | Version (from project files) |
|-------|------------|------------------------------|
| Backend runtime | Python | 3.12 (`backend/Dockerfile`) |
| API | FastAPI | 0.115.6 |
| ASGI server | Uvicorn | 0.34.0 |
| ORM / DB driver | SQLAlchemy, psycopg | 2.0.36, 3.2.3 |
| Validation / config | Pydantic, pydantic-settings | 2.10.3, 2.6.1 |
| AI | OpenAI Python SDK | 1.57.4 |
| Database | PostgreSQL | 16-alpine |
| Frontend runtime | Node.js | 22 (`frontend/Dockerfile`) |
| UI | React, TypeScript | 19.x, ~5.6 |
| Build tool | Vite | 6.0.5 |
| Charts / icons | Recharts, lucide-react | 2.15.0, 0.469.0 |
| Testing | pytest, Vitest | 8.3.4, 2.1.8 |
| Containers | Docker, Docker Compose | — |

## Project Structure

```
insight-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point, CORS, metadata cache startup
│   │   ├── api/                 # Route handlers (ask, health, schema, metadata, generate-sql)
│   │   ├── core/                # Settings (config.py) and database session
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Pipeline logic (SQL gen, execution, insights, charts, metadata)
│   │   ├── models/              # SQLAlchemy base (minimal ORM usage)
│   │   └── utils/               # SQL cleaning and validation helpers
│   ├── tests/                   # pytest suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main page orchestration
│   │   ├── components/          # UI (forms, tables, charts, layout, SQL viewer)
│   │   ├── services/api.ts      # HTTP client for POST /ask
│   │   ├── types/               # TypeScript API interfaces
│   │   ├── hooks/               # Theme toggle
│   │   ├── styles/              # Global CSS variables and base styles
│   │   └── utils/               # Cell formatting, chart row conversion
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── database/
│   ├── init.sql                 # Schema (companies, users, subscriptions, payments, …)
│   └── seed.sql                 # Sample analytics data
├── docs/                        # Additional architecture and development notes
├── docker-compose.yml           # db, backend, frontend, pgadmin services
├── .env.example                 # Root environment template
└── README.md
```

### Database tables

The sample schema includes: `companies`, `users`, `subscriptions`, `payments`, `feature_usage`, `support_tickets`, and `login_events`.

## Prerequisites

- **Docker** and **Docker Compose** (recommended for full stack)
- **OpenAI API key** (required for `POST /ask` and `POST /generate-sql`)
- For local development outside Docker:
  - Python **3.12**
  - Node.js **22+**
  - PostgreSQL **16** (or run only the `db` service via Docker)

No XML configuration files are used by this project.

## Quick Start (Docker)

1. Copy the environment template and set your OpenAI key:

   ```bash
   cp .env.example .env
   ```

   Edit `.env`:

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

2. Start all services:

   ```bash
   docker compose up --build
   ```

3. Open the application:

   | Service | URL |
   |---------|-----|
   | Frontend | http://localhost:5173 |
   | Backend API docs | http://localhost:8000/docs |
   | Health check | http://localhost:8000/health |
   | pgAdmin | http://localhost:5050 |

   Default pgAdmin login (from `.env.example`): `admin@example.com` / `admin`

## Local Development (without full Docker stack)

### Database only

```bash
docker compose up db
```

Schema and seed data apply automatically on first container start via `database/init.sql` and `database/seed.sql`.

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend reads configuration from the root `.env` file (`backend/app/core/config.py`). Set `DATABASE_URL` to point at your PostgreSQL instance when not using Docker networking.

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` from `frontend/.env` (default `http://localhost:8000`).

When running the frontend on a different origin, set `CORS_ORIGINS` in the root `.env` so the backend accepts browser requests (default `http://localhost:5173`).

## Configuration

### Root `.env` (backend + Docker Compose)

Copy from `.env.example`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (for `/ask`, `/generate-sql`) | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4.1-mini` | Chat model for SQL and insight generation |
| `DATABASE_URL` | No* | `postgresql+psycopg://insight:insight@db:5432/insightagent` | PostgreSQL connection string (*Docker overrides host to `db`) |
| `POSTGRES_USER` | No | `insight` | Database user |
| `POSTGRES_PASSWORD` | No | `insight` | Database password |
| `POSTGRES_DB` | No | `insightagent` | Database name |
| `POSTGRES_PORT` | No | `5432` | Host port for PostgreSQL |
| `BACKEND_PORT` | No | `8000` | Host port for FastAPI |
| `FRONTEND_PORT` | No | `5173` | Host port for Vite dev server |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Backend URL injected into frontend container |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated allowed browser origins |
| `DEBUG` | No | `false` (Docker), `true` (.env.example) | Backend debug logging |
| `METADATA_LOW_CARDINALITY_THRESHOLD` | No | `20` | Max distinct values to profile as categorical |
| `INSIGHT_MAX_ROWS` | No | `50` | Max result rows sent to the insight LLM |
| `PGADMIN_DEFAULT_EMAIL` | No | `admin@example.com` | pgAdmin login email |
| `PGADMIN_DEFAULT_PASSWORD` | No | `admin` | pgAdmin login password |
| `PGADMIN_PORT` | No | `5050` | Host port for pgAdmin |

Get an OpenAI API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### Frontend `frontend/.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL for API requests |

## Usage

### Web UI

1. Open http://localhost:5173
2. Enter a question or click an example, e.g. **Which companies have the highest revenue?**
3. Click **Ask**
4. Review the AI insight, results table, chart (when applicable), metadata, and optional SQL

### API example

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Show total revenue by subscription plan\"}"
```

Example response shape:

```json
{
  "answer": "...",
  "table": {
    "columns": ["subscription_plan", "total_revenue"],
    "rows": [["enterprise", 131036], ["pro", 4776], ["starter", 196]]
  },
  "chart": {
    "type": "bar",
    "x_key": "subscription_plan",
    "y_key": "total_revenue",
    "title": "Total Revenue by Subscription Plan"
  },
  "metadata": {
    "row_count": 3,
    "execution_time_ms": 42
  },
  "debug": {
    "sql": "SELECT ..."
  }
}
```

## `/ask` Pipeline

1. **Metadata selection** — Relevant tables are chosen from the in-memory metadata cache
2. **SQL generation (LLM #1)** — Question + metadata → PostgreSQL `SELECT`
3. **Validation** — Read-only safety checks
4. **Execution** — Query runs against PostgreSQL
5. **Insight generation (LLM #2)** — Result rows → human-readable `answer`
6. **Chart selection** — Rule-based chart type and axis keys

The insight step receives only executed result rows (up to `INSIGHT_MAX_ROWS`), not the full schema, to reduce hallucinated values.

## Testing

### Backend (pytest)

With Docker:

```bash
docker exec insightagent-backend pytest
```

Locally:

```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend (Vitest)

With Docker:

```bash
docker exec insightagent-frontend npm test
```

Locally:

```bash
cd frontend
npm install
npm test
```

### Build frontend for production

```bash
cd frontend
npm run build
npm run preview
```

## Known Limitations

Verified from the current codebase:

- **Sidebar placeholders** — History, Saved Queries, Analytics, and Settings nav items are UI-only (not wired to backend routes)
- **`POST /generate-sql`** — Debug endpoint; does not validate or execute SQL
- **Chart selection** — Rule-based only; no LLM chart recommendations yet
- **Database migrations** — Schema is applied via `init.sql` on first DB start; no Alembic migration runner (see `docs/architecture.md`)
- **ORM models** — Most data access uses raw SQL execution; SQLAlchemy models are minimal
- **OpenAI dependency** — `/ask` and `/generate-sql` require a valid `OPENAI_API_KEY`; insight failures fall back to a generic answer while still returning table/SQL data

## Additional Documentation

- [`docs/architecture.md`](docs/architecture.md) — High-level architecture notes
- [`docs/development.md`](docs/development.md) — Development conventions

## License

Proprietary — all rights reserved.
