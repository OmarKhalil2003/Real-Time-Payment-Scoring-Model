select
    row_number() over (order by country) as country_key,
    country as country_code,
    country as country_name
from (
    select distinct country
    from {{ ref('int_transactions_enriched') }}
    where country is not null
) c
