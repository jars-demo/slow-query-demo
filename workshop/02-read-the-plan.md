# Read the plan

> Before you add an index, ask the database what it intends to do. EXPLAIN QUERY PLAN tells you in one line per step.

**Time:** 12 minutes

## Goal

Read SQLite query plans, tell a scan from a search, and spot the sort step that hides in many slow queries.

## Ask for the plan

Every database can explain a query without running it. In SQLite it is `EXPLAIN QUERY PLAN`. The lab wraps it in a command:

```bash
uv run python -m shop explain "SELECT * FROM orders WHERE customer_id = 42"
```

```text
!! SCAN orders
```

The lab marks a step with `!!` when it is one of the two expensive kinds. That rule lives in `lab/shop/plan.py`:

```python
# "SCAN orders" reads every row of the table. "SCAN orders USING INDEX ..." walks an index in
# order, which can be fine. "USE TEMP B-TREE" means the rows had to be sorted after reading.
FULL_SCAN = re.compile(r"^SCAN \w+$")
TEMP_SORT = "USE TEMP B-TREE"
```

## The words that matter

| Plan says                         | Means                                                             |
| --------------------------------- | ----------------------------------------------------------------- |
| `SCAN orders`                     | read every row of the table                                       |
| `SEARCH orders USING INDEX x (…)` | jump straight to the matching rows through index `x`              |
| `USING COVERING INDEX`            | the index alone had every column needed; the table was never read |
| `USE TEMP B-TREE FOR ORDER BY`    | the matching rows were sorted after they were found               |
| `AUTOMATIC COVERING INDEX`        | SQLite built a throwaway index for this one query, every time     |

Postgres and MySQL use other words, `Seq Scan` and `Index Scan` in Postgres, but the questions are the same: does it read everything, and does it sort afterwards?

## Try a few

```bash
uv run python -m shop explain "SELECT * FROM orders WHERE id = 42"
uv run python -m shop explain "SELECT * FROM orders ORDER BY created_at DESC LIMIT 20"
uv run python -m shop explain "SELECT count(*) FROM orders WHERE status = 'refunded'"
```

The first one is a `SEARCH` without you adding anything: `id` is the primary key, and the table itself is stored in `id` order. The second sorts all 200,000 orders to return 20. The third reads every row to count a few thousand.

## Check it works

- You can explain why `WHERE id = 42` is fast and `WHERE customer_id = 42` is not.
- `explain "SELECT * FROM nowhere"` prints SQLite's error instead of crashing.

## Exercise

Write down the plan for the `REPORT` query from `lab/shop/queries.py` (replace `?` with `'NG'`). It contains `AUTOMATIC COVERING INDEX`. SQLite noticed the join had no index and built one, and it throws it away after the query. Why is that still 230 milliseconds per run, and what does it tell you about which index to add?

### More to try

- Run `explain "SELECT * FROM orders WHERE total_cents > 40000"`. Would an index help a query that matches a fifth of the table? Keep your answer; chapter 04 comes back to it.
- Postgres users: run `EXPLAIN ANALYZE` on a slow query at work and match its steps to this table.
