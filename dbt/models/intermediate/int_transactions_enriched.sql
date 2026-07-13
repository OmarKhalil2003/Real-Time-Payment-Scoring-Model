with scored as (
    select * from {{ ref('stg_scored_transactions') }}
),
ops as (
    select * from {{ ref('stg_operational_transactions') }}
)
select
    coalesce(s.transaction_id, o.transaction_id) as transaction_id,
    coalesce(s.customer_id, o.customer_id) as customer_id,
    coalesce(s.amount, o.amount) as amount,
    coalesce(s.country, o.country) as country,
    s.score,
    s.prediction,
    s.status,
    s.reason,
    s.mcp_risk_score,
    s.triggered_rules,
    s.explanation,
    coalesce(s.event_time, o.event_time) as event_time,
    coalesce(s.processed_at, o.ingested_at) as processed_at,
    case when s.status in ('DECLINED', 'REVIEW') then true else false end as is_flagged,
    case when s.status = 'DECLINED' then true else false end as is_fraud
from scored s
full outer join ops o on s.transaction_id = o.transaction_id
