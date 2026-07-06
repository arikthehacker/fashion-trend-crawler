# Nav/Build Regression Sweep — Run 89

Date: 2026-07-06
Branch: ari3lla-index-loop-improvements

## Process hygiene
- Checked for stray node.exe/python.exe processes before starting: none found (`wmic process where "name='node.exe'"` and `python.exe` both returned "No Instance(s) Available"). No kills needed.

## Clean wipe + checks
1. `rm -rf .next out` — done.
2. `npx tsc --noEmit` — clean, no output, exit clean.
3. `npx eslint .` — clean, no output, exit clean.
4. `npm run build` — succeeded and ran to full completion (waited for Turbopack static generation, page finalization, and the postbuild `pagefind` indexing step to finish before inspecting output, per the run-86 false-alarm lesson).
   - 81 reports copied by `scripts/copy-reports.mjs` (prebuild).
   - 196 static pages generated (78 report dates + 3 shown, 95 signal slugs + 3 shown, plus static routes).
   - No build warnings.
   - Postbuild pagefind indexed 191 HTML files / 6178 words successfully.

## Built-output verification (in `web/out`)
Note: static export emits `<route>.html` files (not `<route>/index.html`) alongside same-named directories containing Next's RSC payload chunks — greps were pointed at the `.html` files.

- Signal-anchor deep-linking permalinks: confirmed, e.g. `id="signal-sheer-layering"` present in `out/reports/2026-07-06.html`, with permalink anchor/aria-label pattern in `app/reports/[date]/page.tsx`.
- Dark mode: confirmed via CSS, not a JS toggle — `@media (prefers-color-scheme:dark)` present in the built/minified CSS bundle (`out/_next/static/chunks/*.css`). This is by design (system-preference based, no toggle control in source).
- Skip-link: confirmed, `.skip-link` class in `globals.css` and `<a href="#main-content" className="skip-link">` in `layout.tsx`.
- Open Graph meta tags: confirmed, `og:description`, `og:title`, `og:type`, `og:url` all present in `out/index.html`.
- RSS: confirmed `atom:link` self-reference present (count 1) and exactly 50 `<item>` elements in `out/rss.xml`.
- Corrections banner: confirmed rendering in `out/reports/2026-05-07.html` (a report with an actual correction) — "Correction" text and `correction-history` anchor both present.
- Signal titles wrapped in real `<h3>`: confirmed in `out/reports/2026-07-06.html`.
- `/signals/[slug]` recency status line: confirmed — "most recently published report" text rendered in built signal page HTML.
- JSON-LD structured data: confirmed on report pages (`application/ld+json` present in `out/reports/2026-07-06.html`); not present on the homepage or signal pages, consistent with source (`app/reports/[date]/page.tsx` is the only file emitting it).
- Sources / Taxonomy pages: confirmed distinct "Sources" / "Taxonomy" content rendered in `out/sources.html` / `out/taxonomy.html`.
- Archive year-grouping headers: confirmed `2026`, `2027`, `2028` all present in `out/archive.html`.

## Report count match
- `data/reports/*.json`: 81
- `web/out/reports/*.html`: 81
- Match confirmed exactly.

## Regressions found
None. All checks passed on a genuinely clean, fully-completed build. No code changes were made.
