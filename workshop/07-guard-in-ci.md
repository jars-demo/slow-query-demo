# Guard it in CI

> A fast query is one careless migration away from slow again. Check query plans on every pull request, so a dropped index fails the build instead of the pager.

**Time:** 12 minutes

## Goal

Run the plan check, see it fail without indexes and pass with them, and wire it into CI the way this repository does.

## Plans are stable, timings are not

You could fail CI when a query takes over 5 milliseconds, but CI machines are noisy and the test would be flaky. The plan is deterministic: given the schema, the indexes and the data's statistics, SQLite picks the same steps every time. So the check asserts on the plan.

Every case in `lab/shop/bench.py` is guarded unless it says otherwise. `check` fails if a guarded query's plan contains a full table scan or a temp sort:

```bash
uv run python -m shop check
```

With your `lab/indexes.sql` from the earlier chapters, every line should say `ok`. To see it fail, comment out one line in `lab/indexes.sql` with `--`, run `check` again, and read which query it names:

```text
FAIL  recent_orders       SCAN orders | USE TEMP B-TREE FOR ORDER BY
```

`check` exits with 1 when anything fails, which is all CI needs to block a merge.

## The reference answer

`lab/solutions/indexes.sql` holds one set of indexes that passes. Compare it with yours: there is more than one right answer, and the check does not care which index you chose, only that no guarded query reads the whole table or sorts afterwards.

## In CI

The workflow in `.github/workflows/lab.yml` runs lint and tests, then:

```yaml
- name: Query plans (no full scans, no temp sorts)
  run: uv run python -m shop --indexes solutions/indexes.sql check
```

In your own project, point it at your real migrations instead of a solutions file. The test pattern carries over directly: build the schema, run `EXPLAIN` on the queries your pages send, and fail on the steps you never want to see. Postgres can do the same with `EXPLAIN (FORMAT JSON)`, as long as the test database has realistic statistics.

## Check it works

- `check` exits with 0 and prints `0 of 5 guarded queries need an index` with your indexes.
- `uv run pytest -k check` passes: it proves the check fails without indexes and passes with the solution.

## Exercise

Look back at the ranking you wrote in chapter 01. Which query was harder to fix than you expected, and which was easier? Then add a new guarded case to `CASES` in `lab/shop/bench.py`: "a customer's refunded orders this year". Write the query, run `check`, watch it fail, and fix it with the smallest index change you can.

### More to try

- `check` uses a database of 200,000 orders. Run it on 2,000 by passing a smaller `orders` to `build()`. Do the plans change? A tiny test database can make the planner choose a scan just because the table is small.
- Add a guard for statement counts too, so an N+1 regression fails CI the same way a missing index does.
