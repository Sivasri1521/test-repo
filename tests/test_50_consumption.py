"""Consumption: gold, KPIs and the dashboard."""
import pytest

from qa_lib import checks


# ---- EXAMPLE: report agrees with gold ------------------------------------------------
@pytest.mark.consumption
@pytest.mark.smoke
def test_report_total_matches_gold(conn):
    report = conn.execute("SELECT SUM(total_revenue) FROM report_sales_dashboard").fetchone()[0]
    gold = conn.execute("SELECT SUM(revenue) FROM agg_daily_region_sales").fetchone()[0]
    assert report == pytest.approx(gold, abs=0.01)
    # Passing this proves only that report = gold. It says nothing about whether gold is right.
