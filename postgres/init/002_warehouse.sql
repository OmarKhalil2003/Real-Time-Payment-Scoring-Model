-- Dimensional warehouse schema (star schema)
CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT,
    country TEXT,
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_merchant (
    merchant_key SERIAL PRIMARY KEY,
    merchant_id TEXT NOT NULL UNIQUE,
    merchant_name TEXT,
    category TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS warehouse.dim_card (
    card_key SERIAL PRIMARY KEY,
    card_id TEXT NOT NULL UNIQUE,
    customer_id TEXT NOT NULL,
    card_type TEXT,
    last_four TEXT
);

CREATE TABLE IF NOT EXISTS warehouse.dim_country (
    country_key SERIAL PRIMARY KEY,
    country_code TEXT NOT NULL UNIQUE,
    country_name TEXT
);

CREATE TABLE IF NOT EXISTS warehouse.dim_time (
    time_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    hour INTEGER NOT NULL DEFAULT 0,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS warehouse.fact_transactions (
    fact_id BIGSERIAL PRIMARY KEY,
    transaction_id TEXT NOT NULL UNIQUE,
    customer_key INTEGER REFERENCES warehouse.dim_customer(customer_key),
    merchant_key INTEGER REFERENCES warehouse.dim_merchant(merchant_key),
    card_key INTEGER REFERENCES warehouse.dim_card(card_key),
    country_key INTEGER REFERENCES warehouse.dim_country(country_key),
    time_key INTEGER REFERENCES warehouse.dim_time(time_key),
    event_type TEXT NOT NULL,
    amount DOUBLE PRECISION,
    currency TEXT,
    payment_method TEXT,
    device TEXT,
    fraud_label INTEGER DEFAULT 0,
    score DOUBLE PRECISION,
    prediction INTEGER,
    status TEXT,
    reason TEXT,
    model_version TEXT,
    is_fraud BOOLEAN DEFAULT FALSE,
    event_time TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_time ON warehouse.fact_transactions (time_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer ON warehouse.fact_transactions (customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_status ON warehouse.fact_transactions (status);
CREATE INDEX IF NOT EXISTS idx_fact_event_type ON warehouse.fact_transactions (event_type);
