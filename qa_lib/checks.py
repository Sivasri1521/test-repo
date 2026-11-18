"""SQL-based data checks. Each function returns a DataFrame of offending rows (empty = pass),
so a test can assert on it AND save it as evidence."""
import pandas as pd


def q(conn, sql, params=None):
    return pd.read_sql(sql, conn, params=params)


def row_count(conn, table, where="1=1"):
    return conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]


def count_diff_pct(source_count, target_count):
    """Percentage of rows lost (+) or gained (-) between two layers."""
    if source_count == 0:
        return 0.0
    return round((source_count - target_count) * 100.0 / source_count, 4)


def except_both_ways(conn, sql_a, sql_b):
    """Set-based comparison: rows in A not in B, and rows in B not in A."""
    a_minus_b = q(conn, f"{sql_a} EXCEPT {sql_b}")
    b_minus_a = q(conn, f"{sql_b} EXCEPT {sql_a}")
    return a_minus_b, b_minus_a


def duplicates(conn, table, keys, where="1=1"):
    k = ", ".join(keys)
    return q(conn, f"SELECT {k}, COUNT(*) AS cnt FROM {table} WHERE {where} GROUP BY {k} HAVING COUNT(*) > 1")


def nulls(conn, table, column):
    return q(conn, f"SELECT * FROM {table} WHERE {column} IS NULL OR TRIM({column}) = ''")


def orphans(conn, child, child_key, parent, parent_key):
    return q(conn, f"""SELECT c.* FROM {child} c LEFT JOIN {parent} p ON c.{child_key} = p.{parent_key}
                      WHERE p.{parent_key} IS NULL AND c.{child_key} IS NOT NULL""")


def invalid_values(conn, table, column, allowed):
    placeholders = ",".join("?" for _ in allowed)
    return q(conn, f"SELECT * FROM {table} WHERE {column} NOT IN ({placeholders}) OR {column} IS NULL",
             params=list(allowed))


def scd2_gaps_overlaps(conn, table, key, start="start_date", end="end_date"):
    """Each version's end_date must equal the next version's start_date (Nilabja, 14 Oct, TC6)."""
    return q(conn, f"""
        SELECT * FROM (
            SELECT {key}, {start}, {end},
                   LEAD({start}) OVER (PARTITION BY {key} ORDER BY {start}, {end}) AS next_start
            FROM {table})
        WHERE next_start IS NOT NULL AND next_start <> {end}""")


def multiple_current(conn, table, key, flag="is_current"):
    return q(conn, f"SELECT {key}, COUNT(*) AS current_rows FROM {table} WHERE {flag}='Y' GROUP BY {key} HAVING COUNT(*) > 1")
