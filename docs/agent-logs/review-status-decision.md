# review_status / reviewed_by: render, don't suppress

Checked actual data: `grep -rn "review_status\|reviewed_by" data/reports/*.json`
shows both fields populated with real, varying values across all 15 reports
that carry them — `reviewed_by` is never the schema default `""`. Values
include `"loop-consolidation"` (routine loop runs), `"websearch-run-thin-week"`
(thin-week manual passes), `"hand-authored-example-run1"` /
`"hand-authored-placeholder-run0"` (early hand-built reports), and
`"websearch-run-plus-manual-sample-worldcup-jersey"` (a specific manual
sampling run). `review_status` is always `"reviewed"` in the data (no
`"draft"` reports exist yet), but `reviewed_by` alone is genuine, differentiated
provenance data, not inert bookkeeping — so this does not qualify for
`KNOWN_BACKEND_ONLY_FIELDS` (that set is for fields confirmed to carry no
distinguishable editorial content, e.g. `content_hash`/`confidence_source`).

## What was done

- `web/lib/reports.ts`: added `review_status?: string` and
  `reviewed_by?: string` to the `Report` interface.
- `web/app/reports/[date]/page.tsx`: rendered both inside the existing
  "Notes" `<section>` (real `<h2>` heading, same pattern as
  confidence/volatility/incentive notes) as a "Review:" line — `"Draft, "` or
  `"Reviewed, "` prefix from `review_status`, followed by `reviewed_by`. Only
  renders when `reviewed_by` is present, so old/placeholder reports without
  the field don't show an empty line. Extended the section's existing
  truthy-guard to include `report.reviewed_by`.

## Verification

- `python -m py_compile src/*.py` — passes (no backend files changed besides
  reading them).
- `cd web && npx tsc --noEmit` — clean.
- `cd web && npx next build` — succeeds, all 18 `/reports/[date]` pages
  prerender.
- Manually confirmed the new line uses a real `<h2>` section heading already
  in place (not a styled-`<p>`), per the SKILL.md checklist item on the
  recurring fake-heading bug.
