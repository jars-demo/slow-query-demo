"""A small shop database in SQLite, built fresh in memory with the same rows every time."""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

SCHEMA = """
CREATE TABLE customers (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    country    TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    status      TEXT NOT NULL,
    total_cents INTEGER NOT NULL,
    created_at  TEXT NOT NULL
);
"""

COUNTRIES = ("IN", "US", "DE", "BR", "JP", "GB", "FR", "NG", "AU", "CA")
STATUSES = ("paid", "shipped", "pending", "refunded")
STATUS_WEIGHTS = (50, 35, 10, 5)
START = datetime(2025, 1, 1)
SPAN = int(timedelta(days=640).total_seconds())

# Your indexes. Chapters 03 and 04 ask you to write them here.
INDEXES = Path(__file__).resolve().parent.parent / "indexes.sql"


def stamp(rng: random.Random) -> str:
    return (START + timedelta(seconds=rng.randrange(SPAN))).strftime("%Y-%m-%d %H:%M:%S")


def build(
    customers: int = 5_000, orders: int = 200_000, indexes: str = "", seed: int = 7
) -> sqlite3.Connection:
    """Create the tables, fill them, then run `indexes` (SQL) and ANALYZE."""
    rng = random.Random(seed)
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?)",
        ((i, f"Customer {i}", rng.choice(COUNTRIES), stamp(rng)) for i in range(1, customers + 1)),
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
        (
            (
                i,
                rng.randint(1, customers),
                rng.choices(STATUSES, STATUS_WEIGHTS)[0],
                rng.randint(199, 49_999),
                stamp(rng),
            )
            for i in range(1, orders + 1)
        ),
    )
    conn.executescript(indexes)
    conn.execute("ANALYZE")  # give the planner real statistics, as a production database has
    conn.commit()
    return conn


def read_indexes(path: Path = INDEXES) -> str:
    return path.read_text(encoding="utf-8")
