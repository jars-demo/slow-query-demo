# AGENTS.md

Guidance for AI coding agents and developers. Humans: start with [README.md](README.md).

## What this is

A short workshop, "Make the slow query fast": query plans, indexes, N+1 and keyset pagination
on an in-memory SQLite shop. The lab in `lab/` and the chapters in `workshop/` are the product;
`frontend/` is the site.

## Map

```text
lab/shop/db.py            SCHEMA and build(): the same 5,000 customers and 200,000 orders every run
lab/shop/queries.py       the SQL each page runs, as constants, and the functions that run it
lab/shop/plan.py          explain() and problems(): full scans and temp sorts
lab/shop/bench.py         CASES (guarded or not), timed(), statements(), measure()
lab/shop/__main__.py      CLI: bench [--latency], explain, check; --indexes FILE
lab/indexes.sql           the learner's indexes; ships with comments only
lab/solutions/indexes.sql one passing answer; CI checks it
workshop/NN-slug.md       chapters; SQL quoted from lab/ must match it exactly
frontend/                 Next.js site; reads ../workshop at build time
```

## Commands

```bash
cd lab && uv sync && uv run pytest && uv run python -m shop bench
cd frontend && npm ci && npm run verify
```

## Rules

1. **No runtime dependencies** in `lab/`. Standard library only, so it runs anywhere.
2. **`lab/indexes.sql` stays empty.** Learners start from full scans; answers go in `solutions/`.
3. **Chapters quote real code and real output.** A unit test checks the SQL quoted in chapters
   03, 05 and 06 and every file path chapters mention. Timings are labelled as one machine's run.
4. **Writing style.** Plain English, short sentences, no em dashes. Conventional Commits, no AI
   attribution trailers.
