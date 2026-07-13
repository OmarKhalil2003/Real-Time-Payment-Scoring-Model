select
    transaction_id,
    customer_id,
    amount,
    country,
    score,
    prediction,
    status,
    reason,
    mcp_risk_score,
    triggered_rules,
    explanation,
    created_at as event_time,
    processed_at
from {{ source('operational', 'scored_transactions') }}
