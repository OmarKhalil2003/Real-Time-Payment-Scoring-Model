from pydantic import BaseModel

class PaymentTransaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    country: str = "Egypt"
    feature_1: float
    feature_2: float
    feature_3: float
