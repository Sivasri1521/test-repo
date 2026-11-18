-- Silver: payments from system A and ledger from system B, typed. STTM row S-PAY-01, handbook S5
drop table if exists payments_quarantine;
create table payments_quarantine as
select *, 'NULL_CUSTOMER_REF' as quarantine_reason
from raw_payments_a
where trim(cust_id) = '';

drop table if exists silver_payments;
create table silver_payments as
select txn_id, order_id, nullif(trim(cust_id), '') as cust_id,
       round(cast(amount as real), 0) as amount, status, batch_id, load_ts
from raw_payments_a
where trim(cust_id) <> '' and status <> 'PENDING';

drop table if exists silver_ledger;
create table silver_ledger as
select txn_id, order_id, cast(amount as real) as amount, batch_id, load_ts
from raw_ledger_b;
