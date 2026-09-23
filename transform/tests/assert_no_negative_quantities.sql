-- A singular dbt test fails if this query returns any rows.
-- Belt-and-braces check: stg_orders_clean already filters these out,
-- but this catches a regression if that filter is ever loosened.

select *
from {{ ref('fact_sales') }}
where quantity <= 0 or unit_price <= 0