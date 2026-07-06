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
| AI | OpenAI API (planned) |
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

1. Copy the environment template:

   ```bash
   cp .env.example .env
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
npm install
npm run dev
```

**Database:** Start PostgreSQL locally or run only the db service:

```bash
docker compose up db
```

## Status

This repository contains the project scaffold and development environment only. Business logic, API endpoints, and AI integration will be added in subsequent phases.

## License

Proprietary — all rights reserved.
