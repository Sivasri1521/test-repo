import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from qa_lib import evidence as ev

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def cfg():
    return json.loads((ROOT / "config" / "config.json").read_text())


@pytest.fixture(scope="session")
def conn(cfg):
    db = ROOT / cfg["database"]
    if not db.exists():
        pytest.exit("orion.db not found - run: python pipeline/run_pipeline.py", returncode=2)
    c = sqlite3.connect(db)
    yield c
    c.close()


@pytest.fixture(scope="session")
def source(cfg):
    """Read a source CSV exactly as delivered (all text)."""
    def _read(name):
        return pd.read_csv(ROOT / cfg["source_dir"] / name, dtype=str, keep_default_na=False)
    return _read


@pytest.fixture
def evidence(cfg, request):
    """evidence(df, 'label') -> saves reports/evidence/<test>__<label>.csv and prints the path."""
    def _save(df, label="rows"):
        path = ev.save(df, f"{request.node.name}__{label}", ROOT / cfg["evidence_dir"])
        print(f"evidence: {path} ({len(df)} rows)")
        return path
    return _save
