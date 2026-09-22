-- dim_product.sql
-- One row per stock_code. The source dataset has no category column,
-- so we derive a rough one from keywords in the description - simple,
-- but enough to demonstrate a dimension that isn't just a passthrough.

with base as (
    select
        stock_code,
        description,
        min(invoice_date) as first_seen_date
    from {{ ref('stg_orders_clean') }}
    group by 1, 2
),

deduped as (
    -- some stock_codes have multiple description spellings over time;
    -- keep the most recent description per code
    select
        stock_code,
        description,
        first_seen_date,
        row_number() over (
            partition by stock_code order by first_seen_date desc
        ) as rn
    from base
)

select
    stock_code as product_id,
    description,
    first_seen_date,
    case
        when lower(description) like '%christmas%' then 'Seasonal'
        when lower(description) like '%light%' then 'Lighting'
        when lower(description) like '%bag%' then 'Bags'
        when lower(description) like '%card%' then 'Cards & Stationery'
        when lower(description) like '%mug%' or lower(description) like '%cup%' then 'Kitchenware'
        else 'General'
    end as category
from deduped
where rn = 1