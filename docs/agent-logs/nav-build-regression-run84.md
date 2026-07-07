# Run 84 — full regression sweep (clean wipe)

Branch: `ari3lla-index-loop-improvements`. Followed the clean-wipe practice established
since run 72.

## 1. Stray processes
`wmic process where "name='node.exe'"` and `"name='python.exe'"` both returned
"No Instance(s) Available." — nothing to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` from `web/` — **clean, zero output.**

## 3. Lint
`npx eslint .` — **clean, zero output.**

## 4. Build
`npm run build` — **succeeded, zero warnings.**
- `copy-reports.mjs` copied 76 reports into `public/data/reports/` (prebuild + next.config.ts hook both ran).
- 187 total routes generated (Turbopack, Next 16.2.4): 76 `/reports/[date]` pages, 94 `/signals/[slug]` pages, plus the fixed top-level routes (home, about, archive, case-study, glossary, methodology, search, sources, taxonomy, timeline, icon, robots.txt, rss.xml, sitemap.xml, _not-found).
- Pagefind postbuild indexed 182 HTML pages / 6049 words, 0 errors.

## 5. Built-output verification (grepped `web/out` directly)
All prior fixes confirmed intact:
- Signal-anchor deep-linking: `id="signal-<signal_id>"` present per signal block in report pages (e.g. `id="signal-sheer-layering"`) — confirmed run-63 pattern.
- Dark mode (OS-preference `prefers-color-scheme`) present in compiled CSS chunk.
- Skip-link: `#main-content` present in `index.html`.
- Open Graph tags: `og:description`, `og:site`, `og:title`, `og:type`, `og:url` all present.
- RSS: `atom:link rel="self"` present, exactly 50 `<item>` elements.
- Corrections banner: `correction` content found across 36 report pages (includes the `#correction-history` anchor link on pages with revision history).
- Signal titles: 75 report pages contain real `<h3>` elements for signal titles.
- `/signals/[slug]` recency line: confirmed real rendered text, e.g. "Last appeared 2027-01-04 — 48 published reports since, with no further occurrence on file."
- JSON-LD: `application/ld+json` present on report pages (1 block, `reports/2026-07-06.html`).
- Sources (`sources.html`, 65KB) and Taxonomy (`taxonomy.html`, 71KB) pages both render substantial real content, not stubs.
- Run-83 archive year-grouping: `archive.html` contains distinct `<h2>` year headers (2027, 2026) grouping entries correctly.

## 6. Report-page count vs. data
`data/reports/*.json` = **76 files**. Built `/reports/[date]` static pages = **76** (matches build output route list exactly).

## 7. Concurrent work note
No signs of other agents' in-progress changes surfacing as build issues at the time of
this sweep — working tree was clean before the wipe, and no anomalous/half-finished
content was found in the built output (no stray `changed_signals` artifacts, no
archive-page inconsistency). If another agent's `save_report()` confidence correction or
archive audit lands mid-sweep in a shared tree, treat any new diff after this point as
their concurrent WIP, not a regression from this run.

## Verdict
**No regression found.** All checks pass: tsc clean, eslint clean, build clean (187
routes, 0 warnings), all spot-checked built-output features intact, report count matches
exactly (76 = 76). No code changes made.
