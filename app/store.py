"""Orion store business logic (system under test).

Requirements: docs/BRD_orion.md  (BR-03 senior discount, BR-04 order discount, BR-05 status flow)
"""

ORDER_FLOW = ["PLACED", "CONFIRMED", "PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]


def can_transition(source_status: str, target: str) -> bool:
    """BR-05: an order moves forward one step at a time; CANCELLED is allowed before SHIPPED."""
    if target == "CANCELLED":
        return source_status in ("PLACED", "CONFIRMED", "PACKED")
    if source_status not in ORDER_FLOW or target not in ORDER_FLOW:
        return False
    pos_from, pos_to = ORDER_FLOW.index(source_status), ORDER_FLOW.index(target)
    return pos_to == pos_from + 1



def order_discount_pct(is_premium: bool, purchase_amount: float) -> int:
    """BR-04 decision table: premium x purchase above Rs 10,000."""
    if purchase_amount <= 0:
        raise ValueError("purchase amount cannot be negative")
    above_10k = purchase_amount > 10000
    if is_premium and above_10k:
        return 15
    if is_premium and not above_10k:
        return 10
    if not is_premium and above_10k:
        return 5
    return 0


def senior_discount_pct(age: int) -> int:
    """BR-03: customers aged 60 and above get a 10% senior discount."""
    if age < 0 or age > 120:
        raise ValueError("age out of range")
    if age >= 65:
        return 10
    return 0