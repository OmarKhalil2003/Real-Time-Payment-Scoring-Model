# Production-Grade Fraud Platform — Architecture

## Overview

End-to-end data engineering platform for real-time payment fraud detection.

```text
Payment Generator (producer/)
        │
        ▼
   Apache Kafka  (payments | refunds | alerts)
        │
   ┌────┴────────────────────────────┐
   ▼                                 ▼
Spark Structured Streaming      Fraud Scoring App
(validate, dedup, enrich)       (ML + MCP + velocity)
   │                                 │
   ├─► MinIO Lake (raw/processed/curated)
   └─► PostgreSQL (operational)      └─► scored_transactions
                │
                ▼
          Apache Airflow
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
      dbt    Great    XGBoost
             Expectations  retrain
                │
                ▼
        Star Schema Warehouse
                │
        ┌───────┴───────┐
        ▼               ▼
   Streamlit       FastAPI /predict
   Dashboard       Grafana + Prometheus
```

## Components

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Ingestion | Kafka + Python producer | Real-time event streaming |
| Stream Processing | PySpark Structured Streaming | Validation, dedup, lake writes |
| Operational DB | PostgreSQL | OLTP + scored transactions |
| Data Lake | MinIO (S3) + Parquet/Delta | Immutable raw, processed, curated zones |
| Orchestration | Apache Airflow | dbt, validation, training, reporting |
| Transformation | dbt | Staging → intermediate → marts |
| Warehouse | PostgreSQL star schema | DimCustomer, DimMerchant, FactTransactions |
| ML | XGBoost | Fraud probability scoring |
| API | FastAPI | Real-time prediction endpoint |
| Validation | Great Expectations | Data quality checks |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| Dashboard | Streamlit | Analyst fraud console |

## Data Lake Zones

- `raw/payments` — immutable Kafka payloads (Parquet)
- `processed/payments` — validated, deduplicated (Delta, partitioned by year/month/day)
- `curated/payments` — analytics-ready enriched events (Delta)

## Ports

| Service | Port |
|---------|------|
| Streamlit Dashboard | 8501 |
| FastAPI | 8000 |
| Airflow | 8080 |
| Grafana | 3000 |
| Prometheus | 9090 |
| MinIO Console | 9001 |
| Kafka | 9092 |
| PostgreSQL | 5432 |
