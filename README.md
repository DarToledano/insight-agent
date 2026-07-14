# InsightAgent

AI Data Analyst Agent that lets users ask complex business questions in natural language about a PostgreSQL database.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Frontend | React, TypeScript, Vite |
| Charts | Recharts |
| AI | OpenAI API |
| Containers | Docker, Docker Compose |

## Project Structure

```
insight-agent/
├── backend/          # FastAPI application
├── frontend/         # React + TypeScript UI
├── database/         # SQL init and seed scripts
├── docs/             # Architecture and development docs
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) Node.js 22+ and Python 3.12 for local development outside Docker

### Run with Docker

1. Copy the environment template and add your OpenAI API key:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY` (required for `POST /generate-sql`):

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

2. Start all services:

   ```bash
   docker compose up --build
   ```

3. Open the app:

   | Service | URL |
   |---------|-----|
   | Frontend | http://localhost:5173 |
   | Backend API docs | http://localhost:8000/docs |
   | Health check | http://localhost:8000/health |

### Frontend setup

The React UI calls `POST /ask` on the backend and displays the answer, results table, metadata, and generated SQL.

1. Copy the frontend environment template:

   ```bash
   cp frontend/.env.example frontend/.env
   ```

2. Configure the backend URL if needed:

   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. When using Docker Compose, also ensure the backend allows the frontend origin:

   ```
   CORS_ORIGINS=http://localhost:5173
   ```

### Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
npm test
```

The frontend reads `VITE_API_BASE_URL` from `frontend/.env` and sends questions to `POST /ask`.

**Database:** Start PostgreSQL locally or run only the db service:

```bash
docker compose up db
```

## Status

The backend exposes health checks, schema introspection, SQL generation (`POST /generate-sql`, debug only), and the full natural-language analytics pipeline (`POST /ask`).

## InsightAgent `/ask` Pipeline

`POST /ask` runs two separate LLM steps:

1. **SQL generation** — converts the question + database metadata into a read-only PostgreSQL query.
2. **Result interpretation** — converts the executed query results into a concise business answer.

This separation reduces hallucinations: the second LLM call receives **only the rows returned by the database**, not the full schema or raw table contents. It cannot invent values that were not in the query result.

The API still returns the full result table, execution metadata, and debug SQL unchanged. Only the `answer` field adds the human-readable summary.

Configure how many rows are sent to the insight LLM with:

```
INSIGHT_MAX_ROWS=50
```

If a query returns more rows, the insight step summarizes the first `INSIGHT_MAX_ROWS` rows and notes that additional rows are available in the `table` response.

Run backend tests:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## OpenAI Configuration

SQL generation uses the OpenAI Chat Completions API. Configure it in `.env` at the project root:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1-mini
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (for `/ask`, `/generate-sql`) | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4.1-mini` | Chat model used by `LLMService` |
| `INSIGHT_MAX_ROWS` | No | `50` | Max result rows sent to the insight LLM |

**Switch models** — change `OPENAI_MODEL` in `.env` (e.g. `gpt-4.1`, `gpt-4o-mini`) and restart the backend:

```bash
docker compose up -d backend
```

**Local development** — the same `.env` file is read by `backend/app/core/config.py` when running outside Docker.

Get an API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

## Frontend Architecture

The frontend is a single-page React app that:

1. Collects a natural-language question
2. Sends `POST {VITE_API_BASE_URL}/ask`
3. Displays the returned `answer`, dynamic `table`, subtle `metadata`, and collapsible `debug.sql`

### Screenshots

<!-- Add screenshots of the InsightAgent dashboard here -->

## License

Proprietary — all rights reserved.
