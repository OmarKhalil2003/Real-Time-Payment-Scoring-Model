"""Pure event generation logic (no Kafka dependency)."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

CUSTOMERS = [f"CUST_{i:05d}" for i in range(1, 501)]
MERCHANTS = [f"MERCH_{i:04d}" for i in range(1, 101)]
CARDS = [f"CARD_{i:05d}" for i in range(1, 501)]
CURRENCIES = ["USD", "EUR", "EGP", "GBP"]
PAYMENT_METHODS = ["credit_card", "debit_card", "wallet", "bank_transfer"]
DEVICES = ["mobile_ios", "mobile_android", "web_desktop", "web_mobile", "pos_terminal"]
DOMESTIC = ["Egypt"]
FOREIGN = ["Russia", "Nigeria", "China", "Brazil", "Germany", "UK", "USA", "France"]
MERCHANT_CATEGORIES = ["retail", "travel", "gaming", "food", "electronics", "services"]


def base_event(event_type: str, is_fraud: bool) -> dict:
    country = random.choice(FOREIGN) if is_fraud and random.random() < 0.7 else (
        random.choice(DOMESTIC) if random.random() < 0.9 else random.choice(FOREIGN)
    )
    amount = (
        round(random.uniform(2000, 15000), 2)
        if is_fraud
        else round(random.uniform(5, 800), 2)
    )
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": random.choice(CUSTOMERS),
        "merchant_id": random.choice(MERCHANTS),
        "merchant_name": f"Merchant {random.randint(1, 500)}",
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "card_id": random.choice(CARDS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount": amount,
        "currency": random.choice(CURRENCIES),
        "payment_method": random.choice(PAYMENT_METHODS),
        "country": country,
        "device": random.choice(DEVICES),
        "ip": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        "event_type": event_type,
        "status": "completed",
        "fraud_label": int(is_fraud),
        "feature_1": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.05, 0.5),
        "feature_2": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.05, 0.5),
        "feature_3": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.05, 0.5),
    }


def generate_event() -> tuple[str, dict]:
    roll = random.random()
    is_fraud = roll < 0.04

    if roll < 0.75:
        return "payments", base_event("purchase", is_fraud)
    if roll < 0.85:
        event = base_event("refund", is_fraud)
        event["amount"] = round(event["amount"] * random.uniform(0.3, 1.0), 2)
        return "refunds", event
    if roll < 0.93:
        event = base_event("failed_payment", is_fraud)
        event["status"] = "failed"
        event["amount"] = round(event["amount"] * 0.5, 2)
        return "payments", event

    event = base_event("chargeback", True)
    event["status"] = "chargeback"
    if random.random() < 0.5:
        return "alerts", {
            "alert_id": str(uuid.uuid4()),
            "transaction_id": event["transaction_id"],
            "customer_id": event["customer_id"],
            "alert_type": "chargeback",
            "severity": "high",
            "timestamp": event["timestamp"],
            "message": f"Chargeback filed for transaction {event['transaction_id']}",
        }
    return "payments", event
