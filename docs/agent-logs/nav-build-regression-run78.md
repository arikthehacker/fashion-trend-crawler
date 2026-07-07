# Run 78 — Full regression sweep (clean wipe)

Date: 2026-07-06

## 1. Stray processes
`wmic process where "name='node.exe'"` and `...python.exe...` both returned "No
Instance(s) Available." — no stray processes to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` from `web/` — clean, no output, no errors.

## 3. ESLint
`npx eslint .` from `web/` — clean, no output, no errors/warnings.

## 4. Build
`npm run build` from `web/` — succeeded from the clean state.
- prebuild copied 70 reports into `public/data/reports/`
- 171 total generated paths: static top-level pages + `/reports/[date]` (70 pages) +
  `/signals/[slug]` (84 pages) + sitemap/robots/rss/icon routes
- No build warnings printed by Next.js or the Pagefind postbuild step (166 HTML files
  indexed, 5811 words, 0 errors)

## 5. Regression-fix verification against `web/out`
All confirmed present and intact:
- **Signal-anchor deep-linking permalinks**: `id="signal-..."` anchors present in
  `reports/2026-07-06.html`.
- **Dark mode**: no manual toggle button exists in `app/` (grep for "toggle" in app dir
  is empty) — per project skill notes this is intentional, OS-`prefers-color-scheme`-driven
  only, not a UI toggle. `globals.css`'s dark-mode block is compiled into
  `_next/static/chunks/*.css`. Not a regression.
- **Skip-link**: `#main-content` present in `index.html`.
- **Open Graph meta tags**: `og:title`, `og:description`, `og:type`, `og:url` all present
  on `index.html`.
- **RSS atom:link self-reference**: present in `out/rss.xml`
  (`<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" .../>`).
  Note: rss.xml is another agent's assigned file this run — confirmed working as-is,
  did not touch it.
- **Corrections banner**: renders on report pages that have corrections (confirmed on
  2026-05-07, 2026-07-06, 2026-07-13 sample).
- **Signal titles as real `<h3>` elements** (run 76 fix): confirmed both on report pages
  (`reports/2026-07-06.html`) and on signal occurrence entries
  (`signals/1990s-minimalism-revival.html`) — real `<h3>` tags, not styled `<p>`.
- **`/signals/[slug]` recency status line** (run 76 feature): confirmed rendering, e.g.
  "Last appeared 2026-07-06 — 68 published reports since, with no further occurrence on
  file." Backed by `getSignalRecencyStatus()` in `lib/reports.ts`, consumed in
  `app/signals/[slug]/page.tsx`.

## 6. Report-page count vs data
`data/reports/*.json` = 70 files. `web/out/reports/` = 70 directories (one per report;
the 210 raw file count in that directory includes the paired `.html`/`.txt` static-export
artifacts per route, 70 × 3 = 210). Counts match exactly.

## 7. Concurrent work note
Did not touch `sitemap.ts`, `robots.ts`, or `rss.xml/route.ts` per instructions. No
in-progress-looking changes or unexpected new files observed in those areas at the time
of this sweep — everything checked rendered correctly and looked like pre-existing,
already-committed behavior, not partial WIP.

## Result
No regressions found. All checks pass. No code changes made this run.
