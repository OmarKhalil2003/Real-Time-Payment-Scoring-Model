import logging
import time
import os
import asyncio
import subprocess
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.database.connection import engine
from app.database.models import Base
from app.database.repository import TransactionRepository
from app.kafka.consumer import KafkaConsumerClient
from app.model.loader import ModelLoader
from app.model.predictor import Predictor
from app.services.scoring_service import ScoringService


def wait_for_database(max_retries=30, delay=5):
    logger = logging.getLogger("startup")
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database is ready.")
            return
        except OperationalError:
            logger.warning(
                f"Database not ready. Retry {attempt + 1}/{max_retries}..."
            )
            time.sleep(delay)

    raise Exception("Database did not become ready in time.")


def ensure_model_exists(logger):
    model_path = "model_artifacts/fraud_model.pkl"

    if not os.path.exists(model_path):
        logger.info("Model not found. Training dummy model automatically...")
        subprocess.run(["python", "scripts/train_dummy_model.py"], check=True)
        logger.info("Model training completed.")


async def main_async():
    """
    Async main loop — keeps a single event loop alive for the entire
    application lifetime so MCP client sessions remain valid.
    """
    setup_logging()
    logger = logging.getLogger("payment-scoring")

    # Wait for DB readiness (sync, runs before async work)
    wait_for_database()

    # Auto-train model if missing
    ensure_model_exists(logger)

    Base.metadata.create_all(bind=engine)

    consumer = KafkaConsumerClient()

    model = ModelLoader.load_model()
    scaler = ModelLoader.load_scaler()
    predictor = Predictor(model, scaler)

    # ----------------------------
    # MCP Client Initialization
    # ----------------------------
    mcp_client = None

    if settings.MCP_ENABLED:
        logger.info("MCP integration enabled. Initializing MCP servers...")
        try:
            from app.mcp.mcp_client import MCPClientManager

            mcp_client = MCPClientManager()
            await mcp_client.initialize()
            logger.info("✅ MCP Client Manager initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize MCP Client: {e}. "
                "Continuing without MCP enrichment."
            )
            mcp_client = None
    else:
        logger.info("MCP integration disabled (MCP_ENABLED=false).")

    service = ScoringService(predictor, mcp_client=mcp_client)

    logger.info("🚀 Real-Time Payment Scoring Started (with MCP enrichment)")

    try:
        while True:
            try:
                message = consumer.poll()
                if message:
                    try:
                        await service.process(message)
                    except Exception:
                        logger.exception("Processing failed. Sending to DLQ.")
                        consumer.send_to_dlq(message)
                else:
                    # Yield control briefly when no messages to prevent busy-wait
                    await asyncio.sleep(0.001)
            except Exception as e:
                logger.error(f"Unexpected error in consumer loop: {e}")
                await asyncio.sleep(1)  # Prevent tight error loop
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down... Flushing remaining transactions.")
        TransactionRepository.flush()

        if mcp_client:
            logger.info("Shutting down MCP clients...")
            await mcp_client.shutdown()

        logger.info("Shutdown complete.")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
