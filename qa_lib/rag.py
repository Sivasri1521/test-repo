"""Helpers for checking Ops Assistant answers against the handbook (Rahul & Basudev, 3 Nov).
These are aids, not a judge: the call on 'grounded' stays with the tester."""
import re
from pathlib import Path


def load_sections(handbook_path):
    """Return {'S1': 'text', ...} from the handbook."""
    text = Path(handbook_path).read_text(encoding="utf-8")
    parts = re.split(r"^(S\d+)\s", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def numbers_in(text):
    """All numbers in a text, normalised ('0.5%' -> '0.5', '1,000' -> '1000')."""
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}


def unsupported_numbers(answer, source_text):
    """Numbers the answer states that the cited section never mentions: a strong hint of number drift
    or an invented fact. An empty set does NOT prove the answer is grounded."""
    return numbers_in(answer) - numbers_in(source_text)
