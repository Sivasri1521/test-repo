# Orion Retail capstone - team kit

GigaAcademy Data Testing Build Program, 2026.   Team: **C2-T08**

You are the QA team for Orion Retail's "Order-to-Insight" release. The client needs a Go/No-Go decision.

> "Finance says the dashboard revenue doesn't match the ledger, a few customers show up in the wrong region,
> and nobody trusts the nightly loads. Tell us what you will test, how long it will take, and whether we can go live."

The kit is a working system with a working test framework. Nothing in it tells you where the problems are.
**Your strategy decides what you find.** Your team's data is your own: other teams' IDs and totals differ.

## 1. Get it running

Needs Python 3.10+. The database is SQLite, built into Python.

```
python check_env.py          checks your setup, prints PASS/FAIL with fixes
Windows:        run.bat      (or: run.bat smoke)
macOS / Linux:  ./run.sh     (or: ./run.sh smoke)
```
The run scripts create a virtual environment, install requirements, run the pipeline into `orion.db`, run the tests
and write `reports/report.html`. Expect 27 passed: these are worked examples. **Every other test is yours to write.**

Manual steps, if you prefer:
```
python -m venv .venv && .venv\Scripts\activate      (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python pipeline/run_pipeline.py
pytest -rs --html=reports/report.html --self-contained-html
```
Useful variants: `pytest -m smoke`, `pytest -m "storage or consumption"`,
`pytest ai/generated_tests -v` (the AI-generated pack).

Browse the data with any SQLite tool (DB Browser for SQLite, the VS Code SQLite extension, DBeaver), or from Python:
`pandas.read_sql("SELECT * FROM fact_sales LIMIT 5", sqlite3.connect("orion.db"))`.

## 2. Where to start

1. Read `docs/BRD_orion.md`, `docs/STTM_orion.csv`, `docs/orion_ops_handbook.txt` and `data/source/defect_history.csv`.
2. Write your strategy in `templates/01_test_strategy.md`: what could hurt Orion most, and how you'll find it first.
3. Write your tests. The files in `tests/` hold worked examples only; add your tests there or in new files.
   **What to test is up to you**: work it out from the BRD, the STTM and the API spec. Nothing tells you where the
   problems are.
4. Test the API with Postman (section 3).
5. For every failing test that shows a real problem, raise a defect (`templates/03_defect_report.md` or the
   GitHub issue form) with evidence and the line in the code that causes it.

## 3. API testing with Postman

The store also has a small API. Its contract is `docs/API_SPEC.md`.

1. Build the database first (`run.bat`, `./run.sh` or `python pipeline/run_pipeline.py`).
2. Start the API: `python api/server.py`. It runs on `http://localhost:8000`; leave that window open.
3. In Postman, **Import** both files in `postman/` (the collection and the environment) and select the
   **Orion local** environment.
4. Run the worked examples, then add your own requests and tests, built from `docs/API_SPEC.md`.
5. When you're done, export the collection back into `postman/`, replacing the starter file.

`POST /api/test/reset` clears status changes between runs. To run the collection from the command line (optional,
needs Node.js): `npx newman run postman/Orion_API.postman_collection.json -e postman/Orion_local.postman_environment.json`.
API problems are defects too: the request and the response are your evidence.

## 4. What's in the box

```
docs/BRD_orion.md            requirements and business rules (FR, DR, BR)
docs/STTM_orion.csv          source-to-target mapping: the spec for every table
docs/orion_ops_handbook.txt  the knowledge base behind the Ops Assistant
docs/AI_POLICY.md            what may and may not go into an AI tool
docs/API_SPEC.md             the API contract
data/source/                 orders, customers (day 1 and day 2), products, payments (system A),
                             ledger (system B), load_log, defect_history. Treat as client production data.
pipeline/run_pipeline.py     the nightly pipeline: source -> raw -> silver -> gold -> report
pipeline/sql/                the SQL behind each layer
app/store.py                 store business logic: discounts and order status
api/server.py                the store API (start it with python api/server.py)
postman/                     Postman collection (worked examples) and environment
qa_lib/                      reusable checks: counts, EXCEPT both ways, duplicates, nulls, orphans,
                             valid values, SCD2 gaps/overlaps, key-level reconciliation (pandas and PySpark),
                             RAG helpers, redaction, evidence capture
tests/                       worked examples by area; your tests go here too
ai/ops_assistant_qa_log.csv  12 answers from the Ops Assistant, to mark
ai/generated_tests/          a test pack an AI assistant wrote: review it
ai/teammate_request.md       an AI guardrails situation to handle
templates/                   team charter, strategy, RTM, defect report, DQ checklist, test summary,
                             AI review log, AI usage log
.github/                     CI pipeline (works; not yet a regression strategy) and a defect issue form
config/config.json           tolerances, valid values, load and extract windows: tests read from here
check_env.py                 setup check
```

