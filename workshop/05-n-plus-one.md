# N+1 queries

> One query for the list, then one more for every row. Fast on your laptop, slow in production. Find it by counting statements, and fix it with one JOIN.

**Time:** 15 minutes

## Goal

See why the N+1 pattern hides on a local database, make it visible with simulated network latency, and replace it with a single query.

## The pattern

From `lab/shop/queries.py`:

```python
def report_n_plus_one(conn: sqlite3.Connection, country: str) -> list[Row]:
    rows = []
    for customer_id, name in conn.execute(CUSTOMERS_IN, (country,)).fetchall():
        count, total = conn.execute(TOTALS_FOR, (customer_id,)).fetchone()
        rows.append((customer_id, name, count, total))
    return rows
```

One query to list Nigeria's customers, then one per customer for their totals. With 479 customers, that is 480 statements for one page. ORMs write this for you when you loop over records and touch a relation, which is why it is so common.

## Why it hid

Run the bench with the reference indexes from `lab/solutions/indexes.sql`, which include the ones from chapters 03 and 04:

```bash
uv run python -m shop --indexes solutions/indexes.sql bench
```

```text
report_n_plus_one        6.81         480  SEARCH orders USING INDEX orders_customer_created (customer_id=?)
report                   7.67           1  SEARCH c USING INDEX customers_country (country=?) | SEARCH o USING INDEX orders_customer_created (customer_id=?) LEFT-JOIN
```

Nearly the same! SQLite runs inside your Python process, so a statement costs microseconds. Your production database is across a network, and every statement pays a round trip, often 0.5 to 2 milliseconds.

## Add the network back

`bench --latency` waits that many milliseconds before every statement:

```bash
uv run python -m shop --indexes solutions/indexes.sql bench --latency 1
```

```text
report_n_plus_one      751.32         480  SEARCH orders USING INDEX orders_customer_created (customer_id=?)
report                  10.27           1  SEARCH c USING INDEX customers_country (country=?) | SEARCH o USING INDEX orders_customer_created (customer_id=?) LEFT-JOIN
```

Three quarters of a second for one page, against 10 milliseconds. The query was never the problem; the number of statements was. That is why the bench shows a `statements` column.

## The fix

One query that asks for everything at once:

```sql
SELECT c.id, c.name, count(o.id), coalesce(sum(o.total_cents), 0)
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
WHERE c.country = ?
GROUP BY c.id
ORDER BY c.id
```

`LEFT JOIN` keeps customers with no orders, and `coalesce` turns their missing sum into 0, so the result matches the loop exactly. A test in `lab/tests/test_shop.py` proves it.

The join needs two indexes: one to find customers by country, and one to find orders by customer. You have the second from chapter 03. Add the first to your own `lab/indexes.sql`, then run `bench` without `--indexes`:

```sql
CREATE INDEX customers_country ON customers (country);
```

## Check it works

- `report` shows `SEARCH c USING INDEX customers_country` and sends 1 statement.
- `uv run pytest -k "n_plus_one or join"` passes.

## Exercise

When a JOIN is awkward, for example when the data comes from two different services, the other fix is batching: one query for the customers, then one query for all their totals with `WHERE customer_id IN (...)`. Write `report_batched` in `lab/shop/queries.py`, add it to `CASES` in `lab/shop/bench.py`, and compare its statements and time with `--latency 1`.

### More to try

- Most ORMs have a fix built in: `select_related` and `prefetch_related` in Django, `include` in Prisma, `joinedload` in SQLAlchemy. Find the one your project uses.
- Write a test that fails if a page sends more than 5 statements, using `statements()` from `lab/shop/bench.py`. That catches N+1 before review does.
