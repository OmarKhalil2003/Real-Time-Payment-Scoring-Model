import logging
from datetime import datetime
from app.kafka.schema import PaymentTransaction
from app.database.repository import TransactionRepository

VELOCITY_THRESHOLD = 12  # 12 tx in 60 seconds
VELOCITY_WINDOW_SECONDS = 60

logger = logging.getLogger("scoring-service")


class ScoringService:

    def __init__(self, predictor):
        self.predictor = predictor

    def determine_status(self, score: float) -> str:
        """
        Final classification strictly based on risk score.
        """
        if score >= 0.85:
            return "DECLINED"
        elif score >= 0.65:
            return "REVIEW"
        else:
            return "APPROVED"

    def process(self, raw_message: dict):

        start_time = datetime.utcnow()

        transaction = PaymentTransaction(**raw_message)

        features = [
            transaction.feature_1,
            transaction.feature_2,
            transaction.feature_3
        ]

        # ----------------------------
        # ML Prediction
        # ----------------------------
        score, prediction = self.predictor.predict(features)
        reason = "ML_MODEL"

        # ----------------------------
        # Velocity Rule
        # ----------------------------
        recent_count = TransactionRepository.count_recent_transactions(
            transaction.customer_id,
            seconds=VELOCITY_WINDOW_SECONDS
        )

        if recent_count >= VELOCITY_THRESHOLD:
            reason = "VELOCITY_RULE"

            # Soft risk boost (controlled impact)
            score = min(score + 0.15, 0.99)

            logger.warning(
                f"[VELOCITY_ALERT] Customer={transaction.customer_id} "
                f"RecentTx={recent_count}"
            )

        # ----------------------------
        # Final Decision
        # ----------------------------
        status = self.determine_status(score)

        processed_time = datetime.utcnow()
        latency_ms = (processed_time - start_time).total_seconds() * 1000

        logger.info(
            f"[SCORING] Tx={transaction.transaction_id} | "
            f"Score={score:.4f} | Status={status} | "
            f"Reason={reason} | Latency={latency_ms:.2f}ms"
        )

        # ----------------------------
        # Persist
        # ----------------------------
        TransactionRepository.save({
            "transaction_id": transaction.transaction_id,
            "customer_id": transaction.customer_id,
            "amount": transaction.amount,
            "score": score,
            "prediction": prediction,
            "status": status,
            "reason": reason,
            "processed_at": processed_time
        })
