from sqlalchemy import (
    Column, Integer, Float, String, DateTime,
    UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ScoredTransaction(Base):
    __tablename__ = "scored_transactions"

    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_transaction_id"),
        Index("idx_customer_id", "customer_id"),
        Index("idx_created_at", "created_at"),
        Index("idx_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), nullable=False)
    customer_id = Column(String(100), nullable=False)
    amount = Column(Float)
    score = Column(Float)
    prediction = Column(Integer)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
