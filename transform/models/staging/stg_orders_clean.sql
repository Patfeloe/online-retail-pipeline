-- stg_orders_clean.sql
-- Cleans the raw staging table: drops cancelled invoices (they start
-- with "C" in this dataset), drops rows with no customer_id, and
-- filters out non-positive quantities/prices so downstream marts
-- don't have to repeat this logic.

select
    invoice_no,
    stock_code,
    description,
    quantity,
    invoice_date,
    cast(invoice_date as date)      as invoice_date_day,
    unit_price,
    customer_id,
    country,
    quantity * unit_price           as line_total
from {{ source('raw', 'stg_orders') }}
where customer_id is not null
    and customer_id != 'nan'
    and left(invoice_no, 1) != 'C'   -- cancelled invoices
    and quantity > 0
    and unit_price > 0