# Orion Retail - Order-to-Insight release R1.0 (BRD extract)

Fictional client, for GigaAcademy capstone use. Priorities: P0 must work at go-live, P1 high, P2 medium, P3 low.

## Functional requirements (store)

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Customers register and log in; locked or unverified accounts cannot log in | P0 |
| FR-005 | Customers search and filter products by price range, brand and rating | P1 |
| FR-008 | Cart totals = sum(qty x unit price) - discounts | P0 |
| FR-010 | Checkout applies discounts per BR-03 and BR-04 | P0 |
| FR-012 | Payment by UPI, card, net banking; each payment posts to the accounting ledger | P0 |
| FR-014 | Order status follows BR-05 and is visible to the customer | P1 |
| FR-016 | Customers can cancel an order before it ships | P1 |
| FR-021 | Inventory decrements when an order is confirmed | P2 |

## Data and reporting requirements

| ID | Requirement | Priority |
|---|---|---|
| DR-01 | Nightly load source -> raw -> silver -> gold completes inside the 01:00-05:00 UTC window | P0 |
| DR-02 | No source row is lost silently: every row is loaded, or written to a rejects table with a reason | P0 |
| DR-03 | Customer dimension keeps region and segment history (type 2); name corrections overwrite (type 1) | P0 |
| DR-04 | Payment system and accounting ledger agree at transaction level, not only in total | P0 |
| DR-05 | Regional sales dashboard shows orders, revenue and average order value (AOV) per region | P0 |
| DR-06 | Dashboard figures tie out to source: source = report + rejects + exclusions | P0 |
| DR-07 | The Ops Assistant answers only from the Operations Handbook and says when it doesn't know | P1 |

## Business rules

| ID | Rule |
|---|---|
| BR-03 | Customers **aged 60 and above** get a 10% senior discount |
| BR-04 | Order discount: Premium and purchase > Rs 10,000 -> 20%; Premium and <= Rs 10,000 -> 10%; non-Premium and > Rs 10,000 -> 5%; otherwise 0% |
| BR-05 | Order status moves forward one step: PLACED -> CONFIRMED -> PACKED -> SHIPPED -> OUT_FOR_DELIVERY -> DELIVERED. CANCELLED is allowed only before SHIPPED. No backward moves |
| BR-06 | A closed customer account is kept as inactive (soft delete), never physically removed |
| BR-07 | CANCELLED orders are excluded from revenue, order counts and AOV on the dashboard |
| BR-08 | AOV = total revenue / total orders for the period (never an average of daily averages) |
| BR-09 | Orders whose customer is unknown map to the Unknown customer (customer_key = -1) and still count in totals |
| BR-10 | Products not in the product master are rejected with a reason |

## Definition of done
All P0 requirements tested and traced in the RTM; no open Critical/High defects; tie-out (DR-06) proven; regression pack green in CI; test summary report signed off.
