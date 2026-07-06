# Project Structure (Target / Intended End-State)

This reflects the intended structure per `docs/ARI3LLA INDEX.txt` (sections 23 & 40),
mapping the doc's `app/` onto this repo's `web/app/`. Some paths already existed before
the reorg work; others were built by parallel agents. Status noted per entry. Last synced
against the actual file tree on 2026-07-06 (run 18 doc-sync pass updated the report
count/date range and search/docs entries below without re-walking the whole tree).

```
fashion-trend-crawler/
├── .gitignore                  existing — pycache/pyo covered
├── README.md                   existing — public research index / project overview
├── TODO.md                     existing — working task list
├── .env                        existing — local secrets, gitignored
├── .codex/config.toml          existing — codex CLI config
├── .claude/
│   ├── settings.local.json     existing
│   ├── scheduled_tasks.lock    existing
│   └── skills/ari3lla-index/SKILL.md   existing — working skill / project context doc
├── data/
│   └── reports/                existing — dated JSON trend reports (schema-driven);
│       │                       10 reports as of run 18 (2026-05-07 through 2026-08-31)
│       ├── 2026-05-07.json     existing — first report under new schema
│       ├── 2026-07-06.json     existing — dated report
│       ├── 2026-07-13.json     existing — dated report (see agent-logs/real-report-2026-07-13.md)
│       ├── 2026-07-20.json     existing — dated report
│       ├── 2026-07-27.json     existing — dated report (thin/low-volatility stretch begins)
│       ├── 2026-08-03.json     existing — dated report
│       ├── 2026-08-10.json     existing — dated report
│       ├── 2026-08-17.json     existing — dated report
│       ├── 2026-08-24.json     existing — dated report (thin/low-volatility stretch ends)
│       └── 2026-08-31.json     existing — dated report
├── docs/
│   ├── ARI3LLA INDEX.txt       existing — the reorg/spec doc driving this work, read-only
│   ├── CHANGELOG.md            existing — master reconciled log
│   ├── PROJECT_STRUCTURE.md    existing — this file
│   ├── PROMPT_CHANGELOG.md     existing — review trail for summarize.py's build_prompt()
│   ├── EDITORIAL_CALENDAR.md   existing — known recurring high-volatility windows
│   │                           (fashion month Sept-Oct 2026), so a volatility shift
│   │                           isn't mistaken for a crawl/sourcing anomaly
│   └── agent-logs/             existing — per-agent hygiene/status/provenance logs
│       ├── data-pipeline.md
│       ├── frontend-archive.md
│       ├── frontend-static-pages.md
│       ├── hygiene-scan.md
│       ├── journalism-research.md
│       ├── legacy-file-cleanup.md
│       ├── pipeline-wiring.md
│       ├── readme-casestudy.md
│       ├── real-report-2026-07-13.md
│       ├── repo-hygiene.md
│       ├── schema-fixity-fields.md
│       ├── signals-timeline-design.md
│       ├── social-ingestion-research.md
│       ├── static-pages-audit-2.md
│       └── voice-audit.md
├── src/
│   ├── .gitignore              existing — covers __pycache__/*.pyc already
│   ├── crawler.py              existing — BFS crawler, robots.txt-respecting, UNCHANGED core logic
│   ├── summarize.py            existing — calls Claude to produce a report (doc section 21 tone)
│   ├── server.py               existing — MCP server (crawl/cache/search/list/get report tools)
│   ├── report_schema.py        existing — Report/Signal/CollectionWindow schema, save/load/list by date
│   ├── taxonomy.py             existing — source sector / confidence / volatility / origin vocab + classify_source(url)
│   ├── test_tools.py           existing — tests the old raw-cache pipeline; unrelated to
│   │                           report_schema.py, left alone unless migrating it
│   └── run.sh                  existing — fixed run 1 (no longer stale): runs
│                               crawler.py -> summarize.py (classify+summarize+save dated report)
└── web/
    ├── .gitignore               existing — covers node_modules/.next already
    ├── package.json / package-lock.json   existing — Next.js app config; `pagefind`
    │                              devDependency + `postbuild` script
    │                              (`pagefind --site out --output-subdir _pagefind`)
    ├── next.config.ts           existing — `output: "export"` set (required for Pagefind
    │                              to index the static `out/` build)
    ├── next-env.d.ts            existing
    ├── tsconfig.json / tsconfig.tsbuildinfo   existing
    ├── postcss.config.mjs       existing
    ├── eslint.config.mjs        existing
    ├── app/
    │   ├── page.tsx              existing — homepage (hero/tagline/footer, section 2/25 voice)
    │   ├── layout.tsx            existing — site-wide title/description metadata
    │   ├── globals.css           existing
    │   ├── favicon.ico           existing
    │   ├── archive/page.tsx      existing — lists all dated reports
    │   ├── reports/[date]/page.tsx   existing — renders one report (module order, section 20/36)
    │   ├── methodology/page.tsx  existing — doc section 22
    │   ├── taxonomy/page.tsx     existing — doc sections 11/14/15/16
    │   ├── sources/page.tsx      existing — doc section 11's outlet lists
    │   ├── about/page.tsx        existing — doc sections 37/38
    │   ├── case-study/page.tsx   existing — doc section 33, portfolio framing
    │   ├── timeline/page.tsx     existing — built run 3; doc section 24, reverse-chronological
    │   │                          longitudinal recurrence view across all reports
    │   ├── signals/[slug]/page.tsx   existing — shipped run 4; doc section 24, per-signal
    │   │                                history page across reports
    │   ├── search/page.tsx, search/SearchClient.tsx   existing — added run 12; client-side
    │   │                          facet filter (source sector, confidence, volatility),
    │   │                          plus Pagefind full-text search over report prose
    │   │                          (added later run, see agent-logs/pagefind-integration.md;
    │   │                          confirmed working end-to-end via a real
    │   │                          `npm install && npm run build` in
    │   │                          agent-logs/pagefind-verification-run15.md)
    │   └── rss.xml/route.ts      existing — RSS feed over the report archive
    ├── lib/
    │   ├── reports.ts            existing — archive data layer, reads data/reports/*.json;
    │   │                          homepage reads off this too (trends.ts retired run 13);
    │   │                          also exposes getSearchIndex() (run 12) for /search
    │   └── site.ts               existing — shared SITE_URL/SITE_NAME constants for
    │                              metadata/sitemap/robots/JSON-LD
    ├── public/                  existing — static assets
    └── node_modules/, .next/    build artifacts, gitignored, not tracked
```

## Notes / Follow-ups (informational only, not acted on)

- **Legacy trend files removed**: `trends_raw.json` / `trends_summary.json` (root and
  `src/`) and `web/lib/trends.ts` have all been retired (`trends.ts` retired run 13, once
  the homepage was rebuilt off `reports.ts`). `git ls-files` confirms none of the legacy
  JSON cache files remain tracked; `src/test_tools.py` still exercises the old raw-cache
  pipeline directly but is left alone unless it's migrated.
- **`/timeline` and `/signals/[slug]`** were built (run 3 / run 4 respectively) and are no
  longer planned-only.
- **No stray `.git` directories** found anywhere else in the tree besides the repo root
  `.git/`.
- **No `__pycache__` dirs or `.pyc` files** present anywhere in the tree; `src/.gitignore`
  and root `.gitignore` both cover them.
- `web/.next/` and `web/node_modules/` are already covered by `web/.gitignore`
  (`/node_modules`, `/.next/`); root `.gitignore` also lists `node_modules`/`.next` as a
  belt-and-suspenders entry.
