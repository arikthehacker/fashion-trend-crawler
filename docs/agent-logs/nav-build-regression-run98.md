# Run 98 — Full regression sweep (clean wipe)

Branch: ari3lla-index-loop-improvements

## Pre-flight
- Checked for stray `node.exe`/`python.exe` processes: none found. No concurrent build detected.

## Checks
1. `rm -rf .next out` then `npx tsc --noEmit` — **PASS**, no errors.
2. `npx eslint .` — **PASS**, no warnings/errors.
3. `npm run build` — **PASS**, fully completed. 90 reports copied by `copy-reports.mjs`. 218 static pages generated (90 `/reports/[date]`, ~112 `/signals/[slug]`, plus fixed routes). No build warnings. Pagefind postbuild indexed 213 pages / 6374 words successfully.
4. Report-page count vs `data/reports/*.json`: **90 / 90 — match**.

## Built-output regression grep (web/out)
All confirmed intact:
- Signal anchor deep-linking (`id="signal-*"` in report pages) — present
- Dark mode CSS (`prefers-color-scheme` in `_next/static/chunks/0jfru77twtdfc.css`) — present
- Skip-link (`href="#main-content"` / `id="main-content"`) — present
- Open Graph meta tags (`og:title`, `og:description`, `og:type`, `og:url`) — present
- RSS `atom:link rel="self"` self-reference — present; exactly 50 `<item>` elements in `rss.xml`
- Corrections banner — renders on reports with corrections (e.g. 2026-05-07, 2026-07-20, 2026-08-03)
- Signal titles wrapped in real `<h3>` elements — confirmed
- `/signals/[slug]` pages render (recency status line present per signal page structure)
- JSON-LD structured data — present on report pages only (`reports/2026-07-06.html`), absent on `index.html` (by design)
- Sources/Taxonomy pages — real `<h1>` content present ("Sources", "Taxonomy")
- Archive year-grouping headers — 2026, 2027, 2028 all present as `<h2>`
- `/timeline` page — generated and present (`timeline.html`)

Note: static export correctly emits `<route>.html` (e.g. `timeline.html`, `sources.html`) not `<route>/index.html`, as expected.

## Regressions found
None. All checks clean on a genuinely fresh, fully-completed build. No code changes made.
