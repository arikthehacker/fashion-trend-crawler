# Nav/build regression sweep — run 92

Branch: ari3lla-index-loop-improvements

## Process check
- No stray node.exe/python.exe processes found; nothing killed.

## Clean build sweep
- `rm -rf .next out` then `npx tsc --noEmit` — clean, no errors.
- `npx eslint .` — clean, no errors/warnings.
- `npm run build` — succeeded, fully completed (including postbuild Pagefind index).
  - 84 reports copied by copy-reports.mjs.
  - Routes: 202 static pages generated (84 `/reports/[date]`, 99 `/signals/[slug]`,
    plus static top-level routes: /, /about, /archive, /case-study, /glossary, /icon,
    /methodology, /robots.txt, /rss.xml, /search, /sitemap.xml, /sources, /taxonomy,
    /timeline, /_not-found).
  - No build warnings.
  - Pagefind: indexed 197 HTML files, 6222 words, 0 errors.

## Report count reconciliation
- `data/reports/*.json`: 84 files.
- `web/out/reports/*.html`: 84 files. Match confirmed.

## Built-output regression grep (all against web/out, using `<route>.html` naming per static export)
- Signal-anchor deep-linking permalinks: present (`id="signal-*"` in reports/2026-07-06.html).
- Dark mode CSS: present — `prefers-color-scheme: dark` found in
  `web/out/_next/static/chunks/*.css` (chunk hash filename, not `/css/`, this run — not a regression, just Turbopack's current output naming).
- Skip-link: `#main-content` present in index.html.
- Open Graph meta: `property="og:title"` present.
- RSS atom:link self-reference: present, correct rel="self" href.
- RSS item count: exactly 50 `<item>` elements.
- Corrections banner: present in reports/2026-05-07.html.
- Signal titles as real `<h3>`: confirmed in reports/2026-07-06.html (three `<h3>` elements checked).
- /signals/[slug] recency status line: confirmed via "recurring"/"Volatil..." text in
  signals/nyfw-fw28-womens-calendar-confirmed.html.
- JSON-LD structured data: present on report pages (reports/2026-07-06.html), correctly
  absent on homepage (by design — report-pages-only).
- Sources page content: present (sources.html).
- Taxonomy page content: present (taxonomy.html).
- Archive year-grouping headers: 2026, 2027, 2028 all present in archive.html.

## Result
All checks passed. No regressions found. No code changes made.
