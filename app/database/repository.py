from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import insert
from app.database.connection import SessionLocal
from app.database.models import ScoredTransaction

BATCH_SIZE = 200


class TransactionRepository:

    _buffer = []

    @classmethod
    def save(cls, transaction_data: dict):
        """
        Add transaction to in-memory buffer.
        Flush automatically when batch size is reached.
        """
        cls._buffer.append(transaction_data)

        if len(cls._buffer) >= BATCH_SIZE:
            cls.flush()

    @classmethod
    def flush(cls):
        """
        Bulk insert buffered transactions into MySQL.
        """
        if not cls._buffer:
            return

        session = SessionLocal()
        try:
            # Use INSERT IGNORE to prevent batch failure on duplicate transaction_id
            stmt = insert(ScoredTransaction).values(cls._buffer).prefix_with("IGNORE")
            session.execute(stmt)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            cls._buffer.clear()
            session.close()

    @classmethod
    def count_recent_transactions(cls, customer_id: str, seconds: int = 60):
        """
        Count transactions for a customer in the last X seconds.
        Optimized query using COUNT(*) with proper filtering.
        """

        session = SessionLocal()
        try:
            time_threshold = datetime.utcnow() - timedelta(seconds=seconds)

            db_count = (
                session.query(func.count())
                .select_from(ScoredTransaction)
                .filter(ScoredTransaction.customer_id == customer_id)
                .filter(ScoredTransaction.created_at >= time_threshold)
                .scalar()
            )
            db_count = db_count or 0

            # Count un-flushed transactions in the buffer for this customer
            buffer_count = sum(
                1 for tx in cls._buffer
                if tx["customer_id"] == customer_id
            )

            return db_count + buffer_count
        finally:
            session.close()
