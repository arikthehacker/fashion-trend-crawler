# Run 79 — full regression sweep (clean wipe)

Branch: ari3lla-index-loop-improvements

## Process check
- `wmic process where "name='node.exe'"` and `python.exe`: no instances found. No stray
  processes to kill.

## Clean wipe + typecheck
- `rm -rf web/.next web/out` then `npx tsc --noEmit`: clean, no errors.

## Lint
- `npx eslint .`: clean, no errors/warnings.

## Build
- `npm run build`: succeeded from clean state. No warnings emitted.
- prebuild copied 71 reports into `public/data/reports/`.
- 174 total routes generated (per Next.js route summary): includes 71 `/reports/[date]`
  pages, 86 `/signals/[slug]` pages, plus static pages (home, archive, about, case-study,
  glossary, methodology, search, sources, taxonomy, timeline, rss.xml, sitemap.xml,
  robots.txt, icon, _not-found).
- Pagefind postbuild indexed 169 HTML pages / 5847 words successfully.

## Report count match
- `data/reports/*.json`: 71 files.
- `web/out/reports/` subdirectories: 71 (matches exactly).

## Built-output grep verification (web/out)
All prior fixes confirmed intact:
- Signal-anchor deep-linking permalinks: `href="#signal-sheer-layering"` etc. present in
  report pages.
- Dark mode: automatic `prefers-color-scheme: dark` CSS present in built stylesheet
  chunk (per project convention this is OS-preference-driven, no manual toggle by
  design — not a regression that no toggle button/JS exists).
- Skip-link: `href="#main-content"` present on homepage.
- Open Graph meta tags: `og:title`, `og:description`, `og:type`, `og:url` all present.
- RSS `atom:link` self-reference: present in `rss.xml`
  (`atom:link href=".../rss.xml" rel="self" ...`).
- Corrections banner: renders on reports with correction history (checked
  2026-05-07, 2026-07-20, 2026-08-03).
- Signal titles wrapped in real `<h3>` elements: confirmed in report pages (run 76 fix
  holding).
- `/signals/[slug]` recency status line: confirmed present on all 86 built signal pages
  (`Appeared in the most recently published report.` / `Last appeared ... published
  report(s) since ...` phrasing from `getSignalRecencyStatus()` in
  `web/app/signals/[slug]/page.tsx`).
- **New (run 79): RSS item count** — `web/out/rss.xml` contains exactly 50 `<item>`
  elements, not more. Confirmed via `grep -o '<item>' rss.xml | wc -l` → 50.

## Regressions found
None. All checks passed clean on first pass; no code changes were needed or made.

## Notes on concurrent work
- Did not touch `web/app/methodology/page.tsx` (other agent's assigned file this run).
- No other build-affecting changes observed that looked like in-progress concurrent
  work; build was clean throughout.
