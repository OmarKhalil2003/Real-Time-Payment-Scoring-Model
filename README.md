# Production-Grade Real-Time Payment Analytics & Fraud Detection Platform

A full-stack **Data Engineering + ML** portfolio project simulating a fintech payment infrastructure with real-time streaming, batch processing, data lake, warehouse, orchestration, and monitoring.

## Architecture

```
Producer → Kafka → Spark Streaming → MinIO (raw/processed/curated)
                 ↘ Fraud Scoring App → PostgreSQL
                                           ↓
                                      Airflow → dbt → Star Schema
                                           ↓
                              FastAPI + Streamlit + Grafana
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

## Tech Stack

| Category | Tools |
|----------|-------|
| Streaming | Apache Kafka |
| Stream Processing | PySpark Structured Streaming |
| Database | PostgreSQL |
| Data Lake | MinIO, Parquet, Delta Lake |
| Warehouse | PostgreSQL Star Schema |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| ML | XGBoost |
| API | FastAPI |
| Validation | Great Expectations |
| Monitoring | Prometheus, Grafana |
| Dashboard | Streamlit |
| CI/CD | GitHub Actions |
| Containers | Docker Compose |

## Quick Start

```bash
docker compose up --build -d
```

Wait ~2 minutes for all services to initialize, then open:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Fraud Dashboard** | http://localhost:8501 | — |
| **FastAPI Docs** | http://localhost:8000/docs | — |
| **Airflow** | http://localhost:8080 | admin / admin |
| **Grafana** | http://localhost:3000 | admin / admin |
| **MinIO Console** | http://localhost:9001 | minio / minio12345 |
| **Prometheus** | http://localhost:9090 | — |

## What Runs Automatically

- Kafka topics: `payments`, `refunds`, `alerts` (+ DLQ topics)
- MinIO buckets: `raw`, `processed`, `curated` lake zones
- PostgreSQL schemas: operational OLTP + warehouse star schema
- Payment event generator (purchases, refunds, failed payments, chargebacks)
- Spark Structured Streaming (validate, dedup, watermark, lake writes)
- Real-time fraud scoring (ML + MCP rules + velocity detection)
- XGBoost model auto-training if artifacts missing
- Airflow DAG for dbt, Great Expectations, model retraining

## API Usage

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx-001",
    "customer_id": "CUST_00001",
    "amount": 150.00,
    "country": "Egypt",
    "feature_1": 0.3,
    "feature_2": 0.2,
    "feature_3": 0.1
  }'
```

## dbt (Manual)

```bash
cd dbt
dbt deps --profiles-dir .
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Or trigger the `fraud_platform_pipeline` DAG in Airflow.

## Project Structure

```
producer/          Payment event generator
app/               Fraud scoring consumer + FastAPI
spark/             Structured Streaming jobs
dbt/               Warehouse transformations (staging → marts)
airflow/           Orchestration DAGs
postgres/          Database init scripts
minio/             Lake bucket initialization
ml/                XGBoost model training
great_expectations/ Data validation
monitoring/        Prometheus + Grafana
dashboard.py       Streamlit analyst console
docs/              Architecture documentation
tests/             Unit + integration tests
```

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest -q
```

## Skills Demonstrated

- Python, Advanced SQL, PostgreSQL
- Apache Kafka, PySpark Structured Streaming
- Delta Lake, Parquet, Data Lakes
- Data Warehousing, Star Schema, dbt
- ETL/ELT, Airflow orchestration
- XGBoost ML integration, FastAPI
- Great Expectations data validation
- Prometheus, Grafana monitoring
- Docker, GitHub Actions CI/CD
- Distributed systems, production data engineering

## Author

Omar Khalil — [omark8977@gmail.com](mailto:omark8977@gmail.com)
