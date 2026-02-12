# 💳 Real-Time Payment Scoring System

## 📌 Overview

This project implements a **real-time payment scoring system** that consumes transaction data from Apache Kafka, applies a pre-trained machine learning model for fraud detection, and stores the scoring results in a MySQL database.

The system is designed to simulate a real-world fraud detection pipeline used in financial institutions.

---

## 🎯 Objectives

* Consume payment transactions from a Kafka stream in real time
* Score each transaction using a pre-trained ML model
* Detect fraud using both model-based and rule-based logic
* Store results in MySQL for reporting and monitoring
* Provide a live monitoring dashboard using Streamlit

---

## 🏗 Architecture

```
Kafka Producer
      ↓
Kafka Topic (payments)
      ↓
Kafka Consumer (Python)
      ↓
ML Model (Fraud Scoring)
      ↓
Velocity Check (MySQL-based)
      ↓
Batch Insert
      ↓
MySQL (scored_transactions table)
      ↓
Streamlit Dashboard
```

---

## ⚙️ Tech Stack

* Python 3.10+
* Apache Kafka
* MySQL 8
* SQLAlchemy (ORM)
* Scikit-learn
* Streamlit
* Docker & Docker Compose
* Pytest (Unit Testing)

---

## 📂 Project Structure

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
requirements.txt
```

---

## 🚀 Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/OmarKhalil2003/Real-Time-Payment-Scoring-Model
cd Real-Time-Payment-Scoring-Model
```

---

### 2️⃣ Start Infrastructure (Kafka + MySQL)

```bash
docker compose up -d
```

Wait ~20 seconds for services to initialize.

---

### 3️⃣ Create Kafka Topic

```bash
docker exec -it real-time-payment-scoring-model-kafka-1 bash
```

Inside container:

```bash
kafka-topics --create \
  --topic payments \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1
```

Exit container.

---

### 4️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Train Dummy Model (Required Once)

```bash
python scripts/train_dummy_model.py
```

This creates:

```
model_artifacts/
    fraud_model.pkl
    scaler.pkl
```

---

### 6️⃣ Run Real-Time Scoring Service

```bash
python -m app.main
```

You should see:

```
Real-Time Payment Scoring Started
```

---

### 7️⃣ Send Sample Transactions

In another terminal:

```bash
python scripts/sample_producer.py
```

Transactions will now be scored and stored in MySQL.

---

### 8️⃣ Run Monitoring Dashboard

```bash
streamlit run dashboard.py
```

Open:

```
http://localhost:8501
```

---

## 🗄 MySQL Schema

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

## 📊 Fraud Logic

The system combines:

### 1️⃣ ML-Based Detection

* RandomForest classifier
* Probability-based fraud scoring

### 2️⃣ Velocity-Based Rule

* Counts recent transactions per customer
* Flags suspicious burst behavior

### 3️⃣ Business Status Classification

* APPROVED
* REVIEW
* DECLINED

---

## 📈 Dashboard Features

* Fraud rate monitoring
* Fraud-over-time chart
* Customer risk profile
* Auto-refresh capability
* Latest transaction viewer

---

## 🧪 Running Tests

```bash
pytest
```

Expected output:

```
2 passed
```

---

## ⚡ Performance Optimizations

* Indexed database columns
* Batch insert (bulk insert mappings)
* Idempotent transaction handling
* Graceful shutdown flush
* Structured logging

---

## 🔒 Reliability Features

* Dead Letter Queue (DLQ) handling
* Unique transaction constraint
* Schema validation with Pydantic
* Exception handling and logging

---

## 📈 Scalability Considerations

For production-scale systems:

* Redis-based velocity detection
* Kafka partition scaling
* Horizontal consumer scaling
* Connection pooling tuning
* Kubernetes deployment
* MLflow model registry
* Exactly-once processing guarantees


---

# ✅ Deliverables Summary

✔ Complete code repository
✔ Documentation
✔ Sample Kafka producer
✔ MySQL schema definition
✔ Unit tests
✔ Live monitoring UI

---
