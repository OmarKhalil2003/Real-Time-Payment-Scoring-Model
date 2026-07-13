select
    (extract(epoch from date_trunc('day', event_time))::bigint / 86400)::int as time_key,
    date_trunc('day', event_time)::date as full_date,
    extract(year from event_time)::int as year,
    extract(quarter from event_time)::int as quarter,
    extract(month from event_time)::int as month,
    extract(day from event_time)::int as day,
    extract(dow from event_time)::int as day_of_week,
    extract(hour from event_time)::int as hour,
    extract(dow from event_time) in (0, 6) as is_weekend
from {{ ref('int_transactions_enriched') }}
group by 1, 2, 3, 4, 5, 6, 7, 8, 9
