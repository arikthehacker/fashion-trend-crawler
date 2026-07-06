# Project Structure (Target / Intended End-State)

This reflects the intended structure per `docs/ARI3LLA INDEX.txt` (sections 23 & 40),
mapping the doc's `app/` onto this repo's `web/app/`. Some paths already existed before
tonight's reorg work; others are new/in-progress additions being built by parallel agents
as of 2026-07-06. Status noted per entry.

```
fashion-trend-crawler/
├── .gitignore                  existing — pre-existing, updated tonight (pycache/pyo added)
├── README.md                   existing — project overview, do not edit here
├── .env                        existing — local secrets, gitignored
├── data/
│   └── reports/                new — dated JSON trend reports (schema-driven)
│       └── 2026-05-07.json     new — first report under new schema (in progress)
├── docs/
│   ├── ARI3LLA INDEX.txt       existing — the reorg/spec doc driving this work
│   ├── PROJECT_STRUCTURE.md    new — this file
│   └── agent-logs/             new — per-agent hygiene/status logs
│       └── repo-hygiene.md     new — this audit's log
├── src/
│   ├── .gitignore              existing — covers __pycache__/*.pyc already
│   ├── crawler.py              existing — fetches fashion source data (owned by another agent)
│   ├── summarize.py            existing — summarization logic (being modified by another agent)
│   ├── server.py               existing — MCP server (being modified by another agent)
│   ├── report_schema.py        new — schema for data/reports/*.json (another agent's work)
│   ├── taxonomy.py             new — trend taxonomy/categorization (another agent's work)
│   ├── test_tools.py           existing — MCP tool smoke tests, reads legacy trends_raw.json
│   ├── run.sh                  existing — pipeline runner (crawler -> tests -> server); order
│   │                           will likely need updating once report_schema/taxonomy land
│   ├── trends_raw.json         legacy — pre-archive-schema cache, superseded by data/reports/
│   └── trends_summary.json     legacy — pre-archive-schema summary, superseded by data/reports/
├── trends_raw.json             legacy — root-level duplicate/older copy of src/trends_raw.json
├── trends_summary.json         legacy — root-level duplicate/older copy of src/trends_summary.json
└── web/
    ├── .gitignore               existing — covers node_modules/.next already
    ├── package.json / lock      existing — Next.js app config
    ├── next.config.ts           existing
    ├── app/
    │   ├── page.tsx             existing — home/landing (being modified tonight)
    │   ├── layout.tsx           existing
    │   ├── globals.css          existing
    │   ├── favicon.ico          existing
    │   ├── case-study/page.tsx  existing
    │   ├── archive/page.tsx     TARGET (per doc section 23) — not yet created
    │   └── reports/[date]/page.tsx  TARGET (per doc section 23) — not yet created
    ├── lib/                     existing — shared web helpers, do not edit here
    ├── public/                  existing — static assets
    └── node_modules/, .next/    build artifacts, gitignored, not tracked
```

## Notes / Follow-ups (informational only, not acted on)

- **Legacy trend files**: `trends_raw.json` / `trends_summary.json` exist in both the repo
  root and `src/`, and the two copies have diverged content (different Met Gala article
  sets/summaries) — they look stale and duplicated. Left in place per instructions since
  the new `data/reports/` pipeline (via `report_schema.py`) is still being wired up by
  another agent. Once that pipeline is confirmed working end-to-end, all four legacy files
  should be removed.
- **`src/run.sh` / `src/test_tools.py`**: `run.sh` currently runs `crawler.py` ->
  `test_tools.py` -> `server.py`, and `test_tools.py` reads `trends_raw.json` directly.
  Once `report_schema.py` / `taxonomy.py` are integrated into `summarize.py`/`server.py`,
  the pipeline order and the test fixture path will likely need updating to point at
  `data/reports/*.json` instead of the legacy cache file. Not changed here — those files
  are owned by other agents.
- **No stray `.git` directories** were found anywhere else in the tree besides the repo
  root `.git/`.
- **No `__pycache__` dirs or `.pyc` files** were present anywhere in the tree at audit
  time, so nothing needed deleting. `src/.gitignore` already excludes them; root
  `.gitignore` did not, so `__pycache__/`, `*.pyc`, `*.pyo`, `.venv/` were added there
  tonight as a safety net for anything created at the repo root in the future.
- `web/.next/` and `web/node_modules/` are already covered by `web/.gitignore`
  (`/node_modules`, `/.next/`); root `.gitignore` also lists `node_modules`/`.next` as a
  belt-and-suspenders entry. No changes needed there.
