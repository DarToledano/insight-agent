-- InsightAgent database initialization
-- Runs once when the PostgreSQL container is first created.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Placeholder schema for development; business tables will be added later.

CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(64) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_migrations (version)
VALUES ('0001_initial')
ON CONFLICT (version) DO NOTHING;
