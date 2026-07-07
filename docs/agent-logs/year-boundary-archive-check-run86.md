# Year-boundary archive grouping check — run 86

## What was checked

`web/app/archive/page.tsx` (lines ~138-159) implements the year-grouping header
added in run 83:

```ts
const year = report.report_date.slice(0, 4);
const prevYear = i > 0 ? reports[i - 1].report_date.slice(0, 4) : null;
const isNewYear = year !== prevYear;
```

This groups purely by the first 4 characters of `report_date` (a `YYYY-MM-DD`
string) compared against the previous entry in the already-sorted `reports`
array. `getAllReports()` (`web/lib/reports.ts`) sorts by `report_date` as a
plain string descending (`a.report_date < b.report_date ? 1 : -1`), which is
correct for ISO `YYYY-MM-DD` dates including across a year boundary (lexical
order matches chronological order for that format).

**No hardcoded year literals, switch/if against specific "2026"/"2027"
strings, or two-year-only assumption exists anywhere in this logic.** It is a
general string-slice + Set-like adjacent-comparison approach that will produce
a correctly-labeled new header for any year value that appears in the data,
including 2028, 2029, etc., with zero code changes required.

## Verification performed

- Read the full grouping implementation and the sort/read logic in
  `web/lib/reports.ts` (`getAllReports`).
- Rebuilt the site clean (`rm -rf .next out && npm run build`) and inspected
  the built `web/out/archive.html`: found exactly one `2026` header and one
  `2027` header, each appearing once, confirming the existing boundary
  renders correctly.
- Ran `npx tsc --noEmit` and `npx eslint .` — both clean, no errors/warnings.
- Watched `data/reports/` for the concurrently-being-added first 2028 (or
  late-Dec-2027-dated New Year's week) report. As of this check, the newest
  file on disk was `2027-12-27.json`; the new report had **not yet landed**
  by the time this check needed to conclude. (Also discovered mid-task that a
  concurrent agent was running `next build` in the same `web/` directory at
  the same time — Next.js correctly refused a second concurrent build
  ("Another next build process is already running"); waited for it to finish
  rather than forcing a second build, since builds in this shared working
  tree are not safe to run in parallel.)

## Conclusion

No latent bug found. The year-grouping code is already general (string-slice
based, not hardcoded to specific year values), so a new 2028-dated report —
whichever exact `report_date` convention it lands with (2027-12-28 vs.
2028-01-03) — will automatically get its own correct year header the moment
it exists in `data/reports/`, with no code change needed. No fix was applied.

**Caveat:** the true end-to-end 2028 case (an actual `2028`-prefixed
`report_date` flowing through a real build) could not be directly observed
before this check concluded, because the concurrent report-writing agent's
file had not yet landed in `data/reports/`. Confidence in the "will work"
conclusion is high given the code reading (pure string-slice, no
year-specific branching, correct lexical sort for ISO dates), but it is
based on code review + the existing 2026/2027 boundary test rather than a
direct observation of the 2028 case itself.
