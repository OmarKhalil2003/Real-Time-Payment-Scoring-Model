import logging
from app.kafka.schema import PaymentTransaction
from app.database.repository import TransactionRepository

# More realistic threshold
VELOCITY_THRESHOLD = 12  # 12 transactions in 60 seconds

logger = logging.getLogger("scoring-service")


class ScoringService:

    def __init__(self, predictor):
        self.predictor = predictor

    def determine_status(self, score):
        """
        Balanced classification thresholds
        """
        if score >= 0.85:
            return "DECLINED"
        elif score >= 0.65:
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

        # ----------------------------
        # Velocity Rule (Soft Impact)
        # ----------------------------
        recent_count = TransactionRepository.count_recent_transactions(
            transaction.customer_id,
            seconds=60
        )

        if recent_count >= VELOCITY_THRESHOLD:
            logger.warning(
                f"Velocity alert for customer {transaction.customer_id}"
            )

            # Instead of forcing 0.95 (which causes mass DECLINES),
            # slightly increase risk
            score = min(score + 0.1, 0.95)

        # Determine status based on final score only
        status = self.determine_status(score)

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
