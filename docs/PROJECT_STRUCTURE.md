# Project Structure (Target / Intended End-State)

This reflects the intended structure per `docs/ARI3LLA INDEX.txt` (sections 23 & 40),
mapping the doc's `app/` onto this repo's `web/app/`. Some paths already existed before
the reorg work; others were built by parallel agents. Status noted per entry. Last synced
against the actual file tree on 2026-07-06.

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
│   └── reports/                existing — dated JSON trend reports (schema-driven)
│       ├── 2026-05-07.json     existing — first report under new schema
│       ├── 2026-07-06.json     existing — dated report
│       └── 2026-07-13.json     existing — dated report (see agent-logs/real-report-2026-07-13.md)
├── docs/
│   ├── ARI3LLA INDEX.txt       existing — the reorg/spec doc driving this work, read-only
│   ├── CHANGELOG.md            existing — master reconciled log
│   ├── PROJECT_STRUCTURE.md    existing — this file
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
│   ├── test_tools.py           existing — MCP tool smoke tests, reads legacy trends_raw.json
│   ├── run.sh                  existing — KNOWN STALE — runs crawler -> test_tools -> server,
│   │                           never calls summarize.py; needs a follow-up pass to wire the
│   │                           full crawl -> classify -> summarize -> save pipeline
│   ├── trends_raw.json         legacy — pre-archive-schema cache, superseded by data/reports/
│   └── trends_summary.json     legacy — pre-archive-schema summary, superseded by data/reports/
├── trends_raw.json             legacy — root-level duplicate/older copy of src/trends_raw.json
├── trends_summary.json         legacy — root-level duplicate/older copy of src/trends_summary.json
└── web/
    ├── .gitignore               existing — covers node_modules/.next already
    ├── package.json / package-lock.json   existing — Next.js app config
    ├── next.config.ts           existing
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
    │   ├── timeline/page.tsx     PLANNED — not yet created; doc section 24 "optional later pages",
    │   │                          longitudinal recurrence view, once enough dated reports exist
    │   └── signals/[slug]/page.tsx   PLANNED — not yet created; doc section 24, per-signal
    │                                history page across reports
    ├── lib/
    │   ├── trends.ts             existing — ORIGINAL data layer for live/current-crawl view,
    │   │                          not repurposed for archive reads
    │   └── reports.ts            existing — archive data layer, reads data/reports/*.json
    ├── public/                  existing — static assets
    └── node_modules/, .next/    build artifacts, gitignored, not tracked
```

## Notes / Follow-ups (informational only, not acted on)

- **Legacy trend files**: `trends_raw.json` / `trends_summary.json` exist in both the repo
  root and `src/`, and the two copies have diverged content (different Met Gala article
  sets/summaries) — they look stale and duplicated. Left in place per instructions since
  the new `data/reports/` pipeline (via `report_schema.py`) is still being wired up.
  Once that pipeline is confirmed working end-to-end, all four legacy files should be
  removed (tracked in `docs/CHANGELOG.md` "Known gaps").
- **`src/run.sh` / `src/test_tools.py`**: `run.sh` currently runs `crawler.py` ->
  `test_tools.py` -> `server.py`, and `test_tools.py` reads `trends_raw.json` directly.
  Once `report_schema.py` / `taxonomy.py` are fully integrated into `summarize.py`/`server.py`,
  the pipeline order and the test fixture path will likely need updating to point at
  `data/reports/*.json` instead of the legacy cache file.
- **`/timeline` and `/signals/[slug]`** remain planned-only (doc section 24, "optional later
  pages") — not yet built, worth revisiting once there are enough dated reports in
  `data/reports/` to make recurrence tracking meaningful.
- **No stray `.git` directories** found anywhere else in the tree besides the repo root
  `.git/`.
- **No `__pycache__` dirs or `.pyc` files** present anywhere in the tree; `src/.gitignore`
  and root `.gitignore` both cover them.
- `web/.next/` and `web/node_modules/` are already covered by `web/.gitignore`
  (`/node_modules`, `/.next/`); root `.gitignore` also lists `node_modules`/`.next` as a
  belt-and-suspenders entry.
