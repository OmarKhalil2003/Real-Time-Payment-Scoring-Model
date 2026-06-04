"""
Scoring Service — Fraud Analysis Pipeline

Orchestrates the complete fraud scoring flow:
1. Parse transaction from Kafka
2. Run ML model prediction
3. Query MCP Server 1 (Customer History) for behavioral context
4. Query MCP Server 2 (Fraud Rules Engine) for rule-based risk
5. Apply velocity rule (count recent transactions)
6. Blend scores: 40% ML + 40% MCP rules + 20% velocity
7. Query MCP Server 3 (Fraud Explanation) for high-risk transactions
8. Persist enriched result to MySQL
"""

import json
import logging
from datetime import datetime
from app.kafka.schema import PaymentTransaction
from app.database.repository import TransactionRepository

VELOCITY_THRESHOLD = 12  # 12 tx in 60 seconds
VELOCITY_WINDOW_SECONDS = 60

logger = logging.getLogger("scoring-service")


class ScoringService:

    def __init__(self, predictor, mcp_client=None):
        self.predictor = predictor
        self.mcp_client = mcp_client

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

    async def process(self, raw_message: dict):
        """
        Async processing pipeline with MCP enrichment.
        Called directly from the async main loop.
        """
        start_time = datetime.utcnow()

        transaction = PaymentTransaction(**raw_message)

        features = [
            transaction.feature_1,
            transaction.feature_2,
            transaction.feature_3,
        ]

        # ----------------------------
        # ML Prediction
        # ----------------------------
        score, prediction = self.predictor.predict(features)
        ml_score = score
        reason = "ML_MODEL"

        # ----------------------------
        # MCP Enrichment
        # ----------------------------
        customer_history = {}
        mcp_risk_result = {"risk_score": 0, "triggered_rules": []}
        explanation = None

        if self.mcp_client:
            # Step 3: Customer History via MCP
            customer_history = await self.mcp_client.get_customer_history(
                transaction.customer_id
            )

            if customer_history:
                logger.info(
                    f"[MCP] Customer history retrieved for {transaction.customer_id}: "
                    f"avg_amount={customer_history.get('average_amount')}, "
                    f"usual_country={customer_history.get('usual_country')}"
                )

            # Step 4: Fraud Rules via MCP
            tx_data = {
                "amount": transaction.amount,
                "country": transaction.country,
                "transaction_id": transaction.transaction_id,
                "customer_id": transaction.customer_id,
            }
            mcp_risk_result = await self.mcp_client.evaluate_risk_rules(
                tx_data, customer_history
            )

            if mcp_risk_result.get("triggered_rules"):
                logger.info(
                    f"[MCP] Rules triggered for Tx={transaction.transaction_id}: "
                    f"{mcp_risk_result['triggered_rules']}"
                )
                reason = "MCP_RULES"

        # ----------------------------
        # Velocity Rule
        # ----------------------------
        recent_count = TransactionRepository.count_recent_transactions(
            transaction.customer_id,
            seconds=VELOCITY_WINDOW_SECONDS,
        )

        velocity_boost = 0.0
        if recent_count >= VELOCITY_THRESHOLD:
            velocity_boost = 0.15
            reason = "VELOCITY_RULE"

            logger.warning(
                f"[VELOCITY_ALERT] Customer={transaction.customer_id} "
                f"RecentTx={recent_count}"
            )

        # ----------------------------
        # Score Blending
        # ----------------------------
        mcp_risk_normalized = mcp_risk_result.get("risk_score", 0) / 100.0

        if self.mcp_client and customer_history:
            # Full MCP-enriched scoring:
            # 40% ML model + 40% MCP rules + 20% velocity component
            score = (
                ml_score * 0.4
                + mcp_risk_normalized * 0.4
                + velocity_boost
            )
        else:
            # Fallback: ML score + velocity boost (original behavior)
            score = min(ml_score + velocity_boost, 0.99)

        score = min(score, 0.99)

        # ----------------------------
        # Final Decision
        # ----------------------------
        status = self.determine_status(score)

        # ----------------------------
        # Explanation (for high-risk only)
        # ----------------------------
        if self.mcp_client and score >= 0.65:
            tx_data = {
                "amount": transaction.amount,
                "country": transaction.country,
                "transaction_id": transaction.transaction_id,
                "customer_id": transaction.customer_id,
            }
            explanation = await self.mcp_client.explain_fraud_decision(
                tx_data,
                customer_history,
                score,
                mcp_risk_result.get("triggered_rules", []),
            )

        processed_time = datetime.utcnow()
        latency_ms = (processed_time - start_time).total_seconds() * 1000

        logger.info(
            f"[SCORING] Tx={transaction.transaction_id} | "
            f"ML={ml_score:.4f} | MCP_Risk={mcp_risk_result.get('risk_score', 0)} | "
            f"Final={score:.4f} | Status={status} | "
            f"Reason={reason} | Latency={latency_ms:.2f}ms"
        )

        if explanation:
            logger.info(f"[EXPLANATION] {explanation}")

        # ----------------------------
        # Persist
        # ----------------------------
        triggered_rules_str = json.dumps(
            mcp_risk_result.get("triggered_rules", [])
        )

        TransactionRepository.save({
            "transaction_id": transaction.transaction_id,
            "customer_id": transaction.customer_id,
            "amount": transaction.amount,
            "country": transaction.country,
            "score": score,
            "prediction": prediction,
            "status": status,
            "reason": reason,
            "mcp_risk_score": mcp_risk_result.get("risk_score", 0),
            "triggered_rules": triggered_rules_str,
            "explanation": explanation,
            "processed_at": processed_time,
        })
