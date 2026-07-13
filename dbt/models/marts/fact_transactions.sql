with tx as (
    select * from {{ ref('int_transactions_enriched') }}
),
customers as (
    select * from {{ ref('dim_customer') }}
),
countries as (
    select * from {{ ref('dim_country') }}
),
times as (
    select * from {{ ref('dim_time') }}
)
select
    row_number() over (order by tx.event_time) as fact_id,
    tx.transaction_id,
    c.customer_key,
    null::int as merchant_key,
    null::int as card_key,
    co.country_key,
    t.time_key,
    'purchase'::text as event_type,
    tx.amount,
    'USD'::text as currency,
    null::text as payment_method,
    null::text as device,
    case when tx.is_fraud then 1 else 0 end as fraud_label,
    tx.score,
    tx.prediction,
    tx.status,
    tx.reason,
    'v1.0'::text as model_version,
    tx.is_fraud,
    tx.event_time,
    current_timestamp as loaded_at
from tx
left join customers c on tx.customer_id = c.customer_id
left join countries co on tx.country = co.country_code
left join times t on date_trunc('day', tx.event_time)::date = t.full_date
