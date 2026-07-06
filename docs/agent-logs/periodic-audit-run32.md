# Periodic confidence + dormancy audit — run 32

Ran `validate_all_reports.py` (24 reports, all pass), `audit_confidence.py`
(64 signals, 34 mismatches), and `check_field_coverage.py` fresh.

## Confidence audit

All 34 mismatches are assigned-lower-than-derived (editor conservatism), same
direction as every prior run — no `assigned=high, derived=low/medium` case.
Checked runs 24-31's additions (2026-08-31 through 2026-12-07) specifically:
mismatches there are the two back-to-school signals, the NYFW forecast-tense
flag, the Milan schedule-inconsistency signal, and all seven CFDA Fashion Fund
carry-forward windows plus the two CFDA Fashion Awards windows — all
low-confidence institutional/editorial signals held conservatively below what
the formula would derive. None concerning.

## Field coverage

0 warnings — only backend-only `confidence_source` is untyped/unreferenced,
which is expected (matches run 25's baseline).

## Dormancy check

Checked every signal_id appearing in 2+ reports via
`get_signal_status_history()`. Found one genuine gap: **versace-mulier-debut-
timing-unconfirmed** and **armani-post-founder-transition-continues** both
last appeared in the 2026-10-05 report and never resurfaced across the
following 8 windows (2026-10-12 through 2026-12-07), but — unlike every other
comparable case (sheer-layering, soft-tailoring, off-duty-varsity,
peplum-waist-revival, lfw-eligibility-wholesale-requirement-dropped, all of
which got an explicit "closed by silence" note after 3-4 quiet windows) —
these two never received a close-out note.

## Fix applied

Appended a retroactive close-out note (limitations + archive_tags) to
`data/reports/2026-12-07.json` via `save_report(revision_reason=...,
corrected_at="2026-07-06")`, following the established precedent. Did not
touch the new `2026-12-14.json` being added concurrently.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 24 reports pass, 0 failures
