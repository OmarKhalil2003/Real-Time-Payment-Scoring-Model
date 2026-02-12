from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class TransactionScore(Base):
    __tablename__ = "transaction_scores"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), index=True)
    amount = Column(Float)
    user_id = Column(String(100))
    fraud_probability = Column(Float)
    risk_label = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
