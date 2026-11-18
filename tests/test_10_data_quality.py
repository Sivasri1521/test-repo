import sqlite3
import pandas as pd

DB = "orion.db"


def test_fact_orders_not_empty():
    conn = sqlite3.connect(DB)

    df = pd.read_sql(
        "SELECT COUNT(*) as cnt FROM fact_sales",
        conn
    )

    conn.close()