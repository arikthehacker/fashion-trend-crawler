# Nav/Build Regression Sweep — Run 72

Scope: full regression sweep per standing checklist (stray processes, tsc,
eslint, build, built-output grep checks for prior fixes, spot-check newest
report pages).

## Process check
No stray `node.exe`/`python.exe` processes found (both `wmic` queries returned
"No Instance(s) Available"). Nothing to kill.

## Checks
1. `npx tsc --noEmit` — clean, no output.
2. `npx eslint .` — clean, no output.
3. `npm run build` — succeeded. Only output was expected benign
   `[glossary] no DEFINITIONS entry for term "..."` notices (terms referenced
   in reports that don't yet have a glossary definition — not an error).

## Built-output verification of prior fixes
- Signal-anchor deep-linking permalinks (`id="signal-..."`): present.
- Dark mode: implemented as CSS-only `@media (prefers-color-scheme: dark)` in
  `app/globals.css` (2 occurrences) — this is the correct, established
  implementation (confirmed against run 59/61/64/71 logs); there is no JS
  toggle button by design.
- Skip-link: present across pages (`404.html`, `about.html`, report pages, etc.).
- Open Graph meta tags (`og:title`): present.
- RSS `atom:link` self-reference: present in `out/rss.xml`.
- Corrections banner (`revision_history`/correction markup): present on 35
  report pages with revision history.

## Regression found and fixed
**Finding:** initial `npm run build` (without cleaning `web/out` first) produced
only 64 of 65 report pages — `/reports/2027-09-27` (the newest report,
`data/reports/2027-09-27.json`) was missing from `web/out/reports/`, along with
its `.html`/`.txt` output, even though the JSON was valid and correctly named,
and `getAllReportDates()`/`generateStaticParams()` in `web/lib/reports.ts` and
`web/app/reports/[date]/page.tsx` contain no date filtering that would exclude
it.

**Root cause:** this was a **stale `web/out/` build artifact** left over from a
prior build run, not a code regression — `next build` with `output: "export"`
does not always fully reconcile a pre-existing `out/` directory against the
current route set on an incremental build. Doing `rm -rf web/.next web/out`
before rebuilding produced the correct, complete output:
154 HTML files (up from 152), 65/65 report pages, 65/65 signal/report data
represented.

**No source code was changed** — this is a build-hygiene issue, not a bug in
`web/lib/reports.ts` or `web/app/reports/[date]/page.tsx`. Recommend future
regression sweeps always do a clean `web/.next`/`web/out` wipe before judging
build completeness, since a partial/stale `out/` can silently hide missing
pages while `npm run build` still reports success.

## Spot check: newest 3 reports (post clean rebuild)
- `2027-09-13`: signal "New York SS28 schedule still unannounced" found in
  `reports/2027-09-13.html`.
- `2027-09-20`: signal "New York confirms SS28 schedule, unusually close to
  season start" found in `reports/2027-09-20.html`.
- `2027-09-27`: signal "Paris Fashion Week SS28 opens with published show
  order" and executive-summary text "Paris Fashion Week's Spring/Summer 2028
  schedule" both found in `reports/2027-09-27.html`.

## Result
No real code regressions. Build-artifact staleness caused an apparent missing
page; resolved by clean rebuild (no code touched). tsc, eslint, and build all
pass clean on the final clean build. 65/65 report pages and 76/76 signal pages
render (157 total app routes → 154 static HTML files after clean build).
