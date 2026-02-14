from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ScoredTransaction(Base):
    __tablename__ = "scored_transactions"

    __table_args__ = (
        # Ensure idempotency
        UniqueConstraint("transaction_id", name="uq_transaction_id"),

        # Optimized for velocity rule:
        # WHERE customer_id = ? AND created_at >= ?
        Index("idx_customer_created", "customer_id", "created_at"),

        # Used heavily in dashboard aggregations
        Index("idx_status", "status"),

        # Optional but useful for latency analytics
        Index("idx_processed_at", "processed_at"),
    )

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(String(100), nullable=False)
    customer_id = Column(String(100), nullable=False)

    amount = Column(Float)

    score = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)

    # Explainability field
    reason = Column(String(100), nullable=True)

    # When transaction was inserted (event time)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # When model finished processing (for latency tracking)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
