# Revision history display check

**Claim tested:** methodology page's Corrections section says corrections preserve original
content alongside the correction via `revision_history`.

**Finding:** `revision_history` is populated correctly by `save_report()` (confirmed via
`report_schema.py`) and 3 reports in `data/reports/` have real, non-empty entries:

- `2026-05-07.json` — 1 entry (backfill provenance metadata)
- `2026-07-20.json` — 2 entries (added social signal; off-duty-varsity close-out)
- `2026-08-03.json` — 1 entry (sheer-layering/soft-tailoring close-out)

But `web/app/reports/[date]/page.tsx` never read or rendered `revision_history` anywhere.
A reader viewing any of these three report pages had no way to see that a correction had
occurred, what was corrected, or why — same category of gap as run 21's `human_editor_note`
finding. The methodology page's claim was aspirational, not actually true of the rendered
site.

**Fix applied:**
- `web/lib/reports.ts`: added `RevisionEntry` interface and `revision_history?: RevisionEntry[]`
  to the `Report` type (was missing entirely, so the field wasn't even typed).
- `web/app/reports/[date]/page.tsx`: added a "Correction History" section (placed before
  Archive Tags, after Limitations) that lists each revision's `corrected_at` date and
  `reason` in a `<ul>`, styled consistently with the existing Limitations section. Uses a
  real `<h2>` heading (via the shared `labelStyle`), not a styled `<p>`. Only renders when
  `revision_history` has entries, so untouched reports show nothing new.

Does not show old vs. new content diffs (not stored anywhere — only `previous_content_hash`,
a hash, is retained, not the prior text) — just transparency that a correction occurred,
when, and why, which is what the schema actually supports.

**Verification:** `cd web && npx tsc --noEmit && npx next build` — both pass clean, all
67 pages including `/reports/2026-05-07`, `/reports/2026-07-20`, `/reports/2026-08-03`
build successfully. Manually reviewed the new JSX for the styled-`<p>`-as-heading bug per
the SKILL.md checklist item — the section heading is the existing `<h2 style={labelStyle}>`
pattern used everywhere else on the page, not a `<p>`.

**Not committed** per instructions.
