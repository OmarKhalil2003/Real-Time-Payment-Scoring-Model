from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
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
            session.bulk_insert_mappings(
                ScoredTransaction,
                cls._buffer
            )
            session.commit()
            cls._buffer.clear()
        except IntegrityError:
            # Ignore duplicates safely
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def count_recent_transactions(customer_id: str, seconds: int = 60):
        """
        Count transactions for a customer in the last X seconds.
        Optimized query using COUNT(*) with proper filtering.
        """

        session = SessionLocal()
        try:
            time_threshold = datetime.utcnow() - timedelta(seconds=seconds)

            count = (
                session.query(func.count())
                .select_from(ScoredTransaction)
                .filter(ScoredTransaction.customer_id == customer_id)
                .filter(ScoredTransaction.created_at >= time_threshold)
                .scalar()
            )

            return count or 0
        finally:
            session.close()
