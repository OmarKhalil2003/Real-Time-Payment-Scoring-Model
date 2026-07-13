select
    row_number() over (order by customer_id) as customer_key,
    customer_id,
    customer_id as full_name,
    null::text as email,
    max(country) as country,
    min(event_time) as valid_from,
    null::timestamp as valid_to,
    true as is_current
from {{ ref('int_transactions_enriched') }}
group by customer_id
