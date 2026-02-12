import json
import time
import random
import uuid
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})

CUSTOMER_POOL = [f"CUST_{i}" for i in range(1, 201)]

def generate_normal_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": random.choice(CUSTOMER_POOL),
        "amount": round(random.uniform(10, 500), 2),
        "feature_1": random.uniform(0.1, 0.5),
        "feature_2": random.uniform(0.1, 0.5),
        "feature_3": random.uniform(0.1, 0.5),
    }

def generate_fraud_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": random.choice(CUSTOMER_POOL),
        "amount": round(random.uniform(2000, 10000), 2),
        "feature_1": random.uniform(0.7, 1.0),
        "feature_2": random.uniform(0.7, 1.0),
        "feature_3": random.uniform(0.7, 1.0),
    }

def run_producer(num_messages=50, delay=0.5):
    for i in range(num_messages):

        # 15% fraud simulation
        if random.random() < 0.15:
            data = generate_fraud_transaction()
            print("⚠ FRAUD-LIKE:", data)
        else:
            data = generate_normal_transaction()
            print("Normal:", data)

        producer.produce("payments", value=json.dumps(data))
        producer.flush()
        time.sleep(delay)

    print("\n Finished sending messages.")

if __name__ == "__main__":
    run_producer()
