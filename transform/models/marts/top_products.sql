-- top_products.sql
-- Best sellers by revenue and by quantity, with category rolled in.

select
    p.product_id,
    p.description,
    p.category,
    sum(f.quantity)      as total_quantity,
    sum(f.line_total)    as total_revenue,
    count(distinct f.invoice_no) as order_count
from {{ ref('fact_sales') }} f
join {{ ref('dim_product') }} p on f.product_id = p.product_id
group by 1, 2, 3
order by total_revenue desc