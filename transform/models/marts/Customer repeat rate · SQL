-- customer_repeat_rate.sql
-- Share of customers with more than one invoice. A single-number
-- health metric, easy to chart over time as the pipeline accumulates
-- more days of history.

with orders_per_customer as (
    select
        customer_id,
        count(distinct invoice_no) as invoice_count
    from {{ ref('fact_sales') }}
    group by 1
)

select
    count(*)                                            as total_customers,
    sum(case when invoice_count > 1 then 1 else 0 end)  as repeat_customers,
    round(
        sum(case when invoice_count > 1 then 1 else 0 end) * 1.0 / count(*),
        4
    ) as repeat_rate
from orders_per_customer