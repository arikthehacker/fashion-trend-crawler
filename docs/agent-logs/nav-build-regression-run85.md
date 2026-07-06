# Run 85 — full regression sweep (clean wipe)

Branch: ari3lla-index-loop-improvements

## 1. Stray process check
`wmic process where "name='node.exe'"` and `...python.exe...` both returned "No
Instance(s) Available." — no stragglers to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` from `web/` — clean, no output, exit 0.

## 3. Lint
`npx eslint .` — clean, no output, exit 0.

## 4. Build
`npm run build` from clean state — succeeded, no warnings.
- `copy-reports.mjs`: copied 78 report(s) into `public/data/reports/`.
- Route table: 191 total paths generated (7 workers), including:
  - `/reports/[date]`: 78 static pages
  - `/signals/[slug]`: 96 static pages
  - plus static top-level routes (/, /about, /archive, /case-study, /glossary, /icon,
    /methodology, /robots.txt, /rss.xml, /search, /sitemap.xml, /sources, /taxonomy,
    /timeline, /_not-found)
- Pagefind postbuild indexed 186 HTML files, 6115 words, 0 errors.

## 5. Grep verification of built output (web/out)
All confirmed present and correct:
- Signal-anchor deep-linking permalinks: `id="signal-sheer-layering"`,
  `id="signal-soft-tailoring"` etc. present in report pages.
- Dark mode: `prefers-color-scheme` block present in `app/globals.css` (OS-driven, no
  manual toggle — matches documented design, not a manual toggle element).
- Skip-link: `#main-content` present in output.
- Open Graph tags: `og:title`, `og:description`, `og:type`, `og:url` present.
- RSS: `atom:link` self-reference present; exactly 50 `<item>` elements in `rss.xml`.
- Corrections banners: both 2027-05-17 and 2027-07-12 report pages contain
  `correction`/`CORRECTION` text (banner markup renders on both).
- Signal titles: real `<h3>` elements confirmed (4 signal-title h3s + additional
  section h3s in `reports/2026-07-06.html`, matching the 4 `top_signals` in that
  report's JSON).
- `/signals/[slug]` recency status line: confirmed rendering, e.g. "Last appeared
  2026-07-06 — 76 published reports since, with no further occurrence on file." (from
  `getSignalRecencyStatus()` in `lib/reports.ts`, consumed in
  `app/signals/[slug]/page.tsx`).
- JSON-LD: `application/ld+json` present in report pages.
- Sources/Taxonomy pages: both render real `<h1>` content.
- Archive year-grouping headers: `<h2>` elements for `2027` and `2026` confirmed in
  `archive.html`.

Note: static export pages live at `out/<route>.html` (e.g. `out/reports/2026-07-06.html`,
`out/archive.html`), not `out/<route>/index.html` — an early grep pass targeted the wrong
filenames and produced false "not found" errors before this was caught and corrected.

## 6. Report-page count vs data count
`data/reports/*.json`: 78 files.
`web/out/reports/*.html`: 78 files.
Exact match — no drift.

## 7. Concurrent work note
Did not touch `archive/page.tsx` per instructions. No signs in this run's build output
of a partially-wired `archive_tags` filter or other in-progress frontend change — the
archive page content observed (year headers, listing) is consistent with prior
committed state, not new WIP. No `docs/confidence-discipline-precedents.md` precedent-13
edits observed or touched (docs-only, out of scope for this log).

## Result
No regression found. All checks pass: tsc clean, eslint clean, build clean (no
warnings), all prior fixes verified intact in built output, report/page counts match
exactly (78/78). No code changes made this run.
