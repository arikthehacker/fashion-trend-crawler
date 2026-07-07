# Nav/Build Regression Sweep — Run 91

Date: 2026-07-06
Branch: ari3lla-index-loop-improvements

## Process check
No stray leftover node.exe/python.exe serve/crawler/test processes found. Nothing killed.

## Clean wipe + checks
- `rm -rf .next out` — done
- `npx tsc --noEmit` — PASS, clean, no output
- `npx eslint .` — PASS, clean, no output
- `npm run build` — PASS, fully completed
  - prebuild copied 83 reports into public/data/reports
  - Compiled successfully, TypeScript check finished in 2.5s
  - Generated 200 static pages (7 workers)
  - Routes: /, /about, /archive, /case-study, /glossary, /methodology, /reports/[date] (83 paths), /rss.xml, /search, /signals/[slug] (100 paths), /sitemap.xml, /sources, /taxonomy, /timeline
  - No build warnings
  - postbuild: pagefind indexed 195 HTML pages, 6212 words, 0 errors

## Report count reconciliation
- data/reports/*.json: 83
- web/out/reports/*.html: 83
- Match confirmed exactly.

## Built-output verification (grepped web/out, accounting for `<route>.html` static export naming)
- Signal-anchor deep-linking permalinks on report pages — present (id="signal-..." anchors confirmed on out/reports/2026-07-06.html)
- Dark mode CSS (media query, no JS toggle) — present in out/_next/static/chunks/0jfru77twtdfc.css (prefers-color-scheme rule found); no JS toggle, as designed
- Skip-link — present on out/index.html
- Open Graph meta tags — present (og:title, og:description, og:type, og:url on out/index.html)
- RSS atom:link self-reference + exactly 50 `<item>` elements — confirmed in out/rss.xml
- Corrections banner rendering — present, found in 37 report HTML files
- Signal titles wrapped in real `<h3>` elements — confirmed (real `<h3 ...>` tags present, not just styled divs)
- /signals/[slug] recency status line — confirmed present (e.g. "most recently published report" wording on dior-couture-ss28-bias-cut-column-dress.html)
- JSON-LD structured data — present on report pages (app/reports/[date]/page.tsx emits application/ld+json). Confirmed this is report-page-only by design (no ld+json script in app/signals/[slug]/page.tsx source) — not a regression, just noting scope for future sweeps.
- Sources/Taxonomy page content — present, headings render on out/sources.html and out/taxonomy.html
- Archive year-grouping headers — confirmed 2026, 2027, 2028 `<h2>` headers present in out/archive.html

## Regressions found
None. All prior fixes intact. Build succeeded cleanly from a full wipe with no code changes required.

## Notes for concurrent agents
No conflicts observed with dormancy/save_report() work or glossary/page.tsx voice-compliance edits at time of this sweep; build was clean regardless.
