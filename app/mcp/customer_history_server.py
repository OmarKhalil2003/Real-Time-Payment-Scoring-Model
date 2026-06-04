"""
MCP Server 1: Customer History Service

Provides historical customer behavior to the fraud scoring engine.
The scoring service queries this MCP server instead of directly accessing
customer databases, demonstrating indirect communication via MCP.

MCP Tool: get_customer_history(customer_id)
Returns: total_transactions, average_amount, usual_country,
         previous_fraud_flags, last_transaction_hours
"""

import json
import hashlib
import random
from mcp.server.fastmcp import FastMCP

# ------------------------------------
# MCP Server Setup
# ------------------------------------

mcp = FastMCP("customer-history-service")

# ------------------------------------
# Simulated Customer Data Store
# ------------------------------------
# Uses deterministic seeding based on customer_id hash to generate
# consistent, repeatable customer profiles without an external database.

COUNTRIES = ["Egypt", "Saudi Arabia", "UAE", "Jordan", "Turkey"]


def _generate_customer_profile(customer_id: str) -> dict:
    """
    Generate a deterministic customer profile based on customer_id.
    The same customer_id always produces the same profile.
    """
    seed = int(hashlib.sha256(customer_id.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)

    usual_country = rng.choice(COUNTRIES)
    total_transactions = rng.randint(50, 2000)
    average_amount = round(rng.uniform(50, 800), 2)
    previous_fraud_flags = rng.choices([0, 0, 0, 0, 1, 2], weights=[50, 20, 15, 10, 4, 1])[0]
    last_transaction_hours = round(rng.uniform(0.1, 72), 1)

    return {
        "customer_id": customer_id,
        "total_transactions": total_transactions,
        "average_amount": average_amount,
        "usual_country": usual_country,
        "previous_fraud_flags": previous_fraud_flags,
        "last_transaction_hours": last_transaction_hours,
    }


# ------------------------------------
# MCP Tool
# ------------------------------------

@mcp.tool()
def get_customer_history(customer_id: str) -> str:
    """
    Retrieve historical behavior profile for a customer.

    Returns JSON with:
    - total_transactions: lifetime transaction count
    - average_amount: average transaction amount
    - usual_country: most common transaction country
    - previous_fraud_flags: count of prior fraud flags
    - last_transaction_hours: hours since last transaction
    """
    profile = _generate_customer_profile(customer_id)
    return json.dumps(profile)


# ------------------------------------
# Entry Point
# ------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
