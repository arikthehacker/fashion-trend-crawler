# Nav/Build Regression Sweep — Run 93

Branch: ari3lla-index-loop-improvements. Clean-wipe protocol (since run 72).

## Pre-flight
- `wmic process where "name='node.exe'"` / `python.exe` — no instances found, nothing to kill.

## Checks
1. `rm -rf .next out` then `npx tsc --noEmit` — **clean**, no output.
2. `npx eslint .` — **clean**, no output.
3. `npm run build` — **succeeded, fully completed**. 85 reports copied (`copy-reports.mjs`), 204 static pages generated, Pagefind postbuild indexed 199 HTML files / 6239 words. No warnings in build output.
4. Report-page count vs `data/reports/*.json`: **85 == 85**, exact match.

## Built-output verification (grepped `web/out`)
- Signal-anchor deep-linking permalinks: confirmed on report pages (`id="signal-sheer-layering"` etc. + matching `href="#signal-..."`) — intact.
- Dark mode CSS: `prefers-color-scheme: dark` present in `_next/static/chunks` CSS — intact.
- Skip-link: `href="#main-content"` and `id="main-content"` both present (1 each) on homepage — intact.
- Open Graph meta tags: `property="og:*"` present on homepage — intact.
- RSS: `atom:link` self-reference present, exactly 50 `<item>` elements in `rss.xml` — intact.
- Corrections banner: renders on multiple report pages (e.g. 2026-05-07, 2026-07-06, 2026-07-13) — intact.
- Signal titles as real `<h3>`: confirmed real `<h3>` elements — intact.
- `/signals/[slug]` recency status line: confirmed present ("First recorded ... occurrence on file" / "Appeared in the most recently published report.") — intact.
- JSON-LD structured data: present on report pages (`reports/2026-07-06.html`, 1 `application/ld+json` block), correctly absent on signal pages (0) — by design, intact.
- Sources/Taxonomy pages: content present on both — intact.
- Archive year-grouping headers: 2026, 2027, 2028 all present — intact.

## Result
All checks pass. No real regression found; no code changes made. Build output confirmed clean from a genuinely clean, fully-completed rebuild.
