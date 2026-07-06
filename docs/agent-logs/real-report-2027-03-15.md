# Real report: 2027-03-15 (38th weekly window)

Created `data/reports/2027-03-15.json`, collection window Mar 9 - Mar 15, 2027.

## New signal: Fall/Winter 2027-28 women's ready-to-wear fashion month

WebSearch found this archive has never logged the Feb-March women's
ready-to-wear fashion month -- `docs/EDITORIAL_CALENDAR.md` documents the
Sept-Oct fashion month and the Jan menswear/couture cluster but has no entry
for this one. Real coverage confirms NY/London/Milan/Paris ready-to-wear
shows ran through this window, Paris concluding March 10 (FHCM calendar).
Added two new signals: `fw27-28-rtw-fashion-month` (medium confidence,
editorial + designer-origin corroboration -- Dior/Anderson, Chloe/Kamali,
Loewe/Schiaparelli bio-textile pieces) and
`messy-chic-power-shoulder-tailoring` (low confidence, editorial-only,
single-window aesthetic-trend framing not yet corroborated outside
editorial). Flagged the calendar gap in the signal's `index_note` rather
than editing `docs/EDITORIAL_CALENDAR.md` directly, since that's a doc
change out of this task's scope.

## Wales Bonner/Hermes: not re-litigated

Per the 2027-03-08 transition and SKILL.md note 10, did not re-open this as
a top signal. A brief check found no new coverage, consistent with staying
untracked.

## Haute Couture SS27: checked again, still no post-show coverage

Same absence-of-coverage pattern as the prior six windows. Kept under
normal tracking (same `paris-post-show-coverage-gap` reasoning as before,
not re-added as a top signal this window since nothing changed -- referenced
in `limitations` instead).

## CFDA questions

Remain untracked per convention, not re-litigated.

## Verification

- Checked existing `signal_id`s across all reports before naming new ones --
  no collisions.
- `python -m py_compile src/*.py` -- passed.
- `python src/validate_all_reports.py` -- `OK: all 38 report(s)... passed
  schema validation.`
- Saved via `report_schema.save_report()`.
- Scratch script (`build_report_20270315.py`) deleted after use.

Not committed, per instructions.
