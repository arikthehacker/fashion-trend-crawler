# Run 77 — Full Regression Sweep (nav/build)

Date: 2026-07-06
Branch: ari3lla-index-loop-improvements

## 0. Stray process check
`wmic process where "name='node.exe'"` and `python.exe` both returned "No Instance(s) Available." — nothing to kill.

## 1. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` — **clean, no output.**

## 2. Lint
`npx eslint .` — **clean, no output.**

## 3. Build
`npm run build` — **succeeded.** No warnings.
- Next.js 16.2.4 (Turbopack)
- Route summary: 169 total static params generated (`/reports/[date]` × 69 dates, `/signals/[slug]` × 83 slugs, plus ~17 static app routes: `/`, `/about`, `/archive`, `/case-study`, `/glossary`, `/methodology`, `/robots.txt`, `/rss.xml`, `/search`, `/sitemap.xml`, `/sources`, `/taxonomy`, `/timeline`, `/icon`, `/_not-found`).
- `prebuild` copy-reports script: copied 69 reports into `public/data/reports/`.
- `postbuild` pagefind: indexed 164 HTML pages, 5783 words, 0 errors.

## 4. Report count check
- `data/reports/*.json` at time of sweep: **70 files** (repo working tree).
- Build-time report copy / generated report pages: **69**.
- This 70-vs-69 mismatch is **not a regression** — file timestamps show `data/reports/2026-07-20.json` was modified at 14:28 (most recent of all report JSONs, well after the others which cluster at 09:27/11:39), consistent with a concurrent agent actively writing a new report mid-sweep. The build itself (prebuild copy-reports + generateStaticParams) is internally consistent at 69/69/69 (json copied / report dirs / signal occurrences), which is what this check is meant to catch. Re-run the count once the concurrent report-adding agent finishes to confirm final parity.

## 5. Built-output grep verification
All prior fixes confirmed intact in `web/out`:
- **Signal anchor permalinks**: `id="signal-*"` anchors present in report HTML (e.g. `id="signal-sheer-layering"`, `id="signal-1990s-minimalism-revival"`) — **pass**.
- **Dark mode**: implemented as automatic `@media (prefers-color-scheme: dark)` block in `app/globals.css` (not a manual JS toggle — confirmed this is the established approach, no toggle component exists in the codebase) — **pass**.
- **Skip link**: "Skip to main..." text present in `out/index.html` — **pass**.
- **Open Graph meta**: `og:description`, `og:title`, `og:type`, `og:url` all present in `out/index.html` — **pass**.
- **RSS atom:link self-reference**: `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" type="application/rss+xml" />` present in `out/rss.xml` — **pass**.
- **Corrections banner**: "correction" text found rendering across multiple report pages (e.g. 2026-05-07, 2026-07-06, 2026-07-13...) — **pass**.
- **NEW (run 76 fix) — signal titles wrapped in real `<h3>`**: confirmed `<h3>` elements wrapping signal title anchors in report pages (e.g. `out/reports/2026-07-06.html`), not bare `<Link>`/`<a>` text — **pass, accessibility fix holds**.
- **`/signals/[slug]` recency status line**: "Last appeared ... published reports since, with no further occurrence on file." renders correctly across sampled signal pages (`1990s-minimalism-revival`, `2026-bof-voices-gathering`, `antwerp-lineage-raw-edge-wider-claim`) — **pass**.

## Summary
No real regressions found. All checks pass (tsc, eslint, build, and every grepped output-integrity check including the two new-this-run verifications). The only discrepancy noted (70 vs 69 report JSONs) is attributable to a concurrent in-progress agent adding a new report during this sweep, not a defect in already-committed code. No code changes were made.
