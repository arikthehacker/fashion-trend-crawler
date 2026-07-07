# Homepage rewrite — trends.ts retired (approved 2026-08-10, run 13)

User approved the run-11 proposal (`trends-ts-fate-proposal.md`) mid-run-13: "the homepage
can be changed it's ok."

## What changed

- `web/app/page.tsx`: replaced `getTrends()` (from `web/lib/trends.ts`) with
  `getLatestReport()` (new, in `web/lib/reports.ts`). The masthead/hero keeps its exact
  visual styling; the "Observed Signals"/trend-cards/"Source Notes"/"Collected Items"
  sections (built from the one-off live-crawl snapshot) were replaced with a single
  "Latest Report" teaser section: executive summary, top 5 signal cards (name + evidence),
  and a link to the full `/reports/[date]` page.
- `web/lib/reports.ts`: added `getLatestReport()` (`getAllReports()[0]`, since that list is
  already sorted newest-first).
- Deleted `web/lib/trends.ts`.
- Deleted the 4 legacy cache files: `trends_raw.json`, `trends_summary.json` (root), and
  their `src/` copies. **This completes migration step 5/5** — the legacy-migration plan
  from run 5 is now fully closed.

## Verification

- `python -m py_compile src/*.py` — clean.
- `python src/validate_all_reports.py` — 7/7 reports valid.
- `cd web && npx tsc --noEmit && npx next build` — clean, all routes build, homepage now
  renders the 2026-08-10 report's executive summary and top signals.
- Grepped `src/` for `trends_raw.json`/`trends_summary.json` — only the `DEFAULT_OUTPUT_FILE`
  constant definition and code comments remain; no live file reads.

## Not done

`crawler.py`/`summarize.py` still default to writing/reading `trends_raw.json` as their
intermediate cache during a live crawl run (that's the crawler's own working file, not a
frontend dependency) — this is fine and expected; it's regenerated each pipeline run and
was never the issue. Only the frontend's dependency on a *stale, committed copy* of that
file was the actual bug, and that's now resolved.
