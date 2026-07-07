# Run 80 — full regression sweep (clean wipe)

## 1. Stray processes
`wmic process where "name='node.exe'"` and `where "name='python.exe'"` both returned
"No Instance(s) Available." — nothing to kill.

## 2. Clean wipe + tsc
`rm -rf web/.next web/out` then `npx tsc --noEmit` from `web/` — clean, zero errors.

## 3. ESLint
`npx eslint .` from `web/` — clean, zero errors/warnings.

## 4. Build
`npm run build` from `web/` (clean state, prebuild ran `copy-reports.mjs`: copied 72
reports) — succeeded. No build warnings in output.
- 176 total generated paths (Next.js route summary): includes 72 `/reports/[date]`
  pages, 87 `/signals/[slug]` pages, plus static routes (`/`, `/about`, `/archive`,
  `/case-study`, `/glossary`, `/methodology`, `/search`, `/sources`, `/taxonomy`,
  `/timeline`, `/rss.xml`, `/sitemap.xml`, `/robots.txt`, `/icon`, `/_not-found`).
- Postbuild Pagefind indexing succeeded: 171 pages, 5874 words, 0 errors.

## 5. Built-output feature grep (against web/out)
All confirmed present and intact:
- Signal-anchor deep-linking permalinks: `id="signal-sheer-layering"` etc. present in
  `reports/2026-07-06.html`.
- Dark mode: no manual toggle exists by design (per SKILL.md — OS-preference-driven);
  confirmed `prefers-color-scheme` block present in `app/globals.css`. Not a regression.
- Skip-link: `#main-content` present in report page HTML.
- Open Graph meta: `og:title`, `og:description`, `og:type`, `og:url` all present.
- RSS `atom:link` self-reference: `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" .../>` present in `rss.xml`.
- RSS item count: exactly 50 `<item>` elements — confirmed via `grep -o '<item>' rss.xml | wc -l`.
- Corrections banner: "correction" text present in reports/2026-05-07, 07-06, 07-13,
  07-20, 07-27 HTML.
- Signal titles as real headings: `<h3 ...>` tags confirmed wrapping signal titles in
  report page HTML (not styled `<p>`).
- `/signals/[slug]` recency status line: confirmed rendered text "Last appeared
  2026-07-06 — 70 published reports since, with no further occurrence on file." in
  `signals/1990s-minimalism-revival.html`, sourced from `getSignalRecencyStatus()` in
  `lib/reports.ts` per `app/signals/[slug]/page.tsx` lines 8/46/93-103.
- JSON-LD structured data: `application/ld+json` present in report page HTML.

## 6. Report-page count vs data/reports
`data/reports/*.json` = 72 files. Build's `/reports/[date]` static params = 72 pages
(prebuild log: "copied 72 report(s)"). Match confirmed.

## 7. Concurrent work note
Did not touch `web/app/about/page.tsx` or `web/app/case-study/page.tsx` (other agents'
scope this run). No build changes observed that trace to those files during this sweep;
if their freshness-audit edits land mid-sweep on a shared tree, treat any late diff in
those two files as their in-progress work, not a regression from this pass.

## Result
No regressions found. No code changes made — this was a clean, all-green sweep.
