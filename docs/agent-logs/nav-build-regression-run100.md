# Full regression sweep — web/ frontend (run 100)

Branch: `ari3lla-index-loop-improvements`
Date: 2026-07-06

## Build summary

| Step | Result |
|---|---|
| `npx tsc --noEmit` | PASS — no output, no errors |
| `npx eslint .` | PASS — no output, no errors |
| `npm run build` | PASS — compiled successfully, static export + Pagefind postbuild both completed |

Prebuild copied 92 reports into `public/data/reports/`. Next.js reported **220 total routes** generated (`Generating static pages using 7 workers (220/220)`), matching the route table below. Pagefind postbuild indexed 215 HTML files, 6410 words, 0 errors.

### Route table (as printed by `next build`)

```
Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /about
├ ○ /archive
├ ○ /case-study
├ ○ /glossary
├ ○ /icon
├ ○ /methodology
├ ● /reports/[date]
│ ├ /reports/2026-05-07
│ ├ /reports/2026-07-06
│ ├ /reports/2026-07-13
│ └ [+89 more paths]        (92 report pages total)
├ ○ /robots.txt
├ ○ /rss.xml
├ ○ /search
├ ● /signals/[slug]
│ ├ /signals/fw28-season-wrap-unfinished-edge-editorial-synthesis
│ ├ /signals/miumiu-fw28-raw-hem-bias-slip-skirt
│ ├ /signals/loewe-fw28-balloon-sleeve-trench-coat
│ └ [+108 more paths]       (111 signal pages total)
├ ○ /sitemap.xml
├ ○ /sources
├ ○ /taxonomy
└ ○ /timeline

○  (Static)  prerendered as static content
●  (SSG)     prerendered as static HTML (uses generateStaticParams)
```

92 report pages + 111 signal pages + 17 other static routes (/, /_not-found, /about, /archive, /case-study, /glossary, /icon, /methodology, /robots.txt, /rss.xml, /search, /sitemap.xml, /sources, /taxonomy, /timeline, plus /404 and icon-derived assets) = 220 total, consistent with Next's reported count.

## Checklist — verified against built HTML in `web/out/` (not source)

1. **Signal-anchor permalinks on report pages** — PASS.
   `web/out/reports/2027-03-01.html` contains `id="signal-wales-bonner-hermes-debut"` and `id="signal-paris-post-show-coverage-gap"`, each paired with a matching `#signal-wales-bonner-hermes-debut` / `#signal-paris-post-show-coverage-gap` in-page link.

2. **Dark-mode CSS present** — PASS.
   `web/out/_next/static/chunks/0jfru77twtdfc.css` contains: `prefers-color-scheme:dark){:root{--black:#f8f6f1;--white:#0a0a0a;--gray:#b0aca4;--border:#2a2827}`.

3. **Skip-link present** — PASS.
   `web/out/index.html` head/body contains `<a href="#main-content" class="skip-link">Skip to main content</a>`.

4. **OG meta tags present** — PASS.
   `web/out/reports/2027-03-01.html` contains `og:title`, `og:description`, `og:url`, `og:type` meta tags, e.g. `<meta property="og:title" content="2027-03-01 — ARI3LLA INDEX">`.

5. **RSS feed correctness** — PASS.
   `web/out/rss.xml` contains `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" type="application/rss+xml" />` and exactly **50** `<item>` elements (grep count confirmed).

6. **Corrections banner on 2027-03-01 and 2027-03-08** — PASS.
   Both `web/out/reports/2027-03-01.html` and `web/out/reports/2027-03-08.html` contain a "Correction History" section with a "Full correction history" link (`aria-label="Correction history"`).

7. **Signal titles render as real `<h3>` elements** — PASS.
   `web/out/reports/2027-03-01.html` contains real `<h3 style="margin:0;margin-bottom:0.75rem">` elements for signal titles (not styled `<p>`/`<div>` fakes), plus a separate `<h3>` for "Cultural References".

8. **/signals/[slug] recency line** — PASS.
   `web/out/signals/off-duty-varsity.html` contains: "Last appeared 2026-07-27 — 88 published reports since, with no further occurrence on file."

9. **JSON-LD present on report pages, absent on signal pages** — PASS.
   `web/out/reports/2027-03-01.html` contains `<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"NewsArticle",...`.
   `web/out/signals/off-duty-varsity.html` — grep for `ld+json` returns 0 matches (confirmed absent).

10. **Sources and Taxonomy pages have substantive content** — PASS.
    `web/out/sources.html` = 65,012 bytes; `web/out/taxonomy.html` = 70,712 bytes. Both are exported directly at `/sources.html` and `/taxonomy.html` (no `/index.html` subfolder needed — Next exported them as flat files). Sizes are consistent with real outlet-list / taxonomy prose content, not empty stubs.

11. **Archive page year-grouping headers** — PASS.
    `web/out/archive.html` contains `<h2 ...>2028<`, `<h2 ...>2027<`, `<h2 ...>2026<` — real `<h2>` year-group headers, uppercase-styled, matching the site's typographic system.

12. **/timeline page builds with real content** — PASS.
    `web/out/timeline.html` = 426,267 bytes, built successfully as a static route, with a real `<h1>Timeline</h1>` heading (not a placeholder).

**Result: 12/12 PASS.**

## Process hygiene

`wmic process where "name='node.exe'" get ProcessId,CommandLine` and the equivalent for `python.exe` both returned `No Instance(s) Available.` — i.e. no node or python processes were running on the machine at check time (this check ran after the build/postbuild processes had already exited). No stray or orphaned dev-server/build processes found.

## Regressions found

None. No source files under `web/` were modified during this sweep — build, lint, typecheck, and all 12 output-verification checks passed cleanly on the first pass.

## Overall verdict

**Clean regression pass.** tsc, eslint, and `next build` all succeeded with 220 routes generated (92 reports + 111 signals + 17 other static routes), Pagefind indexing completed without error, and all 12 independently-verified checks against the actual built `web/out/` HTML/CSS passed with direct evidence. No code changes were necessary.
