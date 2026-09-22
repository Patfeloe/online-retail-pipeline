-- fact_sales.sql
-- One row per order line item. Grain: invoice_no + stock_code.

select
    o.invoice_no,
    o.stock_code            as product_id,
    o.customer_id,
    o.invoice_date_day      as date_id,
    o.quantity,
    o.unit_price,
    o.line_total
from {{ ref('stg_orders_clean') }} o