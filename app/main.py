import logging
import time
import os
import subprocess
from sqlalchemy.exc import OperationalError

from app.config.logging_config import setup_logging
from app.database.connection import engine
from app.database.models import Base
from app.database.repository import TransactionRepository
from app.kafka.consumer import KafkaConsumerClient
from app.model.loader import ModelLoader
from app.model.predictor import Predictor
from app.services.scoring_service import ScoringService


def wait_for_mysql(max_retries=10, delay=5):
    logger = logging.getLogger("startup")
    for attempt in range(max_retries):
        try:
            engine.connect()
            logger.info("MySQL is ready.")
            return
        except OperationalError:
            logger.warning(f"MySQL not ready. Retry {attempt + 1}/{max_retries}...")
            time.sleep(delay)

    raise Exception("MySQL did not become ready in time.")


def ensure_model_exists(logger):
    model_path = "model_artifacts/fraud_model.pkl"

    if not os.path.exists(model_path):
        logger.info("Model not found. Training dummy model automatically...")
        subprocess.run(["python", "scripts/train_dummy_model.py"], check=True)
        logger.info("Model training completed.")


def main():
    setup_logging()
    logger = logging.getLogger("payment-scoring")

    # Wait for MySQL readiness
    wait_for_mysql()

    # Auto-train model if missing
    ensure_model_exists(logger)

    Base.metadata.create_all(bind=engine)

    consumer = KafkaConsumerClient()

    model = ModelLoader.load_model()
    scaler = ModelLoader.load_scaler()
    predictor = Predictor(model, scaler)
    service = ScoringService(predictor)

    logger.info("🚀 Real-Time Payment Scoring Started")

    try:
        while True:
            message = consumer.poll()
            if message:
                try:
                    service.process(message)
                except Exception:
                    logger.exception("Processing failed. Sending to DLQ.")
                    consumer.send_to_dlq(message)
    except KeyboardInterrupt:
        logger.info("Shutting down... Flushing remaining transactions.")
        TransactionRepository.flush()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()
