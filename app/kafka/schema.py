from pydantic import BaseModel, Field
from typing import Optional


class PaymentTransaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    country: str = "Egypt"
    feature_1: float
    feature_2: float
    feature_3: float
    merchant_id: Optional[str] = None
    currency: Optional[str] = "USD"
    payment_method: Optional[str] = None
    device: Optional[str] = None
    ip: Optional[str] = Field(default=None, alias="ip")
    event_type: Optional[str] = "purchase"
    fraud_label: Optional[int] = 0

    model_config = {"populate_by_name": True}
