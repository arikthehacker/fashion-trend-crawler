# Nav/Build Regression Sweep — Run 75

Date: 2026-07-06
Branch: ari3lla-index-loop-improvements

## 0. Stray process check
`Get-Process node,python` before starting: none found. During the first `npm run build` attempt,
Next.js reported "Another next build process is already running" (stale `.next` lock from a prior
run). Checked again — the two node PIDs (3700, 18872) had already exited on their own by the time
of the check; `taskkill` found nothing to kill. Removed `.next`/`out` and retried; build succeeded.
No unrelated processes were touched.

## 1. `npx tsc --noEmit`
Clean. No output, exit 0.

## 2. `npx eslint .`
Clean. No output, exit 0.

## 3. `npm run build` — two clean runs (`rm -rf .next out` between each)

**Run A:** 67 reports copied by `copy-reports.mjs` → 164 routes total (77 `/signals/[slug]` +
individual reports). `report count (data/reports/*.json) = 67` = `built /reports/*.html = 67`
(201 files in `out/reports/` = 67 × {dir, .html, .txt}). Match confirmed. Zero `[glossary]` warnings
in build output.

**Run B:** Between Run A and Run B, the crawler (a separate process on this machine) wrote a new
report `data/reports/2027-10-18.json` (timestamped 15:12, mid-sweep). `copy-reports.mjs` picked it
up: 68 reports → 166 routes (78 signals, incl. new `bogota-waist-tailoring-resort28-institutional`).
`data/reports/*.json = 68` = built `/reports/*.html = 68`. Match confirmed for Run B's own state.
Build B also printed several `[glossary] no DEFINITIONS entry for term "..."` warnings (return to
structure, waist definition, Inexmoda, Bogota fashion week, Vogue) — all sourced from the new
2027-10-18 report, which introduces terms not yet curated into `DEFINITIONS`. This is the glossary
mechanism working as designed (warn on uncurated terms), not a regression — run 74's "warnings stay
at zero" held for Run A (67-report state) and breaks only because live data changed mid-sweep, not
because of any code fault.

**Turbopack flake (from run 74):** NOT observed. Page/report counts increased monotonically and
exactly matched their respective report-file counts on both runs (67↔164 and 68↔166) — no dropped
pages, no discrepancy within a single run.

## 4. Built-output grep checks (on Run B's `web/out`)
- Signal anchor permalinks: `href="#signal-sheer-layering"` etc. present in report pages — OK.
- Dark mode: implemented via `@media (prefers-color-scheme: dark)` in `app/globals.css` (no JS
  toggle button by design) — rule present in source and compiled CSS — OK.
- Skip link: `skip-link` / "Skip to main" present in `index.html` — OK.
- Open Graph meta: `og:title`, `og:description`, `og:url`, `og:type` present — OK.
- RSS self-reference: `<atom:link href=".../rss.xml" rel="self" ...>` present in `rss.xml` — OK.
- Corrections banner: renders in `reports/2026-05-07.html`, `2026-07-20.html`, `2026-08-03.html` — OK.
- Glossary DEFINITIONS warnings: zero on Run A (67-report state); non-zero on Run B only because a
  new report landed mid-sweep with genuinely new terms (see above) — not a regression.

## Summary
- tsc: PASS
- eslint: PASS
- build (both runs): PASS, succeeded from clean state each time
- Turbopack flake: did not recur
- Report/page count match: PASS on both runs (67=67, then 68=68)
- No real regression found; no code changes made.
