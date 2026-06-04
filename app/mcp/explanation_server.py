"""
MCP Server 3: Fraud Explanation Service

Generates human-readable explanations for fraud decisions.
Demonstrates AI-agent interoperability through MCP — the scoring
service delegates explanation generation to this specialized server.

MCP Tool: explain_fraud_decision(transaction_json, customer_history_json, score)
Returns: explanation (natural language string)
"""

import json
from mcp.server.fastmcp import FastMCP

# ------------------------------------
# MCP Server Setup
# ------------------------------------

mcp = FastMCP("fraud-explanation-service")


# ------------------------------------
# Explanation Generator
# ------------------------------------

def _generate_explanation(
    transaction: dict,
    history: dict,
    score: float,
    triggered_rules: list = None,
) -> str:
    """
    Build a template-based natural language explanation of the fraud decision.
    No LLM dependency — uses rule-aware templates for deterministic output.
    """
    parts = []

    amount = transaction.get("amount", 0)
    country = transaction.get("country", "Unknown")
    avg_amount = history.get("average_amount", 0)
    usual_country = history.get("usual_country", "Unknown")
    fraud_flags = history.get("previous_fraud_flags", 0)
    last_hours = history.get("last_transaction_hours", 0)

    # Amount anomaly
    if avg_amount > 0 and amount > 2 * avg_amount:
        multiplier = round(amount / avg_amount, 1)
        parts.append(
            f"Transaction amount (${amount:,.2f}) is {multiplier}x "
            f"the customer's average (${avg_amount:,.2f})"
        )

    # Geographic anomaly
    if country != usual_country:
        parts.append(
            f"originated from {country} while the customer "
            f"usually transacts from {usual_country}"
        )

    # Fraud history
    if fraud_flags > 0:
        parts.append(
            f"customer has {fraud_flags} previous fraud flag(s) on record"
        )

    # Rapid transactions
    if last_hours < 1:
        minutes = round(last_hours * 60, 0)
        parts.append(
            f"last transaction was only {int(minutes)} minutes ago"
        )

    # Fallback for clean transactions
    if not parts:
        if score < 0.3:
            return "Transaction appears normal — no anomalies detected."
        else:
            return (
                f"Transaction scored {score:.2f} based on ML model analysis. "
                "No specific rule-based anomalies were identified."
            )

    # Decision label
    if score >= 0.85:
        decision = "DECLINED"
    elif score >= 0.65:
        decision = "flagged for REVIEW"
    else:
        decision = "APPROVED"

    # Compose
    explanation = ". ".join(parts) + "."
    explanation = explanation[0].upper() + explanation[1:]
    explanation += f" Decision: {decision} (risk score: {score:.2f})."

    return explanation


# ------------------------------------
# MCP Tool
# ------------------------------------

@mcp.tool()
def explain_fraud_decision(
    transaction_json: str,
    customer_history_json: str,
    score: float,
    triggered_rules_json: str = "[]",
) -> str:
    """
    Generate a human-readable explanation for a fraud scoring decision.

    Args:
        transaction_json: JSON string with transaction data
        customer_history_json: JSON string with customer history
        score: final combined risk score (0.0 to 1.0)
        triggered_rules_json: JSON list of triggered rule names

    Returns: JSON with 'explanation' field
    """
    transaction = json.loads(transaction_json)
    history = json.loads(customer_history_json)
    triggered = json.loads(triggered_rules_json)

    explanation = _generate_explanation(transaction, history, score, triggered)
    return json.dumps({"explanation": explanation})


# ------------------------------------
# Entry Point
# ------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
