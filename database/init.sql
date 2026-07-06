-- InsightAgent SaaS analytics schema
-- Runs once when the PostgreSQL container is first created.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Migration tracking
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS schema_migrations (
    id          SERIAL PRIMARY KEY,
    version     VARCHAR(64) NOT NULL UNIQUE,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- companies
-- ---------------------------------------------------------------------------

CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    industry        VARCHAR(100) NOT NULL,
    country         VARCHAR(2)   NOT NULL,
    employee_count  INTEGER      NOT NULL CHECK (employee_count > 0),
    website         VARCHAR(255),
    status          VARCHAR(20)  NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'churned', 'trial')),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_companies_status ON companies (status);
CREATE INDEX idx_companies_country ON companies (country);
CREATE INDEX idx_companies_industry ON companies (industry);

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id  UUID         NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    full_name   VARCHAR(255) NOT NULL,
    role        VARCHAR(30)  NOT NULL
                    CHECK (role IN ('admin', 'analyst', 'viewer', 'billing')),
    country     VARCHAR(2)   NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_company_id ON users (company_id);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_is_active ON users (is_active);

-- ---------------------------------------------------------------------------
-- subscriptions
-- ---------------------------------------------------------------------------

CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id      UUID          NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    plan            VARCHAR(20)   NOT NULL
                        CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
    status          VARCHAR(20)   NOT NULL
                        CHECK (status IN ('active', 'trial', 'cancelled', 'past_due')),
    monthly_price   NUMERIC(10, 2) NOT NULL CHECK (monthly_price >= 0),
    billing_cycle   VARCHAR(10)   NOT NULL DEFAULT 'monthly'
                        CHECK (billing_cycle IN ('monthly', 'annual')),
    started_at      TIMESTAMPTZ   NOT NULL,
    trial_ends_at   TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT subscriptions_cancelled_check CHECK (
        (status = 'cancelled' AND cancelled_at IS NOT NULL)
        OR (status <> 'cancelled')
    )
);

CREATE INDEX idx_subscriptions_company_id ON subscriptions (company_id);
CREATE INDEX idx_subscriptions_plan ON subscriptions (plan);
CREATE INDEX idx_subscriptions_status ON subscriptions (status);
CREATE INDEX idx_subscriptions_started_at ON subscriptions (started_at);

-- ---------------------------------------------------------------------------
-- payments
-- ---------------------------------------------------------------------------

CREATE TABLE payments (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id       UUID           NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    subscription_id  UUID           NOT NULL REFERENCES subscriptions (id) ON DELETE CASCADE,
    amount           NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    currency         VARCHAR(3)     NOT NULL DEFAULT 'USD',
    status           VARCHAR(20)    NOT NULL
                         CHECK (status IN ('succeeded', 'failed', 'refunded')),
    payment_method   VARCHAR(30)    NOT NULL
                         CHECK (payment_method IN ('credit_card', 'bank_transfer', 'invoice')),
    paid_at          TIMESTAMPTZ    NOT NULL,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_company_id ON payments (company_id);
CREATE INDEX idx_payments_subscription_id ON payments (subscription_id);
CREATE INDEX idx_payments_paid_at ON payments (paid_at);
CREATE INDEX idx_payments_status ON payments (status);

-- ---------------------------------------------------------------------------
-- feature_usage
-- ---------------------------------------------------------------------------

CREATE TABLE feature_usage (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    company_id       UUID         NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    feature_name     VARCHAR(100) NOT NULL,
    usage_count      INTEGER      NOT NULL DEFAULT 1 CHECK (usage_count > 0),
    duration_minutes INTEGER      NOT NULL DEFAULT 0 CHECK (duration_minutes >= 0),
    used_at          TIMESTAMPTZ  NOT NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feature_usage_company_id ON feature_usage (company_id);
CREATE INDEX idx_feature_usage_user_id ON feature_usage (user_id);
CREATE INDEX idx_feature_usage_feature_name ON feature_usage (feature_name);
CREATE INDEX idx_feature_usage_used_at ON feature_usage (used_at);
CREATE INDEX idx_feature_usage_company_feature ON feature_usage (company_id, feature_name);

-- ---------------------------------------------------------------------------
-- support_tickets
-- ---------------------------------------------------------------------------

CREATE TABLE support_tickets (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id   UUID         NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    user_id      UUID         REFERENCES users (id) ON DELETE SET NULL,
    subject      VARCHAR(500) NOT NULL,
    category     VARCHAR(30)  NOT NULL
                     CHECK (category IN (
                         'billing', 'bug', 'feature_request',
                         'onboarding', 'churn_risk', 'integration'
                     )),
    status       VARCHAR(20)  NOT NULL DEFAULT 'open'
                     CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority     VARCHAR(10)  NOT NULL DEFAULT 'medium'
                     CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ
);

CREATE INDEX idx_support_tickets_company_id ON support_tickets (company_id);
CREATE INDEX idx_support_tickets_user_id ON support_tickets (user_id);
CREATE INDEX idx_support_tickets_category ON support_tickets (category);
CREATE INDEX idx_support_tickets_status ON support_tickets (status);
CREATE INDEX idx_support_tickets_created_at ON support_tickets (created_at);

-- ---------------------------------------------------------------------------
-- login_events
-- ---------------------------------------------------------------------------

CREATE TABLE login_events (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    company_id   UUID        NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    logged_in_at TIMESTAMPTZ NOT NULL,
    ip_country   VARCHAR(2),
    device_type  VARCHAR(20) CHECK (device_type IN ('desktop', 'mobile', 'tablet')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_login_events_user_id ON login_events (user_id);
CREATE INDEX idx_login_events_company_id ON login_events (company_id);
CREATE INDEX idx_login_events_logged_in_at ON login_events (logged_in_at);
CREATE INDEX idx_login_events_user_logged_in ON login_events (user_id, logged_in_at DESC);

INSERT INTO schema_migrations (version)
VALUES ('0002_saas_analytics_schema')
ON CONFLICT (version) DO NOTHING;
