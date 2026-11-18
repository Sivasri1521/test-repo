# Orion Retail API: contract (R1.0)

Base URL: `http://localhost:8000`. Start the API with `python api/server.py` after the pipeline has built `orion.db`.

## Rules for every endpoint

- Every response is JSON, with `Content-Type: application/json`, including errors.
- Errors have the body `{"error": "<message>"}` and one of these status codes:

  | Code | When |
  |---|---|
  | 400 | Input is missing, malformed or out of range |
  | 404 | The resource or the endpoint doesn't exist |
  | 409 | A status change that BR-05 doesn't allow |
  | 500 | Never expected. If it happens, the body is still the JSON error format and shows no internal details |

- No response ever contains Restricted data: customer names, emails or birth dates (handbook S11).
- Business rules are the ones in `docs/BRD_orion.md`.

## Endpoints

### GET /health
`200 {"status": "ok"}`

### GET /api/discounts/senior?age={age}
Senior discount, BR-03. `age` is an integer from 0 to 120.
`200 {"age": 65, "discount_pct": 10}`. `400` if `age` is missing, not an integer, or outside 0 to 120.

### GET /api/discounts/order?premium={true|false}&amount={amount}
Order discount, BR-04. `amount` is in rupees.
`200 {"premium": true, "amount": 15000.0, "discount_pct": 20}`.
`400` if `premium` isn't `true` or `false`, or `amount` is missing, not a number, or negative.

### GET /api/orders/{order_id}
One order as reported (from `fact_sales`).
`200 {"order_id", "order_date", "customer_id", "region", "product_id", "category", "qty", "amount", "status"}`.
Orders whose customer is unknown are still returned (BR-09). `404` if there is no such order; rejected orders are not
reported, so they return 404 too.

### POST /api/orders/{order_id}/status
Body: `{"status": "<new status>"}`. Moves an order to a new status, following BR-05.
`200 {"order_id", "previous_status", "status"}`.
`400` if the body isn't JSON, `status` is missing, or `status` isn't one of
PLACED, CONFIRMED, PACKED, SHIPPED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED.
`404` if there is no such order. `409` if BR-05 doesn't allow the move.
Changes are held in memory only, not written to `orion.db`. They are cleared when the API restarts, or by
`POST /api/test/reset`.

### GET /api/customers/{customer_id}
The customer's current version.
`200` with exactly these fields: `{"customer_id", "region", "segment_name", "start_date"}`.
`404` if there is no such customer or no current version (for example a closed account).

### GET /api/dashboard
`200 {"regions": [{"region", "total_orders", "total_revenue", "avg_order_value"}, ...]}`: the same figures as
`report_sales_dashboard`.

### POST /api/test/reset
Test helper. Clears status changes made through the API. `200 {"reset": true}`.
