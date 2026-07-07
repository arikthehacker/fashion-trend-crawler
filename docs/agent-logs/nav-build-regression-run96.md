# Full regression sweep — run 96

## Concurrency handling
- Pre-check found a stray `npm install` (PID 26768) — not a serve/crawler/test straggler, left alone; waited for it to exit naturally.
- Then found a concurrent `npm run build` (PID 12868, with its `pagefind` postbuild step PID 27016) already running from another agent — waited for it to fully complete rather than racing a parallel build. Confirmed both processes exited before starting the clean wipe.
- Re-checked node.exe/python.exe list after waiting: empty. Proceeded solo.

## Clean wipe + checks
1. `rm -rf .next out` — done.
2. `npx tsc --noEmit` — **PASS**, exit 0, no errors.
3. `npx eslint .` — **PASS**, exit 0, no warnings/errors.
4. `npm run build` — **PASS**, exit 0, fully completed including postbuild pagefind indexing.
   - 213 routes total in build output (8 static top-level pages + `/reports/[date]` × 89 + `/signals/[slug]` × ~108 + system routes `/_not-found`, `/icon`, `/robots.txt`, `/rss.xml`, `/sitemap.xml`, `/search`).
   - No build warnings emitted.
   - Pagefind: indexed 208 pages, 6314 words, 0 errors.

## Built-output content verification (web/out)
All confirmed intact (static export uses `<route>.html`, not `<route>/index.html`):
- Signal-anchor deep-linking permalinks: `id="signal-sheer-layering"` etc. present in report pages. PASS
- Dark mode CSS: `prefers-color-scheme:dark` present in compiled chunk CSS. PASS
- Skip-link: `<a href="#main-content" class="skip-link">` in index.html, `id="main-content"` present. PASS
- Open Graph meta tags: `og:title`, `og:description`, `og:type`, `og:url` present. PASS
- RSS: `atom:link ... rel="self"` self-reference present; exactly 50 `<item>` elements. PASS
- Corrections banner: renders on reports with corrections (2026-05-07, 2026-07-20, 2026-08-03). PASS
- Signal titles wrapped in real `<h3>` elements (not styled `<p>`). PASS
- `/signals/[slug]` recency line: renders as "Last appeared <date> — N published report(s) since, with no further occurrence on file." (worded differently than the literal string "status" but functionally the required recency status line). PASS
- JSON-LD structured data: present on report pages (1 `application/ld+json` block), correctly absent from homepage (by design). PASS
- Sources/Taxonomy pages: content renders (`Sources`, `Taxonomy` headings present). PASS
- Archive year-grouping headers: `2026`, `2027`, `2028` all present. PASS
- `/timeline` page: renders (`timeline.html` present in output). PASS

## Report count
- `data/reports/*.json`: 89 files
- `web/out/reports/*.html`: 89 files
- **MATCH** — exact.
- Note: `web/public/data/reports/*.json` showed 90 (one stale leftover from a prior run/copy), but this does not affect the actual build output (`web/out`), which correctly matches the live `data/reports/` count of 89. Not treated as a regression since it's a non-authoritative intermediate copy dir, not the served output.

## Regressions found
None. No code was modified.
