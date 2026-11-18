-- Silver: typed, cleaned orders. Source: raw_orders. STTM rows S-ORD-01..07 and S-REJ-01, handbook S5
drop view if exists orders_checked;
create temp view orders_checked as
select r.*,
       case
            when r.order_id in (select order_id from raw_orders group by order_id having count(*) > 1) then 'DUPLICATE_KEY'
            when date(r.order_date) is null or date(r.order_date) <> r.order_date then 'INVALID_DATE'
            when r.product_id not in (select product_id from raw_products) then 'UNKNOWN_PRODUCT'
       end as reject_reason
from raw_orders r;

drop table if exists rejects;
create table rejects as
select order_id, order_date, customer_id, product_id, qty, unit_price, status, batch_id, load_ts, reject_reason
from orders_checked
where reject_reason is not null;

drop table if exists silver_orders;
create table silver_orders as
select
    order_id,
    date(order_date, '+1 day') as order_date,
    nullif(trim(customer_id), '') as customer_id,
    product_id,
    cast(qty as integer) as qty,
    cast(unit_price as real) as unit_price,
    round(cast(qty as integer) * cast(unit_price as real), 2) as amount,
    status,
    batch_id,
    load_ts
from orders_checked
where reject_reason is null and status in ('DELIVERED', 'CANCELLED');
