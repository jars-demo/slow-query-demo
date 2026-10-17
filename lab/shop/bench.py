"""Time every page's query, count the statements it sends, and show its plan."""

import sqlite3
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass

from . import queries as q
from .plan import explain, problems


@dataclass(frozen=True)
class Case:
    name: str
    run: Callable[[sqlite3.Connection], object]
    sql: str
    params: tuple
    # Guarded cases must never full scan or sort; `python -m shop check` fails if they do.
    guarded: bool = True


CASES = [
    Case("recent_orders", lambda c: q.recent_orders(c, 42), q.RECENT_ORDERS, (42,)),
    Case(
        "revenue_since",
        lambda c: q.revenue_since(c, "refunded", "2026-06-01"),
        q.REVENUE_SINCE,
        ("refunded", "2026-06-01"),
    ),
    Case("report_n_plus_one", lambda c: q.report_n_plus_one(c, "NG"), q.TOTALS_FOR, (1,)),
    Case("report", lambda c: q.report(c, "NG"), q.REPORT, ("NG",)),
    Case(
        "page_offset",
        lambda c: q.page_offset(c, page=5_000),
        q.PAGE_OFFSET,
        (20, 100_000),
        guarded=False,  # deep OFFSET always walks the skipped rows; chapter 06 is about why
    ),
    Case(
        "page_after",
        lambda c: q.page_after(c, ("2025-11-10 00:00:00", 0)),
        q.PAGE_AFTER,
        ("2025-11-10 00:00:00", 0, 20),
    ),
]


@dataclass(frozen=True)
class Measurement:
    name: str
    ms: float
    statements: int
    plan: list[str]
    problems: list[str]
    guarded: bool


def statements(conn: sqlite3.Connection, run: Callable[[sqlite3.Connection], object]) -> int:
    sent: list[str] = []
    conn.set_trace_callback(sent.append)
    try:
        run(conn)
    finally:
        conn.set_trace_callback(None)
    return len(sent)


def timed(
    conn: sqlite3.Connection,
    run: Callable[[sqlite3.Connection], object],
    runs: int,
    latency_ms: float = 0,
) -> float:
    """Median milliseconds over up to `runs` runs, stopping early once a second has been spent.

    `latency_ms` waits that long before every statement, like a database across a network.
    """
    if latency_ms:
        conn.set_trace_callback(lambda _: time.sleep(latency_ms / 1000))
    try:
        samples: list[float] = []
        budget = time.perf_counter() + 1.0
        while len(samples) < runs and (not samples or time.perf_counter() < budget):
            started = time.perf_counter()
            run(conn)
            samples.append((time.perf_counter() - started) * 1000)
        return statistics.median(samples)
    finally:
        conn.set_trace_callback(None)


def measure(conn: sqlite3.Connection, runs: int = 5, latency_ms: float = 0) -> list[Measurement]:
    results = []
    for case in CASES:
        plan = explain(conn, case.sql, case.params)
        results.append(
            Measurement(
                case.name,
                timed(conn, case.run, runs, latency_ms),
                statements(conn, case.run),
                plan,
                problems(plan),
                case.guarded,
            )
        )
    return results
