# Archive year-grouping regression check (run 84)

Cross-check of run 83's year-grouping headers added to `web/app/archive/page.tsx`
(commit `1990e91 feat(ux): add year-grouping headers to the archive listing`).

## What was checked

1. **Implementation review.** `git log` confirms the commit touched only
   `web/app/archive/page.tsx` — `web/lib/reports.ts` (the shared data layer) is
   untouched. The grouping logic (lines 138-159) maps over the *same*
   `reports` array `getAllReports()` already returns, in the same order. Each
   iteration derives `year`/`prevYear` from `report_date.slice(0, 4)` and
   inserts an `<h2>` header only when the year changes (`isNewYear`). It does
   not filter, re-sort, re-key, or slice the array — the `<Link>` row for
   every report is rendered unconditionally inside the same `.map()`, with
   the optional header as a sibling before it. This shape structurally
   cannot drop or duplicate a report; a header is purely additive markup.

2. **Report coverage.** `data/reports/*.json` has 76 files. Built
   `out/archive.html` contains exactly 76 `/reports/<date>` links, all
   unique (verified via regex extraction + `Set` dedup). No report dropped
   or duplicated.

3. **Year-boundary correctness.** The archive spans two years (earliest
   2026-05-07, latest 2027-12-13). Built output has exactly two `<h2>` year
   headers: `2027` then `2026`, matching the two distinct years present — no
   report misfiled under the wrong year. (String comparison on
   `YYYY-MM-DD`-formatted `report_date` is lexicographically safe across
   year/month/day boundaries, so no Jan/Dec edge-case risk exists here.)

4. **Overall ordering.** Extracted the 76 report-link dates in DOM order and
   confirmed strictly non-increasing (newest-first) across the whole list,
   including across the year-header boundary — grouping did not reorder
   anything within or between year groups.

5. **Downstream sharing.** `getAllReports()`/`lib/reports.ts` is shared by
   `archive/page.tsx`, `glossary/page.tsx`, and `rss.xml/route.ts`, but since
   the data layer itself was not touched by run 83 (only the archive page's
   JSX), none of those consumers are affected. No sitemap/RSS regression
   possible from this change.

6. **Pagefind index.** Ran a full `npm run build` (which chains the
   `pagefind` postbuild). Pagefind indexed 182 pages including
   `out/archive.html` with no errors.

## Validation run

- `cd web && npx tsc --noEmit` — clean, exit 0.
- `npx eslint .` — clean, no findings.
- `npm run build` — succeeded; static export + Pagefind index built with no
  errors.

## Result

**Clean.** No regression found. The year-grouping change is additive-only
markup over the existing, unmodified sort/data logic; report coverage,
ordering, and year-boundary grouping are all correct in the built output.
No code changes were made.
