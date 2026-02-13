import json
import time
import random
import uuid
import os
from confluent_kafka import Producer

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer = Producer({
    "bootstrap.servers": KAFKA_SERVER,
    "linger.ms": 5,              # allow batching
    "batch.num.messages": 1000   # improve throughput
})

CUSTOMER_POOL = [f"CUST_{i}" for i in range(1, 201)]

def generate_transaction():
    is_fraud = random.random() < 0.03

    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": random.choice(CUSTOMER_POOL),
        "amount": round(random.uniform(2000, 10000), 2) if is_fraud else round(random.uniform(10, 500), 2),
        "feature_1": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.1, 0.5),
        "feature_2": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.1, 0.5),
        "feature_3": random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.1, 0.5),
    }

def run_producer():
    print("🚀 Producer started...")
    count = 0

    try:
        while True:
            data = generate_transaction()

            producer.produce("payments", value=json.dumps(data))
            producer.poll(0)

            count += 1
            if count % 100 == 0:
                print(f"Produced {count} transactions")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping producer...")



if __name__ == "__main__":
    run_producer()
