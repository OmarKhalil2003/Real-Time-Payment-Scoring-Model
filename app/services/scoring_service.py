import logging
from app.kafka.schema import PaymentTransaction
from app.database.repository import TransactionRepository

VELOCITY_THRESHOLD = 5
logger = logging.getLogger("scoring-service")

class ScoringService:

    def __init__(self, predictor):
        self.predictor = predictor

    def determine_status(self, score, prediction):
        if prediction == 1 and score > 0.9:
            return "DECLINED"
        elif prediction == 1:
            return "REVIEW"
        else:
            return "APPROVED"

    def process(self, raw_message: dict):
        transaction = PaymentTransaction(**raw_message)

        features = [
            transaction.feature_1,
            transaction.feature_2,
            transaction.feature_3
        ]

        score, prediction = self.predictor.predict(features)

        recent_count = TransactionRepository.count_recent_transactions(
            transaction.customer_id,
            seconds=60
        )

        if recent_count >= VELOCITY_THRESHOLD:
            prediction = 1
            score = max(score, 0.95)
            logger.warning(
                f"Velocity fraud detected for customer {transaction.customer_id}"
            )

        status = self.determine_status(score, prediction)

        logger.info(
            f"Transaction {transaction.transaction_id} | "
            f"Score: {score:.4f} | Status: {status}"
        )

        TransactionRepository.save({
            "transaction_id": transaction.transaction_id,
            "customer_id": transaction.customer_id,
            "amount": transaction.amount,
            "score": score,
            "prediction": prediction,
            "status": status
        })
