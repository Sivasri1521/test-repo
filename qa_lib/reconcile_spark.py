"""Optional PySpark version of qa_lib.reconcile for high volumes (Esra, 28 Oct).
pip install pyspark  (needs Java 17+), or paste into a Databricks notebook."""
from pyspark.sql import functions as F


def reconcile(df_a, df_b, key, value, tolerance=0.01):
    a = df_a.select(key, F.col(value).alias("value_a"))
    b = df_b.select(key, F.col(value).alias("value_b"))
    return (a.join(b, on=key, how="full_outer")
             .withColumn("result",
                F.when(F.col("value_b").isNull(), "MISSING_IN_B")
                 .when(F.col("value_a").isNull(), "MISSING_IN_A")
                 .when(F.abs(F.col("value_a") - F.col("value_b")) <= tolerance, "MATCH")
                 .otherwise("AMOUNT_MISMATCH")))
