
---

# 💳 Real-Time Payment Scoring System

A fully containerized, real-time fraud detection pipeline simulating payment scoring system.

---

# 🎯 Objectives

* Real-time transaction ingestion via Kafka
* ML-based fraud scoring
* Rule-based velocity detection
* Batch persistence into MySQL
* Live monitoring dashboard
* Fully containerized deployment
* Autonomous startup 

---

# 🏗 Architecture

```
Docker Compose
│
├── Zookeeper
├── Kafka
│     └── Topic: payments (auto-created)
├── MySQL (persistent volume)
├── Producer (Dockerized)
│     └── Generates simulated transactions
├── Consumer App (Dockerized)
│     ├── Loads ML model (auto-trains if missing)
│     ├── Applies fraud model
│     ├── Applies velocity rule
│     ├── Batch inserts results
│     └── DLQ handling
└── Streamlit Dashboard (Dockerized)
```

---

# ⚙️ Tech Stack

* Python 3.10
* Apache Kafka
* MySQL 8
* SQLAlchemy
* Scikit-learn
* Streamlit
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

```bash
docker compose up --build -d
```

Then open:

```
http://localhost:8501
```

No `.env` file required. \
No manual Kafka topic creation. \
No manual database setup. \
Fully autonomous.

---

# 🧠 Autonomous System Behavior

On startup, the system automatically:

* Creates Kafka topic (`payments`)
* Waits for MySQL readiness
* Trains ML model if artifacts are missing
* Loads model & scaler
* Starts producer traffic generation
* Starts consumer scoring loop
* Batch inserts into MySQL
* Launches Streamlit dashboard


---

# 🧪 Test Data

## 📩 Sample Kafka Message

The producer generates messages in the following format:

```json
{
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST_148",
  "amount": 320.55,
  "feature_1": 0.42,
  "feature_2": 0.37,
  "feature_3": 0.29
}
```

Fraud simulation logic:

* ~15% high-risk transactions
* Higher amounts
* Higher feature values

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

---

# 📊 Fraud Detection Logic

### 1️⃣ Machine Learning

* RandomForest classifier
* Probability-based fraud scoring
* Scaler preprocessing

### 2️⃣ Velocity Rule

* Detects rapid burst transactions per customer
* Enhances fraud detection reliability
* Combines rule-based + ML logic

### 3️⃣ Status Classification

* APPROVED
* REVIEW
* DECLINED

---

# 📈 Dashboard Features

* Lifetime fraud counters 
* Fraud rate calculation 
* Fraud-over-time visualization (recent 500 window)
* Customer lifetime risk profile
* Latest transactions view
* Adjustable auto-refresh (1–5 seconds)

Metrics use full-table aggregation. \
Charts use recent transaction window for performance.

---

# ⚡ Performance Optimizations

* Indexed MySQL columns
* Batch insert using bulk mappings
* Persistent database volume
* Efficient producer batching
* Consumer offset tracking
* Structured logging
* Idempotent transaction constraint

---

# 🔒 Reliability Features

* Dead Letter Queue (DLQ)
* Unique transaction ID constraint
* Schema validation
* Retry logic for MySQL readiness
* Automatic model training fallback
* Kafka consumer group offset management

---

# 🧪 Running Tests

```bash
pytest
```

Expected output:

```
2 passed
```

---

# 🏁 System Characteristics

| Feature                       | Status |
| ----------------------------- | ------ |
| Fully Dockerized              | ✅      |
| Autonomous Startup            | ✅      |
| Live Traffic Simulation       | ✅      |
| Persistent Database           | ✅      |
| Batch Optimization            | ✅      |
| Monitoring Dashboard          | ✅      |
| Unit Tests                    | ✅      |

---

# ✅ Deliverables Summary

✔ Complete Dockerized system \
✔ Autonomous startup \
✔ Real-time Kafka streaming pipeline \
✔ Machine learning fraud scoring \
✔ MySQL persistence layer \
✔ Sample Kafka test data \
✔ MySQL schema definition \
✔ Live monitoring dashboard \
✔ Unit tests \
✔ Professional documentation \

---

# 👤 Author

Omar Khalil \
[omark8977@gmail.com](mailto:omark8977@gmail.com)

---
