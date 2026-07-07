# Periodic confidence + coverage audit — run 54

Ran across 46 reports (one new report since run 53, 2027-05-10). `gh`
CLI cadence check skipped this run per instructions (not due until
run 60).

## Confidence audit

`audit_confidence.py`: 98 signals checked, 50 mismatches — same count
and same list as run 53. Reviewed the full output: every mismatch is
`assigned < derived` (editor conservatism, e.g. `assigned='low'/'medium'`
vs. `derived='medium'/'high'`). No `assigned='high', derived='low'/
'medium'` case anywhere. Nothing genuinely concerning; no fix applied.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as prior runs (`confidence_source` remains the one
intentionally backend-only field).

## Dormancy / prolonged-silence check

Walked all 54 unique `signal_id`s across all 46 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-53 — no new
occurrence:

- `cfda-fashion-fund-winner` (last tracked 2027-01-04)
- `cfda-fashion-awards-2026` (last tracked 2027-01-04)
- `wales-bonner-hermes-debut` (last tracked 2027-03-08)
- `paris-post-show-coverage-gap` (last tracked 2027-03-08)

Confirmed via grep that "untracked going forward" prose is present in
both new-since-last-audit reports (2027-05-03 and 2027-05-10), not
just up through the prior cutoff — the close-out language continues
to be correctly applied, not re-litigated. No new signal_id has
crossed into prolonged silence since run 53.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 46 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-53. No commits made, per instructions.
