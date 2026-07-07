# Performance check — run 50

**Scope:** re-verify `web/lib/reports.ts` data-layer health at 42 reports (~2x the 23
reports present at run 31's check), and check whether any feature shipped since (recurring
signals, download route, glossary term-filter, homepage index module) introduced a new
redundant full-archive read.

## Build numbers

`cd web && npx tsc --noEmit` — clean, no errors.

`npm run build` (Next.js + Pagefind postbuild): **~11.8s real** total, of which Pagefind
indexing (106 HTML files, 4202 words) is ~2.6s — so `next build` itself is ~9s, generating
**106 static pages** from 42 reports (vs. run 31's 9.1s / 80 pages from 23 reports). Page
count roughly scaled with report count (~1.3x pages per report, consistent with more
signals per report over time), build time did not increase meaningfully — confirms run 31's
prediction that page count, not `getAllReports()` cost, dominates build time.

`out/` total size: **19MB**. Largest individual files: `timeline.html` (243KB),
`search.html` (228KB, expected — client-side facet filter payload), a Next chunk (227KB),
favicon (196KB, duplicated once under `_next/static/media` — normal Next.js behavior, not a
bug). Nothing unexpectedly large; no single report/asset is out of line.

## Redundant-read check — found and fixed one

`getAllReports()`'s module-level cache (run 31) is intact and still the shared path for
every helper in `lib/reports.ts` (`getLatestReport`, `getThisWeeksIndex`,
`getConsecutiveThinWeekCount`, `getRecurringSignals`, `getSearchIndex`,
`getTimelineEntries`, `getSignalHistory`, `getAllSignalSlugs`). Homepage, archive, sitemap,
and `reports/[date]` all go through it or through `getReportByDate`/`getAllReportDates`
(intentionally uncached — single-file/filename-only reads, not full-archive parses).

`app/glossary/page.tsx` (shipped run 20) was the one exception: it did its **own**
independent `fs.readdirSync` + `JSON.parse` of every file in `data/reports/`, completely
bypassing `lib/reports.ts` and its cache — the exact redundant-full-archive-read pattern run
31 fixed elsewhere, reintroduced in a new file that predates/parallels that fix. Every
`/glossary` build was doing a 43rd full-archive read on top of the ~7 already covered by the
shared cache.

**Fix applied:** `loadGlossaryTerms()` now calls the shared `getAllReports()` instead of its
own `fs`/`path` read; removed the now-unused `fs`/`path` imports. No behavior change —
verified with `npx tsc --noEmit` (clean) and a full `npm run build` (glossary page still
renders, same page count/output).

## Verdict

Healthy at 42 reports / 106 pages. One genuine new instance of run 31's bug pattern found in
`glossary/page.tsx` and fixed. `copy-reports.mjs` (build script, not a page) has its own
`readdirSync` too but runs once per build regardless, so it's not part of this pattern.
