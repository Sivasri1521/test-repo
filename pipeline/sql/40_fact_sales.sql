-- Silver: fact_sales, one row per order. STTM rows S-FCT-01..04
drop table if exists fact_sales;
create table fact_sales as
select
    o.order_id,
    o.order_date,
    coalesce(c.customer_key, -1) as customer_key,
    o.customer_id,
    coalesce(c.region, 'Unknown') as region,
    o.product_id,
    p.category,
    o.qty,
    o.amount,
    o.status,
    o.batch_id
from silver_orders o
left join dim_customer c
  on c.customer_id = o.customer_id
 and c.is_current = 'Y'
left join raw_products p
  on p.product_id = o.product_id;
