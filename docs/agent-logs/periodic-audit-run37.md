# Periodic confidence + dormancy audit — run 37

Ran `validate_all_reports.py` (29 reports, all pass), `audit_confidence.py`
(73 signals, 43 mismatches), and `check_field_coverage.py` fresh (0 warnings,
matches run 25/32 baseline).

## Confidence audit

All 43 mismatches are still assigned-lower-than-derived (editor
conservatism) — no `assigned=high, derived=low/medium` case anywhere,
including runs 33-36's additions (2026-12-14 through 2027-01-11): the new
CFDA Fashion Fund/Awards carry-forward windows and the new Golden Globes
red-carpet signal are all held conservatively below the formula, same
pattern as every prior run. None concerning.

## Dormancy check

Computed `get_signal_status_history()` for every signal_id appearing in 2+
reports (12 total). Two came back quiet 18 windows with no close-out
(`nyfw-ss27-schedule-finalization`, `school-y2k-preppy`) but both are
already resolved by explicit prose in `2026-09-14.json`'s `limitations`
(the CFDA/style-signal convention this project uses instead of a schema
field) — not a gap.

## Genuine issue found and fixed

Run 32's retroactive close-out for `versace-mulier-debut-unconfirmed` and
`armani-founder-transition` (in `2026-12-07.json`) referenced them by
stale, pre-run-36 long-form slugs (`versace-mulier-debut-timing-unconfirmed`,
`armani-post-founder-transition-continues`) that don't match the actual
short-form `signal_id` fields used in `2026-09-28.json`/`2026-10-05.json`.
The note even told readers to call `get_signal_status_history()` with the
wrong string, which would silently return an empty list. Traced the
mismatch back further: `2026-10-05.json`'s own `index_note` prose for both
signals self-referenced the long-form name instead of its own (already
shortened) `signal_id` field — that's where the stale name originated and
propagated into run 32's note.

Fixed via `save_report(revision_reason=..., corrected_at="2026-07-06")` on
both `data/reports/2026-10-05.json` (index_note self-reference) and
`data/reports/2026-12-07.json` (close-out note). Did not touch
`2027-01-18.json` (concurrent addition) or any other report.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 29 reports pass, 0 failures
