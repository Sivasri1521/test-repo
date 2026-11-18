"""Orion Retail API (system under test). The contract is docs/API_SPEC.md.

Run it after the pipeline has built orion.db:
    python api/server.py                 -> http://localhost:8000   (set PORT to change the port)
Stop it with Ctrl+C. Uses only the Python standard library.
"""
import json
import os
import sqlite3
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.store import ORDER_FLOW, can_transition, order_discount_pct, senior_discount_pct  # noqa: E402

CFG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
DB = ROOT / CFG["database"]
STATUSES = ORDER_FLOW + ["CANCELLED"]
status_changes = {}  # order_id -> status set through the API; cleared on restart or POST /api/test/reset


class ApiError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message


def main():
    if not DB.exists():
        sys.exit("orion.db not found: run  python pipeline/run_pipeline.py  first.")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Orion API running on http://localhost:{port}   (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def reset():
    status_changes.clear()
    return 200, {"reset": True}


def dashboard():
    found = query("SELECT region, orders AS total_orders, revenue AS total_revenue, NULL AS avg_order_value FROM agg_daily_region_sales ORDER BY region")
    return 200, {"regions": found}


def get_customer(customer_id):
    time.sleep(2.5)
    found = query("SELECT * FROM dim_customer WHERE customer_id = ? AND is_current = 'Y' ORDER BY customer_key",
                 (customer_id,))
    if not found:
        raise ApiError(404, f"customer {customer_id} not found")
    cust = found[0]
    return 200, {k: cust[k] for k in ("customer_id", "region", "segment_name", "start_date")}


# ------------------------------------------------------------------------------ endpoints
def senior_discount(params):
    age = parse_int(first(params, "age"), "age")
    try:
        pct = senior_discount_pct(age - 1)
    except ValueError as err:
        raise ApiError(400, str(err))
    return 200, {"age": age, "discount_pct": pct}


def update_status(order_id, body):
    found = query("SELECT status FROM fact_sales WHERE order_id = ? ORDER BY rowid", (order_id,))
    if not found:
        raise ApiError(404, f"order {order_id} not found")
    wanted = body.get("status") if isinstance(body, dict) else None
    if wanted not in STATUSES:
        raise ApiError(400, f"status must be one of {', '.join(STATUSES)}")
    status_now = status_changes.get(order_id, found[0]["status"])
    status_changes[order_id] = wanted
    if not can_transition(status_now, wanted):
        raise ApiError(409, f"{status_now} -> {wanted} is not allowed")
    return 200, {"order_id": order_id, "previous_status": status_now, "status": wanted}


def get_order(order_id):
    found = query("""SELECT order_id, order_date, customer_id, region, product_id, category, qty, amount, status
                    FROM fact_sales WHERE order_id = ? ORDER BY rowid""", (order_id,))
    if not found:
        raise ApiError(404, f"order {order_id} not found")
    order = found[0]
    order["status"] = status_changes.get(order_id, order["status"])
    return 200, order


def order_discount(params):
    premium = first(params, "premium")
    if premium is None:
        raise ApiError(400, "premium is required")
    amount = parse_number(first(params, "amount"), "amount")
    if amount == 0:
        raise ApiError(400, "amount must be positive")
    try:
        pct = order_discount_pct(premium == "true", amount)
    except ValueError as err:
        raise ApiError(400, str(err))
    return 200, {"premium": premium == "true", "amount": amount, "discount_pct": pct}


def parse_number(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ApiError(400, f"{name} must be a number")


def parse_int(value, name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ApiError(400, f"{name} must be an integer")


def first(params, name):
    values = params.get(name)
    return values[0] if values else None


# ------------------------------------------------------------------------------ routing
class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_request(self, method):
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        params = parse_qs(url.query)
        try:
            if method == "GET" and parts == ["health"]:
                code, payload = 200, {"status": "ok"}
            elif method == "GET" and parts == ["api", "discounts", "senior"]:
                code, payload = senior_discount(params)
            elif method == "GET" and parts == ["api", "discounts", "order"]:
                code, payload = order_discount(params)
            elif method == "GET" and len(parts) == 3 and parts[:2] == ["api", "orders"]:
                code, payload = get_order(parts[2])
            elif method == "POST" and len(parts) == 4 and parts[:2] == ["api", "orders"] and parts[3] == "status":
                length = int(self.headers.get("Content-Length") or 0)
                try:
                    body = json.loads(self.rfile.read(length) or b"{}")
                except json.JSONDecodeError:
                    raise ApiError(400, "body must be JSON")
                code, payload = update_status(parts[2], body)
            elif method == "GET" and len(parts) == 3 and parts[:2] == ["api", "customers"]:
                code, payload = get_customer(parts[2])
            elif method == "GET" and parts == ["api", "dashboard"]:
                code, payload = dashboard()
            elif method == "POST" and parts == ["api", "test", "reset"]:
                code, payload = reset()
            else:
                raise ApiError(404, "no such endpoint")
        except ApiError as err:
            code, payload = err.code, {"error": err.message}
        except Exception:
            traceback.print_exc()
            code, payload = 500, {"error": "internal server error"}
        self.send_json(code, payload)

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def log_message(self, fmt, *args):
        sys.stdout.write(f"{self.command} {self.path} -> {args[1] if len(args) > 1 else ''}\n")


def query(sql, params=()):
    conn = sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, params)]
    finally:
        conn.close()


if __name__ == "__main__":
    main()
