import json
from confluent_kafka import Consumer, Producer
from app.config.settings import settings

class KafkaConsumerClient:

    def __init__(self):
        self.consumer = Consumer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": settings.KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest"
        })

        self.producer = Producer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS
        })

        self.consumer.subscribe([settings.KAFKA_TOPIC])
        self.dlq_topic = f"{settings.KAFKA_TOPIC}_dlq"

    def poll(self):
        msg = self.consumer.poll(1.0)
        if msg is None:
            return None
        if msg.error():
            import logging
            logging.getLogger("consumer").error(f"Kafka error: {msg.error()}")
            return None

        try:
            return json.loads(msg.value().decode("utf-8"))
        except json.JSONDecodeError as e:
            import logging
            logging.getLogger("consumer").error(f"Failed to decode message: {e}. Sending raw to DLQ.")
            try:
                self.producer.produce(self.dlq_topic, value=msg.value())
                self.producer.flush()
            except Exception as dlq_e:
                logging.getLogger("consumer").error(f"Failed to DLQ malformed message: {dlq_e}")
            return None
        except Exception as e:
            import logging
            logging.getLogger("consumer").error(f"Unexpected error decoding message: {e}")
            return None

    def send_to_dlq(self, message):
        self.producer.produce(
            self.dlq_topic,
            value=json.dumps(message)
        )
        self.producer.flush()
