"""Transformation: the STTM rules."""
import pytest

from qa_lib import checks


# ---- EXAMPLE: derived field full_name = first_name || ' ' || last_name ----------------
@pytest.mark.transformation
def test_full_name_derivation(conn, evidence):
    expected = "SELECT customer_id, first_name || ' ' || last_name AS full_name FROM raw_customers_day2"
    actual = "SELECT customer_id, full_name FROM dim_customer_scd1 WHERE is_active = 'Y'"
    missing, extra = checks.except_both_ways(conn, expected, actual)
    if len(missing) or len(extra):
        evidence(missing, "expected_not_in_target")
        evidence(extra, "target_not_in_expected")
    assert missing.empty and extra.empty
