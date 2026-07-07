# /timeline page audit (run 94)

## Scope
First dedicated look at `web/app/timeline/page.tsx` and its data source
`getTimelineEntries()` in `web/lib/reports.ts`, prompted by run 93's nav/build
sweep noting the route builds but had never been individually audited.

## What it does
`/timeline` is a plain reverse-chronological list of every individual
**signal** across the archive, grouped by report date (design rationale in
`docs/agent-logs/signals-timeline-design.md`, built run 3). Each row shows
signal name (linked to `/signals/[slug]` when a `signal_id` exists, plain
text otherwise), `type`, and `confidence`. The date heading links to
`/reports/[date]`. No ranking, no trend graph — wire-service register,
consistent with project voice rules.

## Freshness / accuracy check
- `getTimelineEntries()` reads `getAllReports()`, which globs every file in
  `data/reports/*.json` at build time — there is no hardcoded date list or
  count. Verified against the live archive: 86 report files on disk, build
  output confirms 86 reports copied into `public/data/reports/` and the page
  renders correctly off that full set. No staleness bug of the kind found in
  methodology/sources/taxonomy in prior runs.
- Cross-checked every `top_signals[]` entry across all 86 report JSON files
  (155 signals total) for missing `type`/`confidence` — zero missing. The
  fields this page renders are fully populated and match the underlying data.
- Found one **stale doc comment** (not a functional bug): the JSDoc above
  `getTimelineEntries()` in `web/lib/reports.ts` said "there is no
  signal_id/slug field yet, so no cross-report identity matching is
  attempted" — but `signal_id` has existed in the schema and been used by
  this exact function (and rendered as a link in `timeline/page.tsx`) since
  at least run 4's `/signals/[slug]` ship. The comment predated that addition
  and was never updated. Fixed: rewrote the comment to reflect that
  `signal_id` is included and used for linking when present, and entries
  without one render as plain text. No behavior change — the code was
  already correct, only the comment was wrong.

## Redundancy vs. /archive
Genuinely distinct, not redundant:
- `/archive` is **report-level**: one row per report, showing only that
  report's top-ranked signal plus source count. It's the historical record
  of report issuance.
- `/timeline` is **signal-level**: every signal in every report, so a single
  report date can expand into several rows. It's the closest thing to a
  full signal-chronology view distinct from `/signals/[slug]`'s
  per-signal-across-time view.
- The two pages already cross-link each other in their footers, and
  `/archive`'s "Recurring across the archive" module points to
  `/signals/[slug]`, not `/timeline` — the site's own information
  architecture treats these as three different altitudes (report record /
  full signal chronology / single-signal history), which still holds up.

No scope-drift flag needed here — purpose is intact and not neglected in
practice, just under-visited by prior audits (as run 93 noted).

## Fix made
- `web/lib/reports.ts`: corrected the outdated JSDoc comment on
  `getTimelineEntries()` (see above). No schema, data, or rendering changes.

## Validation
```
cd web && npx tsc --noEmit && npx eslint . && npm run build
```
All three passed clean. Build generated all 207 routes including
`/timeline`, copied 86 reports, and Pagefind indexing completed without
error.

## Files touched
- `web/lib/reports.ts` (comment-only fix)
- `docs/agent-logs/timeline-page-audit-run94.md` (this file)

No other files touched. TODO.md/CHANGELOG.md/data/reports left untouched per
instructions.
