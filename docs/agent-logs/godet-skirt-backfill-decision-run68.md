# Run 68: godet skirt historical backfill decision

**Follow-up to run 67**, which found "godet skirt" duplicated verbatim across
`garments` and `silhouettes` in `data/reports/2026-07-20.json` and fixed the
extraction prompt going forward but left the historical entry untouched.

## Decision: fix it

`garments`/`silhouettes` are controlled-vocabulary taxonomy fields (typed enums'
sibling list fields), not free-text editorial prose making a substantive claim
about the world. The project's own validator and coverage tools (`validate_all_reports.py`,
`check_field_coverage.py`) treat these fields as structured data to be internally
consistent, not as a historical narrative that must be preserved verbatim the way
`human_editor_note`/`evidence` text is. A duplicate term across two fields defined
to be disjoint is a data-entry defect, not an editorial judgment call worth
preserving for provenance — unlike the EDITORIAL CLOSE-OUT notes (see SKILL.md
item 10), there's no legitimate reading under which both fields are simultaneously
correct here.

## Context reviewed

- `garments`: `['shirt', 'handkerchief-hem skirt', 'godet skirt', 'belt', 'soccer jersey', 'layered top']`
- `silhouettes`: `['asymmetric hem', 'godet skirt', 'relaxed suiting']`
- The signal's own evidence text ("Uneven and handkerchief-hem silhouettes") describes
  "godet-style uneven hemlines" as a shape descriptor, but "godet skirt" the term names
  a specific wearable garment (a skirt cut with godet inserts) — same category as the
  already-listed "handkerchief-hem skirt". Its shape contribution to the report is
  already captured by the existing "asymmetric hem" silhouette entry.

## Fix applied

Kept "godet skirt" in `garments` (correct field per the run-67 prompt guidance's
garment=wearable-item definition), removed it from `silhouettes` via
`save_report(revision_reason=..., corrected_at='2026-07-06')`. New `revision_history`
entry recorded in the report itself explaining the change.

## Verification

- `python -m py_compile src/*.py` — clean.
- `python src/validate_all_reports.py` — all 60 reports pass schema validation; one
  pre-existing, unrelated confidence WARNING on `2027-05-17.json` (Dior Cruise LACMA
  signal), not touched by this change.

No web files touched.
