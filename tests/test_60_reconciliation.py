"""Payments (system A) vs accounting ledger (system B)."""
import pandas as pd
import pytest

from qa_lib.reconcile import reconcile


@pytest.fixture(scope="module")
def recon(conn, cfg):
    # System A as delivered: every payment, including any the pipeline quarantines from silver
    a = pd.read_sql("SELECT txn_id, CAST(amount AS REAL) AS amount FROM raw_payments_a", conn)
    b = pd.read_sql("SELECT txn_id, amount FROM silver_ledger", conn)
    return reconcile(a, b, "txn_id", "amount", cfg["amount_tolerance"])


# ---- EXAMPLE: control totals (L2) ------------------------------------------------
@pytest.mark.reconciliation
def test_control_totals_agree(conn):
    a = conn.execute("SELECT ROUND(SUM(CAST(amount AS REAL)),2) FROM raw_payments_a").fetchone()[0]
    b = conn.execute("SELECT ROUND(SUM(amount),2) FROM silver_ledger").fetchone()[0]
    assert a == pytest.approx(b, abs=0.01)


@pytest.mark.reconciliation
def test_reconciliation_runs(recon):
    assert set(recon["result"]) <= {"MATCH", "AMOUNT_MISMATCH", "MISSING_IN_A", "MISSING_IN_B"}
