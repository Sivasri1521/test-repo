"""Smoke: is the build worth testing? Runs on every commit."""
import pytest

EXPECTED_TABLES = ["raw_orders", "raw_customers_day1", "raw_customers_day2", "raw_products",
                   "raw_payments_a", "raw_ledger_b", "silver_orders", "silver_payments",
                   "dim_customer_scd1", "dim_customer", "fact_sales", "agg_daily_region_sales",
                   "kpi_region_sales"]


@pytest.mark.smoke
@pytest.mark.parametrize("table", EXPECTED_TABLES)
def test_table_exists_and_has_rows(conn, table):
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert n > 0, f"{table} is empty"


@pytest.mark.smoke
def test_dashboard_view_returns_all_regions(conn, cfg):
    regions = {r[0] for r in conn.execute("SELECT region FROM report_sales_dashboard")}
    missing = set(cfg["valid_values"]["region"]) - regions
    assert not missing, f"regions missing from the dashboard: {sorted(missing)}"
