# Thin-week pattern surfacing

Addresses health-check-run12's recommendation (c): surface repeated thin
reporting windows explicitly instead of letting each report restate "quiet
period" as if newly observed.

## Changes

- `web/lib/reports.ts`: added `getConsecutiveThinWeekCount()`. Reads
  `getAllReports()` (already newest-first) and counts from the top how many
  consecutive reports have `collection_status === "thin"`, stopping at the
  first non-thin report. Cast to an inline type since `collection_status`
  isn't yet on the `Report` interface (matches existing schema field per
  report_schema.py; not added to the TS interface to keep this change
  scoped to the two named files).
- `web/app/archive/page.tsx`: calls the new helper; when the streak is >= 2,
  renders a plain factual note under the masthead stat line, above the
  report list. Wording: "The archive's N most recent reporting windows were
  classified thin, reflecting limited genuine signal volume rather than a
  change in collection method." Styled to match the existing gray/franklin
  meta-text with a hairline top border, consistent with the page's existing
  Corrections/methodology tone — no alarm, no apology.

## Scope

Only touched `web/lib/reports.ts` and `web/app/archive/page.tsx`, per
instructions. Did not touch `data/reports/2026-07-20.json` (flagged as
concurrently edited) or any other page.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 41
routes generated successfully.

## Not committed

Per instructions, no commit was made.
