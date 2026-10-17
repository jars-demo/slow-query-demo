# Your first index

> Add one index, watch a scan become a search, then add a second column and watch the sort disappear too.

**Time:** 15 minutes

## Goal

Fix `recent_orders` in two steps, and learn why the column after the `=` in an index decides whether the database still has to sort.

## The query

```sql
SELECT id, status, total_cents, created_at
FROM orders
WHERE customer_id = ?
ORDER BY created_at DESC
LIMIT 20
```

An index is a sorted copy of some columns, each entry pointing back at its row. With orders sorted by `customer_id`, finding customer 42 is a binary search instead of a full read.

## Step 1: one column

Add this line to `lab/indexes.sql`:

```sql
CREATE INDEX orders_customer ON orders (customer_id);
```

Run the bench again:

```bash
uv run python -m shop bench
```

The plan for `recent_orders` changes to:

```text
SEARCH orders USING INDEX orders_customer (customer_id=?) | USE TEMP B-TREE FOR ORDER BY
```

On our run it went from 4.27 to 0.02 milliseconds: about 40 orders read instead of 200,000. But the sort is still there. The index found customer 42's orders in `id` order, and the query wants them newest first.

## Step 2: the column you sort by

Replace that line with a two-column index:

```sql
CREATE INDEX orders_customer_created ON orders (customer_id, created_at);
```

```text
SEARCH orders USING INDEX orders_customer_created (customer_id=?)
```

No more sort. Inside one customer, this index is already sorted by `created_at`, so SQLite reads the newest 20 entries and stops. On our run: 0.01 milliseconds.

The rule: **equality columns first, then the column you sort or range over.** The index is sorted by the first column, then by the second within each value of the first. `(created_at, customer_id)` would be sorted by time first, which is useless for "one customer".

## A surprise in the same bench

Look at `report_n_plus_one` and `report`: they got much faster too, because they also look up orders by `customer_id`. One good index often helps several pages.

Now look at `revenue_since`. On our run it went from about 7 to about 18 milliseconds, slower than with no index at all. Its plan now says `ANY(customer_id) AND created_at>?`: SQLite tried to use your new index for a query it was never meant for. Indexes are not free. Chapter 04 fixes this one properly.

## Check it works

- `recent_orders` shows `SEARCH ... orders_customer_created` and no `USE TEMP B-TREE`.
- `uv run pytest -k composite` passes.

## Exercise

Try the index the other way round, `(created_at, customer_id)`, run `bench`, and read the plans. On our run `recent_orders` became `SCAN orders USING INDEX`, barely faster than no index, and `report_n_plus_one` was back to a full scan per customer. Explain from the plans why, then put the right one back.

### More to try

- Every index slows writes down: each `INSERT` has to update it. Time `build()` with and without your index (the first line of `bench` output) and see the cost at load time.
- Would `(customer_id, created_at, status, total_cents)` help `recent_orders` more? Try it and look for `COVERING` in the plan.
