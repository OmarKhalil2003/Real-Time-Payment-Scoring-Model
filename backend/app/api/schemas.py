from pydantic import BaseModel
from datetime import datetime


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    amount: float
    user_id: str
    fraud_probability: float
    risk_label: str
    created_at: datetime

    class Config:
        from_attributes = True
