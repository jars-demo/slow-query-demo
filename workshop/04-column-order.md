# Column order and covering indexes

> Same two columns, opposite order, very different speed. Then add one more column so the table is never read at all.

**Time:** 15 minutes

## Goal

Fix `revenue_since`, learn why the equality column goes before the range column, and use a covering index to skip the table.

## The query

```sql
SELECT count(*), sum(total_cents)
FROM orders
WHERE status = ? AND created_at >= ?
```

`status` is compared with `=`, `created_at` with `>=`. A range on time, inside one status.

## Try the obvious order first

Add this to `lab/indexes.sql`, next to your index from chapter 03:

```sql
CREATE INDEX orders_created_status ON orders (created_at, status);
```

```text
SEARCH orders USING INDEX orders_created_status (created_at>?)
```

Better than a scan: 3.33 milliseconds on our run. But look inside the brackets: only `created_at>?` is used to search. The index is sorted by time first, so every order since June is read, of every status, and the refunded ones are picked out one by one.

## Now the other way round

Replace it with:

```sql
CREATE INDEX orders_status_created ON orders (status, created_at);
```

```text
SEARCH orders USING INDEX orders_status_created (status=? AND created_at>?)
```

Both columns are used. The index jumps to `refunded`, then to June, and reads only the matching entries: 0.62 milliseconds. Same columns, five times faster, because of the order.

The rule from chapter 03, again: **equality first, range last.** Once an index hits a range, the columns after it cannot narrow the search any further.

## Never touch the table

Each match still has to visit the table to read `total_cents`. Put that column in the index too:

```sql
CREATE INDEX orders_status_created ON orders (status, created_at, total_cents);
```

```text
SEARCH orders USING COVERING INDEX orders_status_created (status=? AND created_at>?)
```

`COVERING` means the index alone answered the query. On our run: 0.09 milliseconds, from about 7 with no index. Roughly 80 times faster.

Covering indexes are a trade. They are bigger and slow writes more. Use them for the few queries that run constantly, not for everything.

## Check it works

- `revenue_since` shows `COVERING INDEX` and both `status=?` and `created_at>?` in its plan.
- `recent_orders` still uses `orders_customer_created` from chapter 03.

## Exercise

Without running it, write the plan you expect for `WHERE status = 'paid' AND created_at >= '2025-01-01'`, which matches about half the table. Then check it with `explain`. When most of the table matches, is the index still worth it? Measure it with a quick query of your own.

### More to try

- Low-variety columns like `status`, with four values, are rarely worth an index on their own. Try `CREATE INDEX orders_status ON orders (status)` alone and compare.
- Look up partial indexes (`CREATE INDEX ... WHERE status = 'refunded'`). When would one beat the index above?
