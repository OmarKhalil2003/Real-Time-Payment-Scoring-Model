import logging
from app.config.logging_config import setup_logging
from app.database.connection import engine
from app.database.models import Base
from app.database.repository import TransactionRepository
from app.kafka.consumer import KafkaConsumerClient
from app.model.loader import ModelLoader
from app.model.predictor import Predictor
from app.services.scoring_service import ScoringService

def main():
    setup_logging()
    logger = logging.getLogger("payment-scoring")

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
