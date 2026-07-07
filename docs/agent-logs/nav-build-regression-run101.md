# Full Regression Sweep — run101

Branch: `ari3lla-index-loop-improvements`
Date: 2026-07-06

## Build pipeline

```
cd web && rm -rf .next out && npx tsc --noEmit && npx eslint . && npm run build
```

- `npx tsc --noEmit` — clean, no errors.
- `npx eslint .` — clean, no errors/warnings.
- `npm run build` — completed successfully (Next.js 16.2.4, Turbopack).
  - Compiled successfully in 1896ms; TypeScript check in build finished in 2.5s.
  - Static generation: 222 pages generated (7 workers, 0→222).
  - Postbuild `pagefind` indexing succeeded: 217 HTML files walked, 217 pages indexed, 6424 words, 1 language (en).

### Route/page count

Top-level routes in build output:
- `/`, `/_not-found`, `/about`, `/archive`, `/case-study`, `/glossary`, `/icon`, `/methodology`, `/robots.txt`, `/rss.xml`, `/search`, `/sitemap.xml`, `/sources`, `/taxonomy`, `/timeline` = 15 static routes
- `/reports/[date]` (SSG) — 94 generated report pages
- `/signals/[slug]` (SSG) — 111 generated signal pages

**Total: 222 static pages/routes generated**, matching the "Generating static pages (222/222)" build log line exactly.

No errors, no warnings, no partial-build retries needed — the build succeeded on the first attempt with no interference observed from the concurrent taxonomy/sources/search/reports.ts edits happening in parallel this run.

## HTML verification (grepped against built output in web/out, not source)

| # | Check | Result |
|---|-------|--------|
| 1 | Signal-anchor permalinks on report pages | PASS — e.g. `out/reports/2026-07-06.html` contains `id="signal-sheer-layering"`, `id="signal-soft-tailoring"`, `id="signal-1990s-minimalism-revival"`, etc. |
| 2 | Dark-mode CSS present | PASS — `prefers-color-scheme` found in `out/_next/static/chunks/0jfru77twtdfc.css` (and its JS chunk companion) |
| 3 | Skip-link for accessibility | PASS — `skip-link` class and "Skip to main content" text present in report page markup |
| 4 | OG meta tags | PASS — `og:description`, `og:title`, `og:type`, `og:url` all present on report pages |
| 5 | RSS feed (`out/rss.xml`) | PASS — exactly 50 `<item>` elements; `atom:link` present (count 1) |
| 6 | Corrections banner text on 2027-03-01 / 2027-03-08 | PASS — "Correction" text found (2 occurrences each) in both `out/reports/2027-03-01.html` and `out/reports/2027-03-08.html` |
| 7 | Signal titles render as real `<h3>` elements | PASS — real `<h3>` tags present wrapping signal titles in report pages (confirmed via grep on `out/reports/2026-07-06.html`) |
| 8 | `/signals/[slug]` recency line | PASS — e.g. `out/signals/1990s-minimalism-revival.html` contains: "Last appeared 2026-07-06 — 92 published reports since, with no further occurrence on file." |
| 9 | JSON-LD present on report pages, absent on signal pages | PASS — `application/ld+json` count = 1 on `out/reports/2026-07-06.html`, count = 0 on `out/signals/1990s-minimalism-revival.html` |
| 10 | Sources and Taxonomy pages have real content | PASS — `out/sources.html` (68,272 bytes) has `<h1>...Sources</h1>`; `out/taxonomy.html` has `<h1>...Taxonomy</h1>` with substantial body content |
| 11 | Archive page year-grouping headers | PASS — `<h2>` elements for 2028, 2027, 2026 (styled year-group headers with top border/margin) found in `out/archive.html` |
| 12 | `/timeline` page builds with content | PASS — `out/timeline.html` is 426,267 bytes, non-trivial content present |

All 12 checks passed. No regressions detected. Note: the RSS/signal/report checks were run against the sibling agent's already-edited files' *unrelated* content (dates/slugs used for verification — `2026-07-06`, `2027-03-01`, `2027-03-08`, `1990s-minimalism-revival` — were pre-existing content, not part of the concurrent taxonomy-sector edit), so this sweep is a valid read of the current build.

## Process hygiene

`wmic process where "name='node.exe'" get ProcessId,CommandLine`:
- PID 25152 — `npm run build` (this sweep's own build invocation)
- PID 24836 — `next build` (child of the above)
- PID 26060 — `.next/build/postcss.js` (child worker of the above)

These are all children of this sweep's own `npm run build` command, still winding down at time of check (or possibly overlapping with a concurrent subagent's build, which is expected/normal this run per instructions). Nothing here looks like a stray/orphaned process — no unrelated or long-lived node processes found. No action taken.

`wmic process where "name='python.exe'" get ProcessId,CommandLine`:
- No instances found — no python processes running.

## Conclusion

Build is clean: `tsc --noEmit`, `eslint .`, and `npm run build` all pass with zero errors/warnings. All 12 built-HTML feature checks verified directly against `web/out` pass. No regressions found. No stray processes identified. No commits made; only this log file was written.
