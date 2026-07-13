select
    transaction_id,
    customer_id,
    amount,
    country,
    feature_1,
    feature_2,
    feature_3,
    event_time,
    ingested_at
from {{ source('operational', 'operational_transactions') }}
