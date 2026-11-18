"""Setup check: run this first, before anything else.

    python check_env.py

Prints PASS or FAIL for each item with a fix.
"""
import importlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_FILES = ["orders.csv", "customers_day1.csv", "customers_day2.csv", "products.csv",
                  "payments_system_a.csv", "ledger_system_b.csv", "load_log.csv", "defect_history.csv"]
results = []


def check(name, ok, fix=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok else f"\n       fix: {fix}"))


check(f"Python {sys.version.split()[0]} is 3.10 or newer", sys.version_info >= (3, 10),
      "install Python 3.10+ from python.org or your software centre")
for mod, label, minimum in [("pandas", "pandas", "2.0"), ("pytest", "pytest", "8.0"), ("pytest_html", "pytest-html", "4.1")]:
    try:
        m = importlib.import_module(mod)
        version = getattr(m, "__version__", "0")
        ok = tuple(int(x) for x in version.split(".")[:2] if x.isdigit()) >= tuple(int(x) for x in minimum.split("."))
        check(f"{label} {version} (needs {minimum}+)", ok, "pip install -r requirements.txt")
    except Exception:
        check(f"{label} importable", False,
              "activate .venv, then: pip install -r requirements.txt  (offline: pip install --no-index --find-links wheels -r requirements.txt)")
check(f"SQLite {sqlite3.sqlite_version} available", True)
try:
    cfg = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
    check("config/config.json loads", True)
except Exception as e:
    cfg = {}
    check("config/config.json loads", False, f"restore config.json from the kit zip ({e})")
src = ROOT / cfg.get("source_dir", "data/source")
missing = [f for f in EXPECTED_FILES if not (src / f).exists()]
check("all 8 source files present in data/source", not missing, f"re-extract the kit zip; missing: {missing}")
try:
    (ROOT / "reports" / "evidence").mkdir(parents=True, exist_ok=True)
    probe = ROOT / "reports" / "evidence" / ".write_test"
    probe.write_text("ok")
    probe.unlink()
    check("reports/evidence is writable", True)
except Exception as e:
    check("reports/evidence is writable", False, f"move the kit out of a read-only or synced folder ({e})")

print()
print("Ready: run ./run.sh (macOS/Linux) or run.bat (Windows)." if all(results)
      else "Fix the FAIL lines above, then run this check again.")
sys.exit(0 if all(results) else 1)
