"""Save failing rows as CSV evidence so a defect report never needs a follow-up question."""
from pathlib import Path


def save(df, name, evidence_dir):
    Path(evidence_dir).mkdir(parents=True, exist_ok=True)
    path = Path(evidence_dir) / f"{name}.csv"
    df.to_csv(path, index=False)
    return str(path)
