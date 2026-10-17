# Make the slow query fast

[![Lab](https://github.com/jars-demo/slow-query-demo/actions/workflows/lab.yml/badge.svg)](https://github.com/jars-demo/slow-query-demo/actions/workflows/lab.yml)
[![Frontend](https://github.com/jars-demo/slow-query-demo/actions/workflows/frontend.yml/badge.svg)](https://github.com/jars-demo/slow-query-demo/actions/workflows/frontend.yml)

A hands-on database workshop. Read query plans, choose the index that fixes a slow query, kill N+1 queries, page without OFFSET, and guard query plans in CI. All of it with SQLite and plain Python, and all of it carries over to Postgres and MySQL.

**Workshop site:** [slowquery.jishanahmed.in](https://slowquery.jishanahmed.in)

## Quick start

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python for you. SQLite ships with Python, so there is nothing else to install.

```bash
git clone https://github.com/jars-demo/slow-query-demo.git
cd slow-query-demo/lab
uv sync
uv run python -m shop bench
```

Every run builds the same shop database in memory (5,000 customers, 200,000 orders), runs `lab/indexes.sql`, then times each query and prints its plan. Before you add any indexes, every plan says `SCAN`.

| Query           | No index (ms) | With the solution (ms) |
| --------------- | ------------- | ---------------------- |
| `recent_orders` | 4.23          | 0.01                   |
| `revenue_since` | 8.36          | 0.09                   |
| `report`        | 232.01        | 7.67                   |
| `page_after`    | 11.66         | 0.02                   |

Measured on one laptop; your numbers will differ, the plans will not.

## Commands

| Command                                      | What it does                                         |
| -------------------------------------------- | ---------------------------------------------------- |
| `uv run python -m shop bench [--latency 1]`  | time every query, count statements, show plans       |
| `uv run python -m shop explain "SELECT ..."` | show the plan for any query                          |
| `uv run python -m shop check`                | exit 1 if a guarded query full scans or sorts        |
| `uv run python -m shop --indexes FILE ...`   | use another index file, like `solutions/indexes.sql` |
| `uv run pytest`                              | the tests                                            |

## The workshop

| #   | Chapter                                                          | You learn                                   |
| --- | ---------------------------------------------------------------- | ------------------------------------------- |
| 01  | [Why queries get slow](workshop/01-why-slow.md)                  | rows read against rows returned             |
| 02  | [Read the plan](workshop/02-read-the-plan.md)                    | EXPLAIN QUERY PLAN, scan, search, temp sort |
| 03  | [Your first index](workshop/03-first-index.md)                   | single and composite indexes                |
| 04  | [Column order and covering indexes](workshop/04-column-order.md) | equality first, range last, covering        |
| 05  | [N+1 queries](workshop/05-n-plus-one.md)                         | statement counts, network latency, JOIN     |
| 06  | [Pagination that stays fast](workshop/06-pagination.md)          | OFFSET against keyset pagination            |
| 07  | [Guard it in CI](workshop/07-guard-in-ci.md)                     | fail the build when a plan regresses        |

## Layout

```text
lab/shop/              the database, the queries, plans, the bench and the CLI
lab/indexes.sql        your indexes: the file you edit in chapters 03 to 06
lab/solutions/         one answer that passes the check
lab/tests/             pytest
workshop/              the chapters, in Markdown
frontend/              the workshop site (Next.js), which renders workshop/
```

## Run the site locally

```bash
cd frontend
npm ci
npm run dev
```

## License

[MIT](LICENSE)
