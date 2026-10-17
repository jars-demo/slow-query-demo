"""Read SQLite's query plan, and spot the two steps that make a query slow."""

import re
import sqlite3

# "SCAN orders" reads every row of the table. "SCAN orders USING INDEX ..." walks an index in
# order, which can be fine. "USE TEMP B-TREE" means the rows had to be sorted after reading.
FULL_SCAN = re.compile(r"^SCAN \w+$")
TEMP_SORT = "USE TEMP B-TREE"


def explain(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[str]:
    rows = conn.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
    return [row[3] for row in rows]  # (id, parent, notused, detail)


def problems(plan: list[str]) -> list[str]:
    """The steps of a plan that read the whole table or sort after the fact."""
    return [step for step in plan if FULL_SCAN.match(step.strip()) or TEMP_SORT in step]
