-- dim_customer.sql
-- One row per customer, with their first purchase date and the
-- country most recently seen against their ID (a customer only ever
-- had one country in this dataset, but this pattern is where you'd
-- hang SCD Type 2 logic if country could actually change over time).

select
    customer_id,
    min(invoice_date_day) as first_purchase_date,
    max_by(country, invoice_date) as country
from {{ ref('stg_orders_clean') }}
group by 1