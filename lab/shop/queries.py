"""The queries a shop's pages run. Each one is slow in its own way until you fix it."""

import sqlite3

# The customer page: their 20 most recent orders.
RECENT_ORDERS = """
SELECT id, status, total_cents, created_at
FROM orders
WHERE customer_id = ?
ORDER BY created_at DESC
LIMIT 20
"""

# The finance dashboard: revenue for one status since a date.
REVENUE_SINCE = """
SELECT count(*), sum(total_cents)
FROM orders
WHERE status = ? AND created_at >= ?
"""

# The country report, two ways: one query per customer (N+1), or one JOIN.
CUSTOMERS_IN = "SELECT id, name FROM customers WHERE country = ? ORDER BY id"
TOTALS_FOR = "SELECT count(*), coalesce(sum(total_cents), 0) FROM orders WHERE customer_id = ?"
REPORT = """
SELECT c.id, c.name, count(o.id), coalesce(sum(o.total_cents), 0)
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE c.country = ?
GROUP BY c.id
ORDER BY c.id
"""

# The orders list, newest first, page by page: by OFFSET, or after the last row you saw.
PAGE_OFFSET = """
SELECT id, created_at, total_cents
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT ? OFFSET ?
"""
PAGE_AFTER = """
SELECT id, created_at, total_cents
FROM orders
WHERE (created_at, id) < (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT ?
"""

Row = tuple
Cursor = tuple[str, int]  # (created_at, id) of the last row on the page


def recent_orders(conn: sqlite3.Connection, customer_id: int) -> list[Row]:
    return conn.execute(RECENT_ORDERS, (customer_id,)).fetchall()


def revenue_since(conn: sqlite3.Connection, status: str, since: str) -> Row:
    return conn.execute(REVENUE_SINCE, (status, since)).fetchone()


def report_n_plus_one(conn: sqlite3.Connection, country: str) -> list[Row]:
    rows = []
    for customer_id, name in conn.execute(CUSTOMERS_IN, (country,)).fetchall():
        count, total = conn.execute(TOTALS_FOR, (customer_id,)).fetchone()
        rows.append((customer_id, name, count, total))
    return rows


def report(conn: sqlite3.Connection, country: str) -> list[Row]:
    return conn.execute(REPORT, (country,)).fetchall()


def page_offset(conn: sqlite3.Connection, page: int, size: int = 20) -> list[Row]:
    return conn.execute(PAGE_OFFSET, (size, page * size)).fetchall()


def page_after(conn: sqlite3.Connection, cursor: Cursor | None, size: int = 20) -> list[Row]:
    if cursor is None:
        return conn.execute(PAGE_OFFSET, (size, 0)).fetchall()
    return conn.execute(PAGE_AFTER, (*cursor, size)).fetchall()
