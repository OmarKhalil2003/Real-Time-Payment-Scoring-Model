select
    row_number() over (order by merchant_id) as merchant_key,
    merchant_id,
    merchant_name,
    merchant_category as category,
    country
from (
    select
        'UNKNOWN'::text as merchant_id,
        'Unknown Merchant'::text as merchant_name,
        'unknown'::text as merchant_category,
        'Unknown'::text as country
) seed
where false
