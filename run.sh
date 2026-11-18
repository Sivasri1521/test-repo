#!/usr/bin/env bash
# Orion capstone - one-click run on macOS / Linux / Git Bash
#   ./run.sh          full run (all tests)
#   ./run.sh smoke    smoke tests only
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
if [ -d wheels ]; then
  pip install -q --no-index --find-links wheels -r requirements.txt
else
  pip install -q -r requirements.txt
fi
python pipeline/run_pipeline.py
if [ "$1" = "smoke" ]; then
  pytest -m smoke --html=reports/report.html --self-contained-html || true
else
  pytest -rs --html=reports/report.html --self-contained-html || true
fi
echo "Report: reports/report.html   Evidence: reports/evidence/"
