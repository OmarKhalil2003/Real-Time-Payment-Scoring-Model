#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}"

echo "Creating Kafka topics on ${BOOTSTRAP}..."

for topic in payments refunds alerts payments_dlq refunds_dlq; do
  kafka-topics --bootstrap-server "${BOOTSTRAP}" \
    --create --if-not-exists \
    --topic "${topic}" \
    --partitions 3 \
    --replication-factor 1 || true
done

echo "Kafka topics ready."
