"""python -m shop bench | explain | check"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

from .bench import measure
from .db import INDEXES, build, read_indexes
from .plan import explain, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m shop")
    parser.add_argument(
        "--indexes", type=Path, default=INDEXES, help="SQL file to run after loading the data"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    bench = commands.add_parser("bench", help="time every query and show its plan")
    bench.add_argument(
        "--latency", type=float, default=0, help="ms to wait per statement, like a network"
    )
    ask = commands.add_parser("explain", help="show the plan for one SQL query")
    ask.add_argument("sql")
    commands.add_parser("check", help="fail if a guarded query full scans or sorts")
    args = parser.parse_args(argv)

    started = time.perf_counter()
    try:
        conn = build(indexes=read_indexes(args.indexes))
    except (OSError, sqlite3.Error) as error:
        print(f"could not build the database with {args.indexes}: {error}")
        return 1
    print(f"built 5,000 customers and 200,000 orders in {time.perf_counter() - started:.1f}s")
    print(f"indexes from {args.indexes.parent.name}/{args.indexes.name}\n")

    if args.command == "explain":
        try:
            plan = explain(conn, args.sql)
        except sqlite3.Error as error:
            print(f"SQLite says: {error}")
            return 1
        for step in plan:
            print(f"{'!!' if step in problems(plan) else '  '} {step}")
        return 0

    results = measure(conn, latency_ms=getattr(args, "latency", 0))

    if args.command == "bench":
        print(f"{'query':<20}{'ms':>9}{'statements':>12}  plan")
        for m in results:
            print(f"{m.name:<20}{m.ms:>9.2f}{m.statements:>12}  {' | '.join(m.plan)}")
        return 0

    failing = [m for m in results if m.guarded and m.problems]
    for m in results:
        if m.guarded:
            print(f"{'FAIL' if m.problems else 'ok  '}  {m.name:<20}{' | '.join(m.problems)}")
    print(f"\n{len(failing)} of {sum(m.guarded for m in results)} guarded queries need an index")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
