"""Ops Assistant (RAG) and AI-tool guardrails."""
from pathlib import Path

import pandas as pd
import pytest

from qa_lib.rag import load_sections, unsupported_numbers
from qa_lib.redact import Redactor

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def handbook():
    return load_sections(ROOT / "docs" / "orion_ops_handbook.txt")


@pytest.fixture(scope="module")
def qa_log():
    return pd.read_csv(ROOT / "ai" / "ops_assistant_qa_log.csv", dtype=str, keep_default_na=False)


# ---- EXAMPLES -------------------------------------------------------------------
@pytest.mark.ai
def test_every_answer_cites_a_real_section(qa_log, handbook):
    cited = set(qa_log["source_cited"])
    assert cited <= set(handbook) | {"none"}


@pytest.mark.ai
def test_redaction_is_consistent():
    r = Redactor()
    out = r.redact("C007 on 10.24.7.15 and C007 again from etl01.orion.internal")
    assert out == "CUST_001 on IP_001 and CUST_001 again from HOST_001"
