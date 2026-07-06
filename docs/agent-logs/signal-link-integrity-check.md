# Signal link integrity check (verification pass)

**Result: no issues found. Everything checks out.**

## What was checked

1. **Link/param coverage.** `reports/[date]/page.tsx` only links to `/signals/[id]` from
   `report.top_signals[].signal_id` (line ~215). Both `getAllSignalSlugs()` and
   `getSignalHistory()` in `web/lib/reports.ts` iterate the exact same `top_signals` field
   across `getAllReports()`, so they're structurally guaranteed to agree — but verified
   with actual data rather than trusting that: a Node script scanned all 19 files in
   `data/reports/*.json` (read-only) and found 37 distinct non-empty `signal_id` values,
   no whitespace/casing anomalies. `npx next build` then generated exactly 37 static
   `/signals/[slug]` pages (confirmed in build output: `cfda-vogue-fashion-fund-2026-winner`,
   `lfw-eligibility-wholesale-requirement-dropped`, `pfw-ss27-schedule-date-inconsistency`,
   `+34 more`) — matching the scan count 1:1. No dangling links, no missing params.

2. **Full-history spot check.** 11 signal_ids recur across 2-3 reports (e.g.
   `sheer-layering`: 2026-05-07, 2026-07-06, 2026-08-03; `lfw-eligibility-wholesale-
   requirement-dropped`: 2026-09-21, 2026-10-12, 2026-10-19). Read `getSignalHistory()`
   (web/lib/reports.ts:149) — it pushes every matching occurrence across every report, no
   `.slice`/dedup/latest-only logic, sorted oldest-first. Confirmed against the actual
   built output: inspected `.next/server/app/signals/sheer-layering.html` and all three
   dates (2026-05-07, 2026-07-06, 2026-08-03) render, not just the most recent.

## Verification commands run

- Node script over `data/reports/*.json` (read-only, no edits) counting signal_ids and
  occurrences per id.
- `cd web && npx tsc --noEmit` — clean.
- `cd web && npx next build` — succeeded, 72 pages, 37 signal pages as expected.

No code changes were made; `data/reports/` was not touched.
