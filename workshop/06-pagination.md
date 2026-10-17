# Pagination that stays fast

> Page 1 is fast. Page 5,000 is not, because OFFSET reads every row it skips. Keyset pagination remembers where you stopped instead.

**Time:** 12 minutes

## Goal

Measure how OFFSET pagination slows down as the page number grows, and replace it with keyset pagination, which costs the same on every page.

## OFFSET reads what it skips

```sql
SELECT id, created_at, total_cents
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT ? OFFSET ?
```

To return rows 100,001 to 100,020, the database has to walk past the first 100,000. With no index on `created_at`, it first sorts all 200,000. That was the 520 milliseconds in chapter 01.

Add an index on the sort column to `lab/indexes.sql`:

```sql
CREATE INDEX orders_created ON orders (created_at);
```

Now the walk is in index order, but it is still a walk. Our measurements, with that index:

| Page  | ms   |
| ----- | ---- |
| 0     | 0.01 |
| 100   | 0.06 |
| 1,000 | 0.52 |
| 5,000 | 2.62 |
| 9,000 | 3.52 |

It grows with the page number. That is why `page_offset` is the one query `check` does not guard: no index can make a deep OFFSET cheap.

## Keyset: start after the last row you saw

```sql
SELECT id, created_at, total_cents
FROM orders
WHERE (created_at, id) < (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT ?
```

The client sends back the `created_at` and `id` of the last row on its current page, and the query jumps straight there through the index:

```text
SEARCH orders USING INDEX orders_created (created_at<?)
```

0.01 milliseconds, on any page. `id` is in the sort so that orders with the same timestamp keep a stable order and none is skipped or repeated. A test in `lab/tests/test_shop.py` walks four pages both ways and checks they match.

The trade: keyset pagination cannot jump to "page 5,000". It gives you "next page" and "previous page", which is what infinite scroll, feeds and APIs with a `cursor` parameter need anyway.

## Check it works

- `page_after` shows `SEARCH orders USING INDEX orders_created` and no `USE TEMP B-TREE`.
- `uv run pytest -k keyset` passes.

## Exercise

APIs usually hide the two values in an opaque cursor string. Write `encode_cursor((created_at, id)) -> str` and `decode_cursor(str)` in `lab/shop/queries.py` using base64 of a small JSON list, and a test that round-trips one. Why is it a good idea to keep the cursor opaque to clients?

### More to try

- What happens to keyset pages if an order is inserted while a user is paging? And with OFFSET? Try it in a test: fetch page 0, insert a newer order, fetch page 1 both ways.
- Add a "previous page" query: the same idea with `>` and the sort reversed, then reverse the rows in Python.
