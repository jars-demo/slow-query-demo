import Link from 'next/link'

import { CopyButton } from '@/components/CopyButton'
import { REPO_URL } from '@/components/Shell'
import { CHAPTERS } from '@/lib/workshop'

// Real output of `uv run python -m shop bench`, without and with lab/solutions/indexes.sql.
const BENCH = [
  { name: 'recent_orders', before: '4.23', after: '0.01' },
  { name: 'revenue_since', before: '8.36', after: '0.09' },
  { name: 'report', before: '232.01', after: '7.67' },
  { name: 'page_after', before: '11.66', after: '0.02' },
]

const PARTS = [
  ['Plans', 'lab/shop/plan.py', 'Read EXPLAIN QUERY PLAN and spot the scan.'],
  ['Indexes', 'lab/indexes.sql', 'Composite, column order, covering.'],
  ['Queries', 'lab/shop/queries.py', 'N+1 against JOIN, OFFSET against keyset.'],
  ['Guard', 'lab/shop/bench.py', 'Fail CI when a plan regresses.'],
]

const QUICKSTART = `git clone https://github.com/jars-demo/slow-query-demo.git
cd slow-query-demo/lab
uv sync
uv run python -m shop bench`

export default function Home() {
  const minutes = CHAPTERS.reduce((sum, chapter) => sum + chapter.minutes, 0)

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-20 px-4 pt-16 pb-24 sm:pt-24">
      <section className="grid items-start gap-12 lg:grid-cols-[1.05fr_1fr]">
        <div className="flex min-w-0 flex-col gap-6">
          <p className="font-mono text-[12px] tracking-wider text-muted uppercase">
            Database workshop · {CHAPTERS.length} chapters · {minutes} minutes
          </p>
          <h1 className="text-[2.75rem] leading-[1.05] font-semibold tracking-[-0.035em] text-balance sm:text-[3.5rem]">
            Make the slow query fast.
          </h1>
          <p className="max-w-xl text-[18px] leading-relaxed text-ink-2">
            Most slow pages are a query that reads 200,000 rows to show 20. Learn to read a query
            plan, choose the index that fixes it, kill N+1 queries, page without OFFSET, and guard
            it all in CI.
          </p>
          <ul className="flex flex-col gap-1.5 text-[15px] text-ink-2">
            <li>SQLite, built into Python: nothing to install or run.</li>
            <li>A real shop database, 200,000 orders, rebuilt the same every time.</li>
            <li>A bench that shows time, statements and the plan for every query.</li>
            <li>The ideas carry straight over to Postgres and MySQL.</li>
          </ul>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/workshop/01-why-slow"
              className="inline-flex h-11 items-center rounded-full bg-accent px-6 text-[15px] font-medium text-white hover:bg-accent-strong"
            >
              Start the workshop
            </Link>
            <a
              href={REPO_URL}
              className="inline-flex h-11 items-center rounded-full border border-line-strong px-6 text-[15px] font-medium hover:bg-surface"
            >
              View the code
            </a>
          </div>
        </div>

        <figure className="code min-w-0 overflow-hidden rounded-2xl">
          <figcaption className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-2.5 text-[12px] text-[#a5b4fc]">
            <span>python -m shop bench</span>
            <span>milliseconds</span>
          </figcaption>
          <div className="overflow-x-auto px-4 py-4 text-[12.5px] leading-[1.75]">
            <div className="whitespace-pre text-[#94a3b8]">
              {'query'.padEnd(16)}
              {'no index'.padStart(10)}
              {'indexed'.padStart(10)}
            </div>
            {BENCH.map((row) => (
              <div key={row.name} className="whitespace-pre">
                {row.name.padEnd(16)}
                <span className="text-[#fca5a5]">{row.before.padStart(10)}</span>
                <span className="text-[#86efac]">{row.after.padStart(10)}</span>
              </div>
            ))}
            <div className="mt-3 border-t border-white/10 pt-3 text-[#94a3b8]">
              <div className="whitespace-pre">
                <span className="text-[#fca5a5]">{'before  '}</span>SCAN orders
              </div>
              <div className="whitespace-pre">
                <span className="text-[#86efac]">{'after   '}</span>SEARCH orders USING INDEX
              </div>
            </div>
          </div>
        </figure>
      </section>

      <section aria-labelledby="parts" className="flex flex-col gap-6">
        <h2 id="parts" className="text-[1.6rem] font-semibold tracking-[-0.02em]">
          What you work with
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PARTS.map(([name, file, about]) => (
            <div key={name} className="flex flex-col gap-2 rounded-2xl bg-surface p-5">
              <span className="text-[15px] font-semibold">{name}</span>
              <code className="font-mono text-[12px] break-all text-accent">{file}</code>
              <span className="text-[14px] text-ink-2">{about}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-labelledby="chapters" className="grid gap-10 lg:grid-cols-[1fr_1.3fr]">
        <div className="flex flex-col gap-3">
          <h2 id="chapters" className="text-[1.6rem] font-semibold tracking-[-0.02em]">
            {CHAPTERS.length} short chapters
          </h2>
          <p className="text-[15px] leading-relaxed text-ink-2">
            Each one is a few minutes of reading, one change to make, and a number that proves it
            worked. By the end you can open any slow endpoint and find out why.
          </p>
        </div>
        <ol className="flex flex-col gap-2">
          {CHAPTERS.map((chapter) => (
            <li key={chapter.slug}>
              <Link
                href={`/workshop/${chapter.slug}`}
                className="flex items-baseline gap-4 rounded-xl px-4 py-3 hover:bg-surface"
              >
                <span className="w-7 shrink-0 font-mono text-[13px] text-accent">
                  {chapter.number}
                </span>
                <span className="min-w-0 flex-1 text-[15px] font-medium">{chapter.title}</span>
                <span className="shrink-0 font-mono text-[12px] text-muted">
                  {chapter.minutes} min
                </span>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="start" className="flex flex-col gap-4">
        <h2 id="start" className="text-[1.6rem] font-semibold tracking-[-0.02em]">
          Run it in a minute
        </h2>
        <p className="text-[15px] text-ink-2">
          You need{' '}
          <a href="https://docs.astral.sh/uv/" className="text-accent underline underline-offset-4">
            uv
          </a>{' '}
          and git. uv installs Python for you.
        </p>
        <div className="code relative max-w-2xl overflow-x-auto rounded-2xl px-4 pt-10 pb-4 text-[13px] leading-relaxed">
          <div className="absolute top-2 right-2">
            <CopyButton text={QUICKSTART} />
          </div>
          <pre>{QUICKSTART}</pre>
        </div>
      </section>
    </div>
  )
}
