"""Ingestion: source file -> raw -> silver."""
import pytest

from qa_lib import checks


# ---- EXAMPLE: L1 row count, source file vs raw table -------------------------------
@pytest.mark.ingestion
@pytest.mark.smoke
@pytest.mark.parametrize("csv_name, table", [
    ("orders.csv", "raw_orders"),
    ("customers_day2.csv", "raw_customers_day2"),
    ("payments_system_a.csv", "raw_payments_a"),
])
def test_raw_count_matches_source_file(source, conn, csv_name, table):
    assert checks.row_count(conn, table) == len(source(csv_name))
