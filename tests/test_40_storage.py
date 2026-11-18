"""Storage and integrity."""
import pytest

from qa_lib import checks


# ---- EXAMPLE: uniqueness of a key ------------------------------------------------
@pytest.mark.storage
@pytest.mark.smoke
def test_product_id_unique(conn, evidence):
    dups = checks.duplicates(conn, "raw_products", ["product_id"])
    if len(dups):
        evidence(dups)
    assert dups.empty
