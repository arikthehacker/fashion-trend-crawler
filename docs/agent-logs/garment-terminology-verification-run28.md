# Garment terminology fix verification (run 28)

## Method

Checked all reports 2026-09-28 through 2026-11-09 (post run-20 prompt fix) for signal_ids
carried across multiple reports, comparing their `garments`/`materials` fields for drift.

## Finding: fix untested, not falsified

`mfw-ss27-schedule-date-inconsistency` / `versace-mulier-debut-timing-unconfirmed` /
`armani-post-founder-transition-continues` (09-28 -> 10-05), `lfw-eligibility-wholesale-
requirement-dropped` (09-21, 10-12, 10-19), and `cfda-vogue-fashion-fund-2026-winner`
(10-26 -> 11-09) all continue across reports, but every one of these reports has an empty
`garments: []` and `materials: []` — the post-run-20 window has been dominated by
scheduling/governance/personnel signals (fashion-week calendar mechanics, designer
transitions, awards), not garment-description signals. So the run-20 prompt instruction
has had **no real garment-terminology case to exercise** since it shipped — no drift
observed, but also no positive proof it works. Not a regression; just an untested
instruction. No further prompt change made.

## `peplum-waist-revival`: original drift was never corrected

Confirmed the drift from `costume-core-research.md` (run 19): `garments` read
`["peplum skirt", "peplum trouser", ...]` on 2026-08-10 and `["peplum skirt", ...]` on
2026-08-17, then silently became `["peplum jacket", ...]` on 2026-08-24 (the close-out
report) with no note. This predates the run-20 prompt fix and was left as a documented
finding, never actually repaired.

**Fixed now** via `report_schema.save_report()`: restored `2026-08-24.json`'s `garments`
to `["peplum skirt", "peplum trouser", "structured blazer"]` (append-only, per the
recommended practice) and appended a `human_editor_note` sentence plus a
`revision_history` entry (`revision_reason`, `corrected_at: "2026-11-09"`) explaining the
historical inconsistency and correction — not rewriting the report's substantive
conclusions, only the drifted term list and a note.

## Verification

- `python -m py_compile src/*.py` — passed.
- `python src/validate_all_reports.py` — `OK: all 21 report(s) ... passed schema
  validation.`

## Files touched

- `data/reports/2026-08-24.json` (garments field, human_editor_note, revision_history,
  content_hash — via save_report, not hand-edited)
