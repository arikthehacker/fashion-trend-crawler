# Periodic confidence + coverage audit — run 53

Ran across 45 reports (no new reports since run 52). `gh` CLI cadence
check skipped this run per instructions (owned by a concurrent agent).

## Confidence audit

`audit_confidence.py`: 98 signals checked, 50 mismatches — identical
count and identical list to run 52. Reviewed the full output again:
every mismatch is `assigned < derived` (editor conservatism, e.g.
`assigned='low' derived='medium'/'high'`), same pattern as runs
46-52. No `assigned='high', derived='low'/'medium'` case anywhere.
Nothing genuinely concerning; no fix applied.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43-52 (`confidence_source` remains the
one intentionally backend-only field).

## Dormancy / prolonged-silence check

Walked all 54 unique `signal_id`s across all 45 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-52 — no new
occurrence:

- `cfda-fashion-fund-winner` (last tracked 2027-01-04)
- `cfda-fashion-awards-2026` (last tracked 2027-01-04)
- `wales-bonner-hermes-debut` (last tracked 2027-03-08)
- `paris-post-show-coverage-gap` (last tracked 2027-03-08)

Confirmed via grep that "untracked going forward" prose is present
through the most recent reports (2027-04-05 through 2027-05-03), not
just up to the prior audit's cutoff — the close-out language is still
correctly applied and not being re-litigated. No new signal_id has
crossed into prolonged silence since run 52.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 45 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-52. No commits made, per instructions.
