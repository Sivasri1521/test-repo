-- Gold: daily region sales mart and dashboard KPIs. STTM rows G-AGG-01..02, G-KPI-01..03
drop table if exists agg_daily_region_sales;
create table agg_daily_region_sales as
select order_date, region,
       count(distinct customer_id) as orders,
       round(sum(amount), 2) as revenue
from fact_sales
where status not in ('CANCELLED')
  and strftime('%w', order_date) not in ('0', '6')
group by order_date, region;

drop table if exists kpi_region_sales;
create table kpi_region_sales as
select region,
       sum(orders) as total_orders,
       round(sum(revenue), 2) as total_revenue,
       round(sum(revenue) * 1.0 / sum(orders), 0) as avg_order_value
from agg_daily_region_sales
group by region;

-- The dashboard reads straight from gold
drop view if exists report_sales_dashboard;
create view report_sales_dashboard as
select region, total_orders, total_revenue, avg_order_value from kpi_region_sales;
