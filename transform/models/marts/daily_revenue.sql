-- daily_revenue.sql
-- Revenue by day and by country - the mart you'd point a dashboard at.

select
    d.date_day,
    c.country,
    count(distinct f.invoice_no)   as order_count,
    sum(f.line_total)              as revenue
from {{ ref('fact_sales') }} f
join {{ ref('dim_date') }} d on f.date_id = d.date_id
join {{ ref('dim_customer') }} c on f.customer_id = c.customer_id
group by 1, 2
order by 1, 2