# Why queries get slow

> Build a small shop database, time every query its pages run, and find out which ones read far more rows than they return.

**Time:** 10 minutes

## Goal

Run the lab and read the bench table. By the end you know the one question behind almost every slow query: how many rows did the database read to give you the few you asked for?

## Set up

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python for you. The database is SQLite, which ships with Python, so there is nothing else to install.

```bash
git clone https://github.com/jars-demo/slow-query-demo.git
cd slow-query-demo/lab
uv sync
```

## The shop

`lab/shop/db.py` builds a fresh database in memory every time you run a command: 5,000 customers and 200,000 orders, with the same rows every time, so your numbers are comparable from run to run. The queries the shop's pages run are in `lab/shop/queries.py`:

| Query               | Page                                                   |
| ------------------- | ------------------------------------------------------ |
| `recent_orders`     | a customer's 20 latest orders                          |
| `revenue_since`     | revenue for one order status since a date              |
| `report_n_plus_one` | totals for every customer in a country, one query each |
| `report`            | the same totals with one JOIN                          |
| `page_offset`       | the newest orders list, page 5,000, with OFFSET        |
| `page_after`        | the same list, the page after a given row              |

## Run the bench

```bash
uv run python -m shop bench
```

```text
built 5,000 customers and 200,000 orders in 0.9s
indexes from lab/indexes.sql

query                      ms  statements  plan
recent_orders            4.23           1  SCAN orders | USE TEMP B-TREE FOR ORDER BY
revenue_since            8.36           1  SCAN orders
report_n_plus_one     2529.22         480  SCAN orders
report                 232.01           1  SCAN c | BLOOM FILTER ON o (customer_id=?) | SEARCH o USING AUTOMATIC COVERING INDEX (customer_id=?) LEFT-JOIN
page_offset            520.58           1  SCAN orders | USE TEMP B-TREE FOR ORDER BY
page_after              11.66           1  SCAN orders | USE TEMP B-TREE FOR ORDER BY
```

Your milliseconds will differ; the plans will not. Each row is the median of a few runs, and `statements` counts how many SQL statements the page sent to the database.

`recent_orders` returns 20 rows, and to find them SQLite read all 200,000 orders (`SCAN orders`), then sorted the matches (`USE TEMP B-TREE`). 4 milliseconds sounds fast. It is 4 milliseconds of a CPU core for every page view, and it grows with the table: at 20 million orders it is 100 times slower, while the page still shows 20 rows.

## Check it works

- `bench` prints six rows, and every plan contains `SCAN`.
- `report_n_plus_one` sends hundreds of statements. Everything else sends one.

## Exercise

Before reading on, rank the six queries from "easiest to fix" to "hardest to fix", and write one sentence each on why you think so. You will check your guesses in chapter 07.

### More to try

- Change the order count in `build()` in `lab/shop/db.py` from 200,000 to 400,000 and run `bench` again. Which queries roughly double? Which grow faster than that? Put it back after.
- `lab/indexes.sql` is empty apart from comments. Open it now; it is where you will work for the next three chapters.
