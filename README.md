# 💳 Real-Time Payment Scoring System



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
run.ps1
requirements.txt
```

---

# 🚀 Quick Start (Windows)

### One Command Startup

```powershell
.\run.ps1
```

This will:

* Build Docker images
* Start all services
* Wait until dashboard is ready
* Automatically open browser at:

```
http://localhost:8501
```

---

# 🚀 Quick Start (Manual)

```bash
docker compose up --build -d
```

Then open:

```
http://localhost:8501
```

That’s it.

No additional setup required.

---

# 🧠 Autonomous Features

The system automatically:

* Creates Kafka topic (`payments`)
* Trains ML model if not found
* Waits for MySQL readiness
* Applies batch insert optimization
* Starts producer traffic generation
* Starts consumer scoring
* Launches dashboard

Fully self-initializing.

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

### 2️⃣ Velocity Rule

* Detects burst transactions per customer
* Enhances fraud detection reliability

### 3️⃣ Status Classification

* APPROVED
* REVIEW
* DECLINED

---

# 📈 Dashboard Features

* Lifetime fraud counters
* Fraud rate calculation
* Fraud-over-time visualization
* Customer-level risk profile
* Latest transactions view
* Auto-refresh support

Metrics use full-table aggregation.
Charts use recent 1000-transaction window.

---

# ⚡ Performance Optimizations

* Indexed MySQL columns
* Batch insert using bulk mappings
* Persistent database volume
* Cached dashboard queries
* Structured logging
* Idempotent transaction constraint
* Graceful shutdown flush

---

# 🔒 Reliability Features

* Dead Letter Queue (DLQ)
* Unique transaction ID constraint
* Schema validation
* Retry logic for MySQL readiness
* Automatic model training fallback

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

| Feature                       | Status             |
| ----------------------------- | ------------------ |
| Fully Dockerized              | ✅                  |
| Autonomous Startup            | ✅                  |
| Live Traffic Simulation       | ✅                  |
| Persistent Database           | ✅                  |
| Batch Optimization            | ✅                  |
| Monitoring Dashboard          | ✅                  |
| Unit Tests                    | ✅                  |

---

# ✅ Deliverables Summary

✔ Complete Dockerized system \
✔ Autonomous startup script \
✔ Real-time streaming pipeline \
✔ Machine learning scoring \
✔ MySQL persistence \
✔ Live monitoring dashboard \
✔ Unit tests \
✔ Professional documentation

---

# 👤 Author

Omar Khalil \
omark8977@gmail.com
---

