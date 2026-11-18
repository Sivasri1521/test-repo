"""Store business rules in app/store.py."""
import pytest

from app.store import can_transition, order_discount_pct, senior_discount_pct


# ---- EXAMPLE (equivalence partitioning): one value per partition -----------------
@pytest.mark.app
@pytest.mark.smoke
@pytest.mark.parametrize("age, expected", [(30, 0), (75, 10)])
def test_senior_discount_partitions(age, expected):
    assert senior_discount_pct(age) == expected


@pytest.mark.app
def test_invalid_age_rejected():
    with pytest.raises(ValueError):
        senior_discount_pct(-1)
