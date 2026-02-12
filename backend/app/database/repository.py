from sqlalchemy.orm import Session
from app.database.models import TransactionScore


def save_transaction_score(db: Session, data: dict):
    transaction = TransactionScore(**data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
