-- Operational normalized schema (OLTP)
CREATE SCHEMA IF NOT EXISTS operational;

CREATE TABLE IF NOT EXISTS operational.customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    country TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operational.merchants (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT,
    category TEXT,
    country TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operational.cards (
    card_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES operational.customers(customer_id),
    card_type TEXT,
    last_four TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operational.transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES operational.customers(customer_id),
    merchant_id TEXT REFERENCES operational.merchants(merchant_id),
    card_id TEXT REFERENCES operational.cards(card_id),
    event_type TEXT NOT NULL DEFAULT 'purchase',
    amount DOUBLE PRECISION,
    currency TEXT DEFAULT 'USD',
    payment_method TEXT,
    country TEXT,
    device TEXT,
    ip_address TEXT,
    fraud_label INTEGER DEFAULT 0,
    feature_1 DOUBLE PRECISION,
    feature_2 DOUBLE PRECISION,
    feature_3 DOUBLE PRECISION,
    event_time TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tx_customer_time
    ON operational.transactions (customer_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_tx_merchant
    ON operational.transactions (merchant_id);
CREATE INDEX IF NOT EXISTS idx_tx_event_type
    ON operational.transactions (event_type);

CREATE TABLE IF NOT EXISTS operational.fraud_predictions (
    prediction_id SERIAL PRIMARY KEY,
    transaction_id TEXT NOT NULL UNIQUE REFERENCES operational.transactions(transaction_id),
    score DOUBLE PRECISION NOT NULL,
    prediction INTEGER NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    model_version TEXT,
    confidence DOUBLE PRECISION,
    mcp_risk_score DOUBLE PRECISION,
    triggered_rules TEXT,
    explanation TEXT,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fraud_status ON operational.fraud_predictions (status);
CREATE INDEX IF NOT EXISTS idx_fraud_score ON operational.fraud_predictions (score DESC);

-- Legacy table used by existing scoring consumer + dashboard
CREATE TABLE IF NOT EXISTS scored_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    customer_id VARCHAR(100) NOT NULL,
    amount FLOAT,
    country VARCHAR(50),
    score FLOAT NOT NULL,
    prediction INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    reason VARCHAR(100),
    mcp_risk_score FLOAT,
    triggered_rules VARCHAR(500),
    explanation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_created ON scored_transactions (customer_id, created_at);
CREATE INDEX IF NOT EXISTS idx_status ON scored_transactions (status);

-- Spark streaming sink (backward compatible)
CREATE TABLE IF NOT EXISTS operational_transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    amount DOUBLE PRECISION,
    country TEXT,
    feature_1 DOUBLE PRECISION,
    feature_2 DOUBLE PRECISION,
    feature_3 DOUBLE PRECISION,
    event_time TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_operational_customer_time
    ON operational_transactions (customer_id, event_time DESC);
