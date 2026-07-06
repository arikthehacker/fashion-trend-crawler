# Project Structure (Target / Intended End-State)

This reflects the intended structure per `docs/ARI3LLA INDEX.txt` (sections 23 & 40),
mapping the doc's `app/` onto this repo's `web/app/`. Some paths already existed before
the reorg work; others were built by parallel agents. Status noted per entry. Last synced
against the actual file tree on 2026-07-06 (run 23 doc-sync pass updated the report
count/date range, added `/glossary`, and confirmed the `lint-web` CI job / jsx-a11y
lint config below without re-walking the whole tree). Run 24: removed the specific
report count/date-range claims below (they had already gone stale twice, runs 18 and
23) — see `data/reports/` or the live `/archive` page for the current count instead.

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
│       │                       see `ls data/reports/` or the live `/archive` page for
│       │                       the current count/date range (deliberately not
│       │                       enumerated here — this list went stale twice, runs
│       │                       18 and 23, see docs/agent-logs/report-count-destaling-run24.md)
│       ├── 2026-05-07.json     existing — first report under new schema
│       ├── 2026-07-13.json     existing — dated report (see agent-logs/real-report-2026-07-13.md)
│       ├── 2026-07-27.json     existing — dated report (thin/low-volatility stretch begins)
│       ├── 2026-08-24.json     existing — dated report (thin/low-volatility stretch ends)
│       ├── 2026-09-07.json     existing — dated report (fashion month window begins)
│       └── ...                 existing — additional dated reports (see note above)
├── docs/
│   ├── ARI3LLA INDEX.txt       existing — the reorg/spec doc driving this work, read-only
│   ├── CHANGELOG.md            existing — master reconciled log
│   ├── PROJECT_STRUCTURE.md    existing — this file
│   ├── PROMPT_CHANGELOG.md     existing — review trail for summarize.py's build_prompt()
│   ├── EDITORIAL_CALENDAR.md   existing — known recurring high-volatility windows
│   │                           (fashion month Sept-Oct 2026), so a volatility shift
│   │                           isn't mistaken for a crawl/sourcing anomaly
│   └── agent-logs/             existing — per-agent hygiene/status/provenance logs;
│                               166+ files as of this sync and growing every run
│                               (deliberately not enumerated here — see `ls
│                               docs/agent-logs/` for the current list; this is the same
│                               drift pattern as the report-count issue above)
├── src/
│   ├── .gitignore              existing — covers __pycache__/*.pyc already
│   ├── crawler.py              existing — BFS crawler, robots.txt-respecting, UNCHANGED core logic
│   ├── summarize.py            existing — calls Claude to produce a report (doc section 21 tone)
│   ├── server.py               existing — MCP server (crawl/cache/search/list/get report tools)
│   ├── report_schema.py        existing — Report/Signal/CollectionWindow schema, save/load/list by date
│   ├── taxonomy.py             existing — source sector / confidence / volatility / origin vocab + classify_source(url)
│   ├── test_tools.py           existing — tests the old raw-cache pipeline; unrelated to
│   │                           report_schema.py, left alone unless migrating it
│   ├── validate_all_reports.py existing — CI check (run 4), validates every file in
│   │                           data/reports/ against the schema; also runs
│   │                           derive_confidence() as a non-blocking warning (run 8)
│   ├── audit_confidence.py     existing (run 7) — reusable script comparing assigned
│   │                           confidence vs. derive_confidence() across all reports;
│   │                           periodic review tool, not wired into CI
│   ├── check_field_coverage.py existing (run 25) — enumerates every Report/Signal schema
│   │                           field and flags any not typed in reports.ts or referenced
│   │                           in a .tsx file; non-blocking, not wired into CI
│   ├── check_heading_patterns.py  existing (run 22, revisited run 29) — heuristic scanner
│   │                           for the recurring styled-`<p>`-as-heading bug that ESLint/
│   │                           jsx-a11y cannot catch; not wired into CI, manual/heuristic
│   ├── generate_archive_manifest.py  existing (run 43) — produces a JSON manifest of this
│   │                           site's own /reports/[date] URLs + content hashes for a human
│   │                           operator to feed into archive.org's Save Page Now, once a real
│   │                           deployed SITE_URL exists; does not call any Wayback API itself,
│   │                           not wired into CI
│   └── run.sh                  existing — fixed run 1 (no longer stale): runs
│                               crawler.py -> summarize.py (classify+summarize+save dated report)
├── .github/
│   └── workflows/validate-reports.yml   existing — two jobs: `validate` (py_compile +
│       schema validation of data/reports/) and `lint-web` (ESLint incl. jsx-a11y over
│       web/), both on push/PR
└── web/
    ├── .gitignore               existing — covers node_modules/.next already
    ├── package.json / package-lock.json   existing — Next.js app config; `pagefind`
    │                              devDependency + `postbuild` script
    │                              (`pagefind --site out --output-subdir _pagefind`)
    ├── next.config.ts           existing — `output: "export"` set (required for Pagefind
    │                              to index the static `out/` build); also invokes
    │                              `scripts/copy-reports.mjs`'s `copyReports()` directly
    │                              at config-eval time (run 46), so the JSON copy happens
    │                              on any build invocation, not just via the npm
    │                              "prebuild" lifecycle hook
    ├── scripts/
    │   └── copy-reports.mjs     existing (run 45, hardened run 46) — copies
    │                              data/reports/*.json into public/data/reports/ so the
    │                              static export serves each raw report at
    │                              /data/reports/<date>.json; backs the Dataset JSON-LD's
    │                              DataDownload and the visible "download raw data" link
    │                              on /reports/[date]
    ├── next-env.d.ts            existing
    ├── tsconfig.json / tsconfig.tsbuildinfo   existing
    ├── postcss.config.mjs       existing
    ├── eslint.config.mjs        existing — layers extra `eslint-plugin-jsx-a11y` rules
    │                              (heading-has-content, anchor-has-content, etc.) on top
    │                              of eslint-config-next's defaults; explicitly notes no
    │                              jsx-a11y rule can catch a styled `<p>` masquerading as
    │                              a heading — see workflow convention #3 in the skill doc
    ├── app/
    │   ├── page.tsx              existing — homepage (hero/tagline/footer, section 2/25 voice)
    │   ├── layout.tsx            existing — site-wide title/description metadata
    │   ├── globals.css           existing
    │   ├── favicon.ico           existing
    │   ├── archive/page.tsx      existing — lists all dated reports
    │   ├── reports/[date]/page.tsx   existing — renders one report (module order, section 20/36);
    │   │                          carries NewsArticle + Dataset JSON-LD (run 46: Dataset
    │   │                          includes a CC BY 4.0 `license` URL and a `DataDownload`
    │   │                          distribution pointing at /data/reports/<date>.json), plus a
    │   │                          human-visible "download raw data" link to the same file
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
    │   ├── glossary/page.tsx     existing — definitions of aesthetic terms/cultural
    │   │                          references, filtered to only terms that actually
    │   │                          appear in data/reports/*.json (not a static dictionary)
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
