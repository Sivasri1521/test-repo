"""Key-level reconciliation between two systems (pandas). For millions of rows use the PySpark
version in qa_lib/reconcile_spark.py - same logic, same output columns."""
import pandas as pd


def reconcile(df_a, df_b, key, value, tolerance=0.01, label_a="A", label_b="B"):
    """Full outer join on key; classify every key as MATCH, AMOUNT_MISMATCH, MISSING_IN_<B>, MISSING_IN_<A>."""
    m = df_a[[key, value]].merge(df_b[[key, value]], on=key, how="outer",
                                 suffixes=(f"_{label_a}", f"_{label_b}"), indicator=True)
    va, vb = f"{value}_{label_a}", f"{value}_{label_b}"

    def classify(r):
        if r["_merge"] == "left_only":
            return f"MISSING_IN_{label_b}"
        if r["_merge"] == "right_only":
            return f"MISSING_IN_{label_a}"
        return "MATCH" if abs(r[va] - r[vb]) <= tolerance else "AMOUNT_MISMATCH"

    m["result"] = m.apply(classify, axis=1)
    return m.drop(columns="_merge")


def summary(result_df):
    return result_df["result"].value_counts().to_dict()
