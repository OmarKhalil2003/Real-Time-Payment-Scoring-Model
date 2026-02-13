
---

# 💳 Real-Time Payment Fraud Scoring System

A fully containerized, autonomous, real-time fraud detection pipeline built using Kafka, Machine Learning, MySQL, and Streamlit.

---

# 🎯 Objectives

* Real-time transaction ingestion via Kafka
* Machine learning–based fraud scoring
* Rule-based velocity detection
* High-performance batch persistence into MySQL
* Live monitoring dashboard with real-time metrics
* Fully containerized deployment
* Autonomous system

---

# 🏗 Architecture

```
Docker Compose
│
├── Zookeeper
├── Kafka
│     └── Topic: payments (auto-created)
├── MySQL (persistent volume)
│
├── Producer (Dockerized)
│     └── Generates simulated transactions continuously
│
├── Consumer App (Dockerized)
│     ├── Auto-trains ML model if missing
│     ├── Applies fraud model
│     ├── Applies velocity rule
│     ├── Batch inserts scored results
│     ├── Handles DLQ
│     └── Ensures idempotency
│
└── Streamlit Dashboard (Dockerized)
      ├── Lifetime fraud metrics
      ├── Throughput monitoring
      ├── Risk score distribution (Plotly)
      ├── Fraud-over-time visualization
      └── Customer-level risk profiling
```

---

# ⚙️ Tech Stack

* Python 3.10
* Apache Kafka
* MySQL 8
* SQLAlchemy
* Scikit-learn (RandomForest)
* Streamlit
* Plotly
* Docker & Docker Compose
* Pytest

---

# 📂 Project Structure

```
app/
  config/
  database/
  kafka/
  model/
  services/
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

Then open:

```
http://localhost:8501
```

That’s it.

No virtual environments.
No manual Kafka topic creation.
No manual model training.

The system is fully autonomous.

---

# 🧠 Autonomous Features

The system automatically:

* Auto-creates Kafka topic (`payments`)
* Auto-trains ML model if not found
* Waits for MySQL readiness
* Applies batch insert optimization
* Starts producer traffic generation
* Starts consumer scoring
* Launches dashboard
* Handles retry logic and DLQ


---

# 🗄 MySQL Schema

```sql
CREATE TABLE scored_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    customer_id VARCHAR(100) NOT NULL,
    amount FLOAT,
    score FLOAT,
    prediction INT,
    status VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);
```

Indexed for high-throughput inserts and analytical queries.

---

# 📊 Fraud Detection Logic

### 1️⃣ Machine Learning Layer

* RandomForest classifier
* Probability-based scoring
* Adjustable fraud threshold

### 2️⃣ Velocity Rule Layer

* Detects burst transactions per customer (last 60 seconds)
* Elevates risk when threshold exceeded
* Prevents rapid-attack fraud patterns

### 3️⃣ Status Classification

| Condition               | Status   |
| ----------------------- | -------- |
| High confidence fraud   | DECLINED |
| Medium confidence fraud | REVIEW   |
| Low risk                | APPROVED |

---

# 📈 Dashboard Features

* Lifetime fraud counters 
* Fraud rate monitoring
* Transactions per minute
* Fraud spike alert detection
* Risk score distribution
* Fraud-over-time visualization
* Customer-level lifetime risk profile
* Recent transaction window (last 500)
* Adjustable auto-refresh (1–5 seconds)

---

# ⚡ Performance Optimizations

* Indexed MySQL columns
* Bulk insert using SQLAlchemy mappings
* Producer batching (`linger.ms`, `batch.num.messages`)
* Persistent MySQL Docker volume
* Connection pooling (`pool_pre_ping`)
* Cached lifetime metrics (TTL-based)
* Structured logging
* Idempotent transaction constraint

---

# 🔒 Reliability & Safety Features

* Dead Letter Queue (DLQ)
* Unique transaction ID constraint
* Pydantic schema validation
* Retry logic for MySQL readiness
* Automatic model training fallback
* Kafka consumer group handling

---

# 🧪 Running Tests

```bash
pytest
```

Expected output:

```
2 passed
```

Tests cover:

* Predictor correctness
* Status classification logic

---

# 🏁 System Characteristics

| Feature                         | Status |
| ------------------------------- | ------ |
| Fully Dockerized                | ✅      |
| Autonomous Startup              | ✅      |
| Live Traffic Simulation         | ✅      |
| Persistent Database Volume      | ✅      |
| Batch Optimization              | ✅      |
| Real-Time Throughput Monitoring | ✅      |
| Plotly Analytics Dashboard      | ✅      |
| Velocity Fraud Detection        | ✅      |
| Unit Tests                      | ✅      |

---

# 📦 Expected Deliverables Included

✔ Sample Kafka producer \
✔ MySQL schema definition \
✔ Fully containerized system \
✔ Autonomous infrastructure startup \
✔ Real-time ML fraud scoring \
✔ Live monitoring dashboard \
✔ Unit tests \
✔ Professional documentation

---

# 👤 Author

Omar Khalil \
[omark8977@gmail.com](mailto:omark8977@gmail.com)

---
