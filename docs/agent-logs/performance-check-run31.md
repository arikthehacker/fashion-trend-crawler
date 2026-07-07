# Performance check — run 31

**Scope:** `web/lib/reports.ts` data layer, ahead of continued archive growth (23 reports,
78-80 static pages today).

## Findings

`getAllReports()` does a full `fs.readdirSync` + `JSON.parse` of every report file, and
nearly every other exported helper (`getLatestReport`, `getTimelineEntries`,
`getSignalHistory`, `getSearchIndex`, `getConsecutiveThinWeekCount`, `getThisWeeksIndex`,
`getAllSignalSlugs`) calls it internally with no caching. Confirmed real redundancy within
single page renders:

- Homepage (`app/page.tsx`): calls `getLatestReport()` and `getThisWeeksIndex()` —
  2 full re-reads of the archive per render.
- Archive page (`app/archive/page.tsx`): calls `getAllReports()`,
  `getConsecutiveThinWeekCount()`, and `getThisWeeksIndex()` — 3 full re-reads per render.

At 23 reports this is cheap (files are small JSON), but it's O(pages × helpers-per-page ×
report-count) work that scales linearly with archive size for no reason — every one of
those calls re-reads identical bytes from disk within the same build.

## Fix applied

Added a simple module-level cache (`allReportsCache`) inside `getAllReports()` in
`web/lib/reports.ts`. Report files are static build-time input for a Next.js static export
(not a long-running server watching for file writes), so caching for the process lifetime
is safe and doesn't change behavior — every helper still returns the same data, just from
one disk read instead of N. No call sites changed.

## Build timing

`cd web && npx tsc --noEmit && npx next build` — both pass clean.

- TypeScript: compiles clean, ~2.7s for the build's own type pass.
- `next build` (Turbopack): **9.143s real** wall-clock for 80 static pages generated
  from 23 reports.

## Verdict

Not currently a real performance problem — 9s for 80 pages is fast, and the redundant
reads were reading small JSON files already cached by the OS filesystem cache within a
single build process. The fix is a genuine no-behavior-change simplification (eliminates
actual repeated work), not premature optimization, so it was applied. Extrapolating
linearly to 100+ reports: file I/O volume would grow ~4x but should still be sub-second
per read; page count would grow proportionally with signal/report count, so total build
time is more likely to be dominated by the number of generated pages than by
`getAllReports()` cost. Worth re-measuring once the archive crosses ~100 reports, but no
architectural change is warranted now.
