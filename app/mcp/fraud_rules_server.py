"""
MCP Server 2: Fraud Rules Engine

Provides dynamic fraud rules evaluation without modifying scoring code.
Rules can be updated independently of the scoring service, demonstrating
loose coupling via MCP.

MCP Tool: evaluate_risk_rules(transaction_json)
Input: JSON string with transaction data + customer history
Returns: risk_score (0-100), triggered_rules list
"""

import json
from mcp.server.fastmcp import FastMCP

# ------------------------------------
# MCP Server Setup
# ------------------------------------

mcp = FastMCP("fraud-rules-engine")


# ------------------------------------
# Rule Definitions
# ------------------------------------

def _apply_rules(transaction: dict, history: dict) -> dict:
    """
    Evaluate a set of dynamic fraud rules against a transaction
    combined with customer history context.

    Each rule independently contributes to a cumulative risk score.
    """
    risk = 0
    triggered = []

    amount = transaction.get("amount", 0)
    country = transaction.get("country", "")
    avg_amount = history.get("average_amount", 0)
    usual_country = history.get("usual_country", "")
    fraud_flags = history.get("previous_fraud_flags", 0)
    last_hours = history.get("last_transaction_hours", 999)

    # Rule 1: High transaction amount
    if amount > 3000:
        risk += 20
        triggered.append("high_amount")

    # Rule 2: Foreign country (geographic anomaly)
    if country and usual_country and country != usual_country:
        risk += 30
        triggered.append("foreign_country")

    # Rule 3: Previous fraud history
    if fraud_flags > 0:
        risk += 25
        triggered.append("previous_fraud_flags")

    # Rule 4: Amount significantly exceeds average
    if avg_amount > 0 and amount > 10 * avg_amount:
        risk += 25
        triggered.append("amount_spike")

    # Rule 5: Rapid successive transactions
    if last_hours < 1:
        risk += 10
        triggered.append("rapid_transactions")

    # Cap risk at 100
    risk = min(risk, 100)

    return {
        "risk_score": risk,
        "triggered_rules": triggered,
    }


# ------------------------------------
# MCP Tool
# ------------------------------------

@mcp.tool()
def evaluate_risk_rules(transaction_json: str) -> str:
    """
    Evaluate fraud rules against a transaction with customer context.

    Input: JSON string containing:
        - transaction: {amount, country, ...}
        - customer_history: {average_amount, usual_country, previous_fraud_flags, ...}

    Returns JSON with:
        - risk_score: cumulative risk (0-100)
        - triggered_rules: list of rule names that fired
    """
    data = json.loads(transaction_json)
    transaction = data.get("transaction", {})
    history = data.get("customer_history", {})

    result = _apply_rules(transaction, history)
    return json.dumps(result)


# ------------------------------------
# Entry Point
# ------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
