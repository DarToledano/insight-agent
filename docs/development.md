# Development Setup

## Environment Variables

Copy `.env.example` to `.env` and adjust values as needed. See `.env.example` for the full list.

## Docker Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| `db` | insightagent-db | 5432 | PostgreSQL with init/seed scripts |
| `backend` | insightagent-backend | 8000 | FastAPI with hot reload |
| `frontend` | insightagent-frontend | 5173 | Vite dev server with HMR |

## Useful Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d

# View logs
docker compose logs -f backend

# Stop and remove containers
docker compose down

# Reset database (removes volume)
docker compose down -v
```

## Backend Dependencies

See `backend/requirements.txt`. Key packages:

- **fastapi** / **uvicorn** — web framework and ASGI server
- **sqlalchemy** / **psycopg** — ORM and PostgreSQL driver
- **pydantic-settings** — typed environment configuration
- **openai** — reserved for AI integration (not yet used)

## Frontend Dependencies

See `frontend/package.json`. Key packages:

- **react** / **react-dom** — UI framework
- **recharts** — chart library (reserved for analytics views)
- **vite** — build tool and dev server
