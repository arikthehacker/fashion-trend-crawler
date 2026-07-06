# Run 73 — Full regression sweep (build/nav) with clean-wipe lesson from run 72

## Context
Run 72 found a build without wiping `web/out` first left a stale, missing page. This run
applies that lesson: `web/.next` and `web/out` were fully removed before any build/typecheck
step, so results below reflect a truly clean build.

## 1. Stray process check
`wmic process where "name='node.exe'"` and the `python.exe` equivalent both returned
"No Instance(s) Available." — no stray node/python processes to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` — **PASS**, no output/errors.

## 3. Lint
`npx eslint .` — **PASS**, no output/errors.

## 4. Build (from clean state)
`npm run build` — **PASS**. 159 static pages generated across 7 workers.
Route summary: `/`, `/about`, `/archive`, `/case-study`, `/glossary`, `/icon`,
`/methodology`, `/reports/[date]` (65 dated pages), `/robots.txt`, `/rss.xml`, `/search`,
`/signals/[slug]` (77 signal pages), `/sitemap.xml`, `/sources`, `/taxonomy`, `/timeline`.
Postbuild Pagefind indexed 154 pages / 5492 words successfully.

Warnings: only the expected `[glossary] no DEFINITIONS entry for term "..."` lines for
terms not yet in the glossary's definitions map (proper names, event names, etc.) — this
is documented, non-blocking, informational behavior, not a regression.

## 5. Built-output grep verification (all confirmed intact)
- Signal-anchor deep-linking permalinks: `id="signal-..."` present in
  `web/out/reports/2026-07-06.html`.
- Skip-link: `#main-content` present in `web/out/index.html`.
- Open Graph meta tags: `og:title`/`og:description`/`og:type` present in
  `web/out/index.html`.
- RSS atom:link self-reference: confirmed in `web/out/rss.xml` —
  `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" .../>`.
- Dark mode: `@media (prefers-color-scheme: dark)` block present in
  `web/app/globals.css` (OS-preference-driven, no manual toggle — this is the documented
  design, not a gap).
- Corrections banner: `data/reports/2026-05-07.json` has a `revision_history` entry, and
  `web/out/reports/2026-05-07.html` renders "Correction"/"correction" text — banner
  rendering confirmed intact.

## 6. Report/page count reconciliation
- `data/reports/*.json`: **65** files.
- `web/out/reports/*.html`: **65** files.
- `web/out/reports/*/` (per-date directories): **65**.
- `web/out/reports/*.txt`: **65**.

All four counts match 1:1 per date (one `.html` + one directory + one `.txt` per report
date, consistent with the pattern observed in run 72). No missing pages this run — the
clean-wipe step avoided the stale-output problem run 72 identified.

## Outcome
No real regression found. All checks pass from a genuinely clean build. No code changes
made.
