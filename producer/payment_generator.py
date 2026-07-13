"""
Production-grade payment event generator.

Supports: purchases, refunds, failed payments, chargebacks.
Publishes to Kafka topics: payments, refunds, alerts.
"""

from __future__ import annotations

import json
import logging
import os
import time

from confluent_kafka import Producer

from producer.events import generate_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("payment-generator")

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
PRODUCE_RATE = float(os.getenv("PRODUCE_RATE_SECONDS", "0.02"))
BATCH_LOG = int(os.getenv("BATCH_LOG", "100"))

producer = Producer({
    "bootstrap.servers": KAFKA_SERVER,
    "linger.ms": 5,
    "batch.num.messages": 1000,
    "retries": 5,
    "acks": "all",
})


def _delivery_callback(err, msg):
    if err:
        logger.error("Delivery failed: %s -> sending to DLQ", err)
        dlq_topic = f"{msg.topic()}_dlq"
        try:
            producer.produce(dlq_topic, value=msg.value(), key=msg.key())
        except Exception as dlq_err:
            logger.exception("DLQ publish failed: %s", dlq_err)


def run():
    logger.info("Payment generator started (payments/refunds/alerts)")
    count = 0
    while True:
        topic, payload = generate_event()
        key = payload.get("transaction_id", payload.get("alert_id", ""))
        producer.produce(
            topic,
            key=str(key).encode(),
            value=json.dumps(payload).encode(),
            callback=_delivery_callback,
        )
        producer.poll(0)
        count += 1
        if count % BATCH_LOG == 0:
            logger.info("Produced %s events", count)
        time.sleep(PRODUCE_RATE)


if __name__ == "__main__":
    run()
