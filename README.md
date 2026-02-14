

---

# 💳 Real-Time Payment Fraud Scoring System

A fully containerized, autonomous, real-time fraud detection pipeline built using Kafka, Machine Learning, MySQL, and Streamlit.

This system simulates live payment traffic, applies ML-based fraud scoring combined with rule-based velocity detection, persists results efficiently using batch operations, and exposes real-time operational monitoring via an analyst-oriented dashboard.

---

# 🎯 Objectives

* Real-time transaction ingestion using Kafka
* Machine Learning–based fraud probability scoring
* Rule-based behavioral fraud detection (velocity monitoring)
* High-performance batch persistence into MySQL
* Analyst-ready monitoring dashboard with export capabilities
* Fully containerized, reproducible deployment
* Autonomous startup with zero manual setup

---

# 🏗 System Architecture

```
Docker Compose
│
├── Zookeeper
├── Kafka
│     └── Topic: payments (auto-created)
│
├── MySQL (persistent Docker volume)
│
├── Producer (Dockerized)
│     └── Continuously generates simulated payment transactions
│
├── Consumer App (Dockerized)
│     ├── Auto-trains ML model if not found
│     ├── Applies ML fraud scoring
│     ├── Applies velocity-based fraud rule
│     ├── Classifies status (APPROVED / REVIEW / DECLINED)
│     ├── Stores fraud reason (ML_MODEL / VELOCITY_RULE)
│     ├── Batch inserts scored results
│     ├── Handles Dead Letter Queue (DLQ)
│     └── Enforces idempotency via unique constraints
│
└── Streamlit Dashboard (Dockerized)
      ├── System health panel
      ├── Throughput monitoring
      ├── Fraud source breakdown
      ├── Velocity alert monitoring
      ├── High-risk transaction inspection
      ├── Customer investigation panel
      └── CSV export for analysts
```

---

# ⚙️ Tech Stack

* Python 3.10
* Apache Kafka
* MySQL 8
* SQLAlchemy ORM
* Scikit-learn (RandomForestClassifier)
* Streamlit
* Docker & Docker Compose
* Pytest

---

# 📂 Project Structure

```
app/
  config/
  database/
    connection.py
    models.py
    repository.py
  kafka/
  model/
  services/
    scoring_service.py
  main.py

scripts/
  sample_producer.py
  train_dummy_model.py

tests/
  test_predictor.py
  test_status_logic.py

dashboard.py
docker-compose.yml
Dockerfile
requirements.txt
```

---

# 🚀 Quick Start

Clone the repository and run:

```bash
docker compose up --build -d
```

Or to build and watch logs:
_i recommend using this to watch logs and when the app-1 logs transactions) appear it's time to open the UI_ 

```bash
docker compose up --build
```

Then open:

```
http://localhost:8501
```

No manual setup required:

* No Kafka topic creation
* No manual database schema creation
* No manual model training
* No local virtual environment


---

# 🧠 Autonomous Capabilities

At startup, the system automatically:

* Creates Kafka topic (`payments`)
* Waits for MySQL readiness
* Creates database schema if not present
* Trains ML model if missing
* Starts continuous transaction producer
* Starts fraud scoring consumer
* Applies batch insert optimization
* Launches monitoring dashboard
* Applies retry logic and DLQ handling

---

# 🗄 Updated MySQL Schema

```sql
CREATE TABLE scored_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    customer_id VARCHAR(100) NOT NULL,
    amount FLOAT,
    score FLOAT,
    prediction INT,
    status VARCHAR(20),
    reason VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME NULL,
    
    INDEX idx_customer_created (customer_id, created_at),
    INDEX idx_status (status)
);
```

### Schema Highlights

* `reason` → explains fraud source (`ML_MODEL` / `VELOCITY_RULE`)
* Composite index `(customer_id, created_at)` → optimized for velocity rule
* Indexed `status` → fast dashboard aggregation
* Unique constraint on `transaction_id` → idempotent processing

---

# 📊 Fraud Detection Logic

## 1️⃣ Machine Learning Layer

* RandomForest classifier
* Outputs fraud probability score
* Threshold-based classification:

  * `>= 0.85` → DECLINED
  * `>= 0.65` → REVIEW
  * else → APPROVED

---

## 2️⃣ Velocity Rule Layer

* Counts transactions per customer over last 60 seconds
* Triggers when threshold exceeded (e.g., 12 tx / 60 sec)
* Slightly increases risk score
* Overrides classification when burst activity detected
* Sets `reason = VELOCITY_RULE`

This hybrid architecture balances predictive modeling with behavioral anomaly detection.

---

# 📈 Dashboard Features

## 🔹 System Health

* Lifetime status counters
* Transactions per minute
* Fraud rate monitoring
* Fraud spike alert detection

## 🔹 Fraud Intelligence

* Fraud source breakdown (ML vs Velocity)
* Velocity burst detection table
* High-risk transactions (time window configurable)
* Top risk customers (lifetime aggregation)

## 🔹 Customer Investigation

* Customer lifetime transaction count
* Fraud count
* Average risk score
* Full transaction history per customer

## 🔹 Analyst Export Features

Downloadable CSV exports:

* Fraud source breakdown
* Top risk customers
* High-risk transactions
* Velocity alerts
* Customer transactions
* ✅ Full dataset export (with optional row limit + status filter)

---

# ⚡ Performance Optimizations

* Indexed MySQL columns
* Composite index for velocity rule
* Batch inserts via `bulk_insert_mappings`
* Producer-side batching (`linger.ms`, `batch.num.messages`)
* Persistent MySQL Docker volume
* SQLAlchemy connection pooling (`pool_pre_ping`)
* TTL-based caching for lifetime metrics
* Idempotent transaction constraint
* Structured logging

---

# 🔒 Reliability & Safety

* Dead Letter Queue (DLQ)
* Unique transaction ID constraint
* Pydantic schema validation
* Retry logic for database readiness
* Automatic ML training fallback
* Kafka consumer group coordination

---

# 🧪 Running Tests

```bash
pytest
```

Expected output:

```
2 passed
```

Tests validate:

* ML predictor correctness
* Fraud status classification logic

---

# 📦 Expected Deliverables 

This repository includes:

* Complete GitHub codebase
* Fully Dockerized reproducible environment
* README documentation with setup instructions
* Sample Kafka transaction generator
* MySQL schema definition
* Real-time ML fraud scoring implementation
* Monitoring dashboard
* CSV export capabilities
* Unit tests

---

# 🏁 System Summary

| Capability                     | Included |
| ------------------------------ | -------- |
| Fully Dockerized               | ✅        |
| Autonomous Startup             | ✅        |
| Real-Time Streaming Pipeline   | ✅        |
| ML-Based Fraud Scoring         | ✅        |
| Velocity-Based Fraud Detection | ✅        |
| Fraud Source Attribution       | ✅        |
| Persistent Database Storage    | ✅        |
| Analyst CSV Exports            | ✅        |
| Live Operational Monitoring    | ✅        |
| Unit Testing                   | ✅        |

---

# 👤 Author

Omar Khalil \
[omark8977@gmail.com](mailto:omark8977@gmail.com)

---

