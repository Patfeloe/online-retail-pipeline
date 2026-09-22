-- dim_date.sql
-- Standard date dimension, generated from the range of dates actually
-- present in the cleaned orders rather than a fixed calendar table.

with bounds as (
    select
        min(invoice_date_day) as min_date,
        max(invoice_date_day) as max_date
    from {{ ref('stg_orders_clean') }}
),

spine as (
    select unnest(generate_series(
        (select min_date from bounds),
        (select max_date from bounds),
        interval '1 day'
    )) as date_day
)

select
    date_day                              as date_id,
    date_day,
    extract(year from date_day)           as year,
    extract(month from date_day)          as month,
    extract(day from date_day)            as day,
    extract(dow from date_day)            as day_of_week,
    strftime(date_day, '%A')              as day_name,
    strftime(date_day, '%B')              as month_name
from spine