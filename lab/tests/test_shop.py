from pathlib import Path

import pytest

from shop import queries as q
from shop.__main__ import main
from shop.bench import measure, statements
from shop.db import build, read_indexes
from shop.plan import explain, problems

LAB = Path(__file__).resolve().parent.parent
SOLUTION = read_indexes(LAB / "solutions" / "indexes.sql")


@pytest.fixture(scope="module")
def bare():
    return build(customers=200, orders=5_000)


@pytest.fixture(scope="module")
def indexed():
    return build(customers=200, orders=5_000, indexes=SOLUTION)


def test_build_is_the_same_every_time():
    first = build(customers=10, orders=50).execute("SELECT * FROM orders").fetchall()
    second = build(customers=10, orders=50).execute("SELECT * FROM orders").fetchall()

    assert first == second


def test_problems_flags_full_scans_and_temp_sorts_only():
    plan = [
        "SCAN orders",
        "USE TEMP B-TREE FOR ORDER BY",
        "SCAN orders USING INDEX orders_created",
        "SEARCH orders USING INDEX orders_customer_created (customer_id=?)",
    ]

    assert problems(plan) == ["SCAN orders", "USE TEMP B-TREE FOR ORDER BY"]


def test_without_indexes_the_customer_page_scans_and_sorts(bare):
    plan = explain(bare, q.RECENT_ORDERS, (42,))

    assert problems(plan) == plan


def test_the_composite_index_removes_the_scan_and_the_sort(indexed):
    plan = explain(indexed, q.RECENT_ORDERS, (42,))

    assert problems(plan) == []
    assert "orders_customer_created" in plan[0]


def test_indexes_do_not_change_the_answers(bare, indexed):
    assert q.recent_orders(bare, 42) == q.recent_orders(indexed, 42)
    assert q.revenue_since(bare, "paid", "2026-01-01") == q.revenue_since(
        indexed, "paid", "2026-01-01"
    )


def test_the_n_plus_one_report_sends_one_statement_per_customer(bare):
    customers = len(bare.execute(q.CUSTOMERS_IN, ("IN",)).fetchall())

    assert statements(bare, lambda c: q.report_n_plus_one(c, "IN")) == customers + 1
    assert statements(bare, lambda c: q.report(c, "IN")) == 1


def test_the_join_report_matches_the_n_plus_one_report(bare):
    assert q.report(bare, "IN") == q.report_n_plus_one(bare, "IN")


def test_keyset_pages_match_offset_pages(indexed):
    cursor = None
    for page in range(4):
        rows = q.page_after(indexed, cursor)
        assert rows == q.page_offset(indexed, page)
        cursor = (rows[-1][1], rows[-1][0])


def test_with_the_solution_every_guarded_query_is_clean(indexed):
    guarded = [m for m in measure(indexed, runs=1) if m.guarded]

    assert [(m.name, m.problems) for m in guarded if m.problems] == []


def test_check_fails_without_indexes_and_passes_with_the_solution(tmp_path):
    empty = tmp_path / "none.sql"
    empty.write_text("", encoding="utf-8")

    assert main(["--indexes", str(empty), "check"]) == 1
    assert main(["--indexes", str(LAB / "solutions" / "indexes.sql"), "check"]) == 0


def test_explain_reports_a_bad_query_instead_of_crashing(capsys):
    assert main(["explain", "SELECT * FROM nowhere"]) == 1
    assert "no such table" in capsys.readouterr().out
