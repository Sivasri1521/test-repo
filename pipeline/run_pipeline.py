"""Orion Retail nightly pipeline: source CSV -> raw -> silver -> gold -> report.

Run:  python pipeline/run_pipeline.py
Builds orion.db (SQLite) in the project root. Re-running rebuilds it from scratch.

This is the system under test. Read it the way you'd read client code:
compare what it does with docs/STTM_orion.csv and docs/BRD_orion.md.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
SRC = ROOT / CFG["source_dir"]
DB = ROOT / CFG["database"]
SQL = Path(__file__).resolve().parent / "sql"
SEGMENTS = {"P": "Premium", "S": "Standard", "B": "Basic"}


def main():
    if DB.exists():
        DB.unlink()
    db = sqlite3.connect(DB)
    counts = {
        "raw_orders": load_raw(db, "orders.csv", "raw_orders", "B1001"),
        "raw_products": load_raw(db, "products.csv", "raw_products", "B1001"),
        "raw_customers_day1": load_raw(db, "customers_day1.csv", "raw_customers_day1", "B1001"),
        "raw_customers_day2": load_raw(db, "customers_day2.csv", "raw_customers_day2", "B1001"),
        "raw_payments_a": load_raw(db, "payments_system_a.csv", "raw_payments_a", "B1001"),
        "raw_ledger_b": load_raw(db, "ledger_system_b.csv", "raw_ledger_b", "B1001"),
        "raw_load_log": load_raw(db, "load_log.csv", "raw_load_log", "B1001"),
    }
    run_sql(db, "10_silver_orders.sql")
    run_sql(db, "20_silver_payments.sql")
    build_customers(db)
    run_sql(db, "40_fact_sales.sql")
    run_sql(db, "50_gold.sql")
    built = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'raw_%' "
                                        "AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
    for t in built:
        counts[t] = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    db.close()
    print(f"Pipeline complete -> {DB.name}")
    for t, n in counts.items():
        print(f"  {t:<24}{n:>6} rows")


def build_customers(db):
    db.executescript("""
        DROP TABLE IF EXISTS dim_customer_scd1;
        CREATE TABLE dim_customer_scd1 (customer_id TEXT, full_name TEXT, region TEXT, segment_name TEXT,
            account_type TEXT, gender TEXT, birth_date TEXT, is_active TEXT, created_date TEXT, updated_date TEXT);
        DROP TABLE IF EXISTS dim_customer;
        CREATE TABLE dim_customer (customer_key INTEGER PRIMARY KEY AUTOINCREMENT, customer_id TEXT,
            full_name TEXT, region TEXT, segment_name TEXT, account_type TEXT, gender TEXT, birth_date TEXT,
            start_date TEXT, end_date TEXT, is_current TEXT);
    """)
    day1 = pd.read_sql("SELECT * FROM raw_customers_day1", db).to_dict("records")
    day2 = pd.read_sql("SELECT * FROM raw_customers_day2", db).to_dict("records")
    load_scd1(db, day1, None)
    load_scd2(db, day1, CFG["day1_effective_date"], initial=True)
    load_scd1(db, day2, day1)
    load_scd2(db, day2, CFG["day2_effective_date"], initial=False)
    # batch B1004 failed and was retried (see load_log.csv): the type 1 load ran again
    load_scd1(db, day2, day1)


# ------------------------------------------------------------------ customer dimensions
def to_dim_row(src):
    seg = SEGMENTS.get(src["segment_code"], "Unassigned")
    return {
        "customer_id": src["customer_id"],
        "full_name": f"{src['first_name']} {src['last_name']}",
        "region": src["region"],
        "segment_name": seg,
        "account_type": src["gender"],
        "gender": src["account_type"],
        "birth_date": src["birth_date"],
    }


def load_scd2(db, feed, valid_from, initial):
    """Type 2 customer dimension: region and segment changes keep history."""
    cursor = db.cursor()
    incoming = {r["customer_id"]: to_dim_row(r) for r in feed}
    current = {r[0]: r for r in cursor.execute(
        "SELECT customer_id, region, segment_name, customer_key FROM dim_customer WHERE is_current='Y'")}
    insert_version = """INSERT INTO dim_customer (customer_id, full_name, region, segment_name, account_type, gender,
             birth_date, start_date, end_date, is_current) VALUES (?,?,?,?,?,?,?,?,NULL,'Y')"""
    close_version = "UPDATE dim_customer SET end_date=?, is_current='N' WHERE customer_id=? AND is_current='Y'"
    for customer, d in incoming.items():
        row_values = (customer, d["full_name"], d["region"], d["segment_name"], d["account_type"], d["gender"], d["birth_date"], valid_from)
        if customer not in current:
            cursor.execute(insert_version, row_values)
        elif (current[customer][1], current[customer][2]) != (d["region"], d["segment_name"]):
            cursor.execute(close_version, (valid_from, customer))
            cursor.execute(insert_version, row_values[:3] + (current[customer][2],) + row_values[4:])  # new version opens
        else:
            cursor.execute("UPDATE dim_customer SET full_name=? WHERE customer_id=?", (d["full_name"], customer))
    if not initial:
        for customer in set(current) - set(incoming):
            cursor.execute(close_version, (valid_from, customer))
    db.commit()


def load_scd1(db, feed, previous_feed):
    """Type 1 customer dimension: overwrite changes, handle new and missing customers."""
    cursor = db.cursor()
    already_loaded = {r[0] for r in cursor.execute("SELECT customer_id FROM dim_customer_scd1")}
    incoming = {r["customer_id"]: to_dim_row(r) for r in feed}
    previous_ids = {r["customer_id"] for r in previous_feed} if previous_feed is not None else set()
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # changed rows
    for customer, d in incoming.items():
        if customer in already_loaded:
            cursor.execute(
                """UPDATE dim_customer_scd1 SET full_name=?, region=?, segment_name=?, account_type=?,
                   gender=?, birth_date=?, is_active='Y', updated_date=? WHERE customer_id=?""",
                (d["full_name"], d["region"], d["segment_name"], d["account_type"], d["gender"], d["birth_date"], stamp, customer),
            )
    # new rows
    fresh_ids = [customer for customer in incoming if customer not in already_loaded]
    for customer in fresh_ids:
        d = incoming[customer]
        cursor.execute(
            """INSERT INTO dim_customer_scd1 (customer_id, full_name, region, segment_name, account_type,
               gender, birth_date, is_active, created_date, updated_date) VALUES (?,?,?,?,?,?,?,'Y',?,?)""",
            (customer, d["full_name"], d["region"], d["segment_name"], d["account_type"], d["gender"], d["birth_date"], stamp, stamp),
        )
    # customers no longer in the feed
    if previous_feed is not None:
        for customer in (previous_ids | already_loaded) - set(incoming):
            cursor.execute("UPDATE dim_customer_scd1 SET is_active='N', updated_date=? WHERE customer_id=?", (stamp, customer))
    db.commit()


def run_sql(db, name):
    db.executescript((SQL / name).read_text(encoding="utf-8"))


def load_raw(db, csv_name, table, batch_id):
    """Raw layer: land the file as-is (all text) and stamp the load batch + load_ts."""
    frame = pd.read_csv(SRC / csv_name, dtype=str, keep_default_na=False)
    stamp = "load_batch_id" if "batch_id" in frame.columns else "batch_id"
    frame[stamp] = batch_id
    frame["load_ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frame.to_sql(table, db, if_exists="replace", index=False)
    return len(frame)


if __name__ == "__main__":
    main()