## 5. Layers and tables

| Layer | Tables | Built by |
|---|---|---|
| Raw | raw_orders, raw_customers_day1/day2, raw_products, raw_payments_a, raw_ledger_b, raw_load_log | `load_raw()` |
| Silver | silver_orders, silver_payments, silver_ledger, dim_customer_scd1 (type 1), dim_customer (type 2), fact_sales | `sql/10..40`, `build_customers()` |
| Gold | agg_daily_region_sales, kpi_region_sales | `sql/50_gold.sql` |
| Report | report_sales_dashboard (view) | `sql/50_gold.sql` |

## 6. What to deliver

| Deliverable | Where |
|---|---|
| Team charter: members and who owns what | `templates/00_team_charter.md` |
| Test strategy with estimate and predictions | `templates/01_test_strategy.md` |
| RTM covering every P0 requirement | `templates/02_rtm.csv` |
| Your tests | `tests/` (and any `qa_lib/` extensions) |
| API tests | `postman/Orion_API.postman_collection.json`, exported with your requests and tests |
| Defects with evidence | `templates/03_defect_report.md` copies or GitHub issues, evidence in `reports/evidence/` |
| Data quality checklist | `templates/04_dq_checklist.csv` |
| CI with your commit/nightly split | `.github/workflows/data-tests.yml` |
| Ops Assistant log marked | `ai/ops_assistant_qa_log.csv` |
| Review of the AI-generated pack | `templates/06_ai_review_log.md` |
| Reply to the teammate request | `ai/teammate_reply.md` |
| AI usage log | `templates/07_ai_usage_log.md` |
| Test summary, tie-out and Go/No-Go | `templates/05_test_summary_report.md` |

If the documents don't settle something, ask your facilitator (who plays the client) and record the answer as an
assumption in your strategy.

## 7. Rules of the game

- A defect counts only with a failing test (or query), evidence in `reports/evidence/`, and a root cause in the code.
  Your steps to reproduce will be rerun on a clean copy: if it doesn't reproduce, it doesn't count.
- Don't change `pipeline/` or `app/`: you are testing the client's code. Point at the line instead.
- Known defects stay visible in a green pipeline: mark the test `@pytest.mark.xfail(strict=True, reason="DEF-nnn")`.
- A test that passes on a broken system is worse than no test. Ask of every green test: what would make this fail?
  A test that fails on a correct system is just as bad.
- Raising something that is correct per the spec as a defect costs credibility. Raise doubts as questions.
- Evidence files hold keys, not Restricted data (names, emails, birth dates).
- Follow `docs/AI_POLICY.md` and log every AI use in `templates/07_ai_usage_log.md`.
- Extend `qa_lib/` rather than copy-pasting SQL into tests.
- Every artifact carries `Owner: <name>, <OHR>`, and every commit uses your own git identity.

## 8. Questions your strategy has to answer

1. Which three faults would hurt Orion most in production, and how does your plan find them first?
2. Where do you use SQL, pandas or PySpark, and why?
3. What runs on every commit, what runs nightly, what is a one-off investigation?
4. When the report matches gold, what makes you still test it?
5. What would you never paste into an AI tool on this engagement?

## 9. Submitting

Zip the whole folder (including `reports/evidence/`, `templates/`, `ai/` and `postman/`) as `orion_C2-T08.zip`.
Leave out `.venv/` and `orion.db`. If you use a repository, share the link as well.

## Running on Databricks instead
Upload `data/source/*.csv` as tables, port `pipeline/sql/*.sql` (standard SQL: works as-is apart from `DATE()` casts),
and use `qa_lib/reconcile_spark.py` in a notebook. The test ideas don't change.
#   t e s t - r e p o  
 