# Nav/build regression sweep — run 99

Branch: `ari3lla-index-loop-improvements`
Scope: read-only regression sweep of `web/` frontend. No source files touched — no genuine
regressions found, so no fixes were needed.

## Clean build

```
cd web && rm -rf .next out && npx tsc --noEmit && npx eslint . && npm run build
```

- `npx tsc --noEmit` — clean, zero errors.
- `npx eslint .` — clean, zero errors/warnings.
- `npm run build` — succeeded (Next.js 16.2.4, Turbopack). Prebuild copied 91 reports into
  `public/data/reports/`. Postbuild ran Pagefind successfully (214 HTML files indexed,
  6393 words).

**Route/page count:** 219 static pages generated total.
- Static routes (19): `/`, `/_not-found`, `/about`, `/archive`, `/case-study`,
  `/glossary`, `/icon`, `/methodology`, `/robots.txt`, `/rss.xml`, `/search`,
  `/sitemap.xml`, `/sources`, `/taxonomy`, `/timeline`, plus the dynamic route groups
  below and Next-internal entries.
- `/reports/[date]` (SSG): 91 report pages.
- `/signals/[slug]` (SSG): 111 signal pages (108 + the 3 examples shown in build output).
- Total matches Pagefind's "Indexed 214 pages" (214 crawlable HTML pages; 219 counts a
  couple of non-page build artifacts like `_not-found`/`icon`).

## Verification against built output (`web/out`), all via direct grep of built HTML — not source inspection

1. **Signal-anchor permalinks** — confirmed in `reports/2026-05-07.html`: `id="signal-sheer-layering"` divs plus matching `href="#signal-sheer-layering"` permalink anchors with `aria-label="Permalink to signal: Sheer layering"`. PASS.
2. **Dark-mode CSS** — `_next/static/chunks/0jfru77twtdfc.css` contains a `prefers-color-scheme:dark` block. PASS.
3. **Skip link** — `index.html` contains `<a href="#main-content" class="skip-link">Skip to main content</a>`. PASS.
4. **OG meta tags** — `index.html` has `og:title`, `og:description`, `og:url`, `og:type`. PASS.
5. **RSS feed** — `rss.xml` has exactly one `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" .../>` and exactly 50 `<item>` elements (MAX_FEED_ITEMS cap holding against a 91-report archive). PASS.
6. **Corrections banner** — both `reports/2027-03-01.html` and `reports/2027-03-08.html` contain "Correction"/"Corrections"/"Corrected" text. PASS.
7. **Signal titles as real headings** — confirmed via RSC payload grep in `reports/2026-05-07.html`: the signal title renders inside an actual `<h3>` element (`"$","h3",null,{...,"children":[...,"Sheer layering"]}`), not a styled `<div>`/`<p>`. Matches the file map's noted history of this exact bug class (styled-`<p>`-as-heading) — confirmed NOT recurring here. PASS.
8. **Signal recency line** — `signals/1990s-minimalism-revival.html` contains: "Last appeared 2026-07-06 — 90 published reports since, with no further occurrence on file." PASS.
9. **JSON-LD present/absent split** — `application/ld+json` occurs exactly once in `reports/2026-05-07.html` (present, as designed) and zero times in `signals/1990s-minimalism-revival.html` (absent, as designed). PASS.
10. **Sources/Taxonomy real content** — `sources.html` (65KB) contains sector labels (Editorial/Retail/Independent/etc.); `taxonomy.html` (70KB) contains Confidence/Volatility/Origin taxonomy vocab. Both are substantive pages, not stubs. PASS.
11. **Archive year-grouping headers** — `archive.html` contains `<h2>` year headers for 2026, 2027, 2028 (real `<h2>` elements, not styled divs). PASS.
12. **Timeline page** — `timeline.html` builds and is substantial (426KB), reverse-chronological content present. PASS.

All 12 checks passed with no regressions found. No web source files were modified.

## Process hygiene

```
wmic process where "name='node.exe'" get ProcessId,CommandLine
wmic process where "name='python.exe'" get ProcessId,CommandLine
```

Both returned "No Instance(s) Available." — no stray/orphaned `node.exe` or `python.exe`
processes at the time of this check (build process had already exited by the time this
was run). Nothing to clean up.

## Secret safety

No `.env` file contents, API keys, or credentials were printed, logged, or otherwise
exposed during this run.
