# MCP Integration Plan for Real-Time Payment Fraud Scoring System

## Project Goal

Extend the existing Kafka-based Real-Time Payment Fraud Scoring System by introducing Model Context Protocol (MCP) to create a more realistic distributed AI architecture.

The current system uses Kafka for event-driven communication between services. The enhancement introduces MCP as a standardized protocol for accessing external intelligence and contextual information required for fraud analysis.

The objective is to demonstrate two layers of indirect communication:

1. Kafka → indirect communication between distributed services.
2. MCP → indirect communication between AI/scoring services and external knowledge providers.

---

# Current Architecture

```text
Payment Producer
      |
      v
Kafka Transaction Topic
      |
      v
Fraud Scoring Service
      |
      v
Kafka Result Topic
```

Current fraud detection relies only on transaction data received from Kafka.

Example transaction:

{
"transaction_id": "123",
"customer_id": "C100",
"amount": 5000,
"country": "Egypt"
}

````

The scoring service evaluates the transaction with limited context.

---

# Proposed Architecture

```text
Payment Producer
        |
        v
Kafka Transaction Topic
        |
        v
Fraud Scoring Service
        |
        +-------------------------+
        |                         |
        v                         v
Customer History MCP       Fraud Rules MCP
        |                         |
        +------------+------------+
                     |
                     v
          Risk Score Calculation
                     |
                     v
      Fraud Explanation MCP
                     |
                     v
           Kafka Result Topic
````

---

# MCP Server 1: Customer History Service

## Purpose

Provide historical customer behavior to the fraud scoring engine.

The scoring service should not directly access databases.

Instead, it queries an MCP server.

---

## MCP Tool

```python
get_customer_history(customer_id)
```

---

## Returned Data

```json
{
    "total_transactions": 850,
    "average_amount": 220,
    "usual_country": "Egypt",
    "previous_fraud_flags": 0,
    "last_transaction_hours": 2
}
```

---

## Usage

Transaction arrives:

```json
{
    "customer_id": "C100",
    "amount": 5000,
    "country": "Russia"
}
```

Scoring service calls:

```python
get_customer_history("C100")
```

Response indicates:

* Average transaction amount = 220
* Usual country = Egypt

Current transaction:

* Amount = 5000
* Country = Russia

This significantly increases fraud risk.

---

# MCP Server 2: Fraud Rules Engine

## Purpose

Provide dynamic fraud rules without modifying scoring code.

---

## MCP Tool

```python
evaluate_risk_rules(transaction)
```

---

## Example Rules

```python
IF amount > 3000
    risk += 20

IF country != usual_country
    risk += 30

IF previous_fraud_flags > 0
    risk += 25
```

---

## Returned Result

```json
{
    "risk_score": 75,
    "triggered_rules": [
        "high_amount",
        "foreign_country"
    ]
}
```

---

# MCP Server 3: Fraud Explanation Service

## Purpose

Generate human-readable explanations for fraud decisions.

This demonstrates AI-agent interoperability through MCP.

---

## MCP Tool

```python
explain_fraud_decision(
    transaction,
    customer_history,
    score
)
```

---

## Example Output

```json
{
    "explanation":
    "Transaction amount is 22 times the customer's average transaction amount and originated from an unusual location."
}
```

---

# End-to-End Flow

Step 1

Payment producer sends transaction.

```text
Producer
   |
   v
Kafka
```

---

Step 2

Fraud scoring service consumes event.

```text
Kafka
   |
   v
Scoring Service
```

---

Step 3

Scoring service requests customer history via MCP.

```text
Scoring Service
      |
      v
Customer History MCP
```

---

Step 4

Scoring service requests rule evaluation via MCP.

```text
Scoring Service
      |
      v
Fraud Rules MCP
```

---

Step 5

Scoring service calculates final score.

Example:

```text
Transaction Risk = 45
History Risk = 20
Rules Risk = 15

Final Risk = 80
```

---

Step 6

Scoring service requests explanation.

```text
Scoring Service
      |
      v
Fraud Explanation MCP
```

---

Step 7

Result is published back to Kafka.

```json
{
    "transaction_id": "123",
    "risk_score": 80,
    "decision": "HIGH_RISK",
    "explanation":
    "Unusual amount and location compared to historical behavior."
}
```

---

# Technologies

## Existing

* Python
* Kafka
* Docker
* FastAPI
* Fraud Scoring Logic

## New

* MCP Python SDK
* MCP Servers
* MCP Client inside Fraud Scoring Service

---

# Distributed Systems Concepts Demonstrated

## Kafka Layer

* Publish-Subscribe
* Event Streaming
* Asynchronous Communication
* Decoupling

## MCP Layer

* Indirect Communication
* Context Exchange
* Service Interoperability
* Tool Discovery
* Loose Coupling

---

# Academic Value

The project evolves from a traditional event-driven fraud detection pipeline into a distributed AI system.

The architecture demonstrates how modern intelligent services combine:

* Event-driven communication (Kafka)
* Context-driven communication (MCP)
* Distributed processing
* Service decoupling
* Explainable AI

This makes the project a strong fit for a Distributed Systems course focused on indirect communication because Kafka and MCP represent two complementary forms of indirect interaction operating at different architectural layers.
