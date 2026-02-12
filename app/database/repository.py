from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.database.connection import SessionLocal
from app.database.models import ScoredTransaction

BATCH_SIZE = 20

class TransactionRepository:

    _buffer = []

    @classmethod
    def save(cls, transaction_data: dict):
        cls._buffer.append(transaction_data)

        if len(cls._buffer) >= BATCH_SIZE:
            cls.flush()

    @classmethod
    def flush(cls):
        if not cls._buffer:
            return

        session = SessionLocal()
        try:
            session.bulk_insert_mappings(ScoredTransaction, cls._buffer)
            session.commit()
            cls._buffer.clear()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def count_recent_transactions(customer_id: str, seconds: int = 60):
        session = SessionLocal()
        try:
            time_threshold = datetime.utcnow() - timedelta(seconds=seconds)

            count = session.query(func.count(ScoredTransaction.id))\
                .filter(ScoredTransaction.customer_id == customer_id)\
                .filter(ScoredTransaction.created_at >= time_threshold)\
                .scalar()

            return count
        finally:
            session.close()
