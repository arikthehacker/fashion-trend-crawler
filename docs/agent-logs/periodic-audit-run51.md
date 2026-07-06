# Periodic confidence + coverage audit — run 51

Ran across 43 reports (one new since run 50: a concurrent agent added a
report during this session).

## Confidence audit

`audit_confidence.py`: 96 signals checked, 50 mismatches. Reviewed the
full list and grepped specifically for `assigned='high'` — zero
matches. Every mismatch is still `assigned < derived` (editor
conservatism), the same pattern as runs 46-50. No `assigned=high,
derived=low/medium` case anywhere. Nothing genuinely concerning; no
fix applied.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43-50 (`confidence_source` remains the
one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 19+ consecutive
checks now (runs 26 onward per TODO.md). CI's real GitHub-Actions
pass/fail status remains genuinely unconfirmed — manual YAML
read-throughs only.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s across all 43 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-50, all still
correctly handled — no new occurrence since their last-tracked windows
(`cfda-fashion-fund-winner`/`cfda-fashion-awards-2026` last at
2027-01-04, `wales-bonner-hermes-debut`/`paris-post-show-coverage-gap`
last at 2027-03-08). No new signal_id has crossed into prolonged
silence since run 50.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 43 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-50. No commits made, per instructions.
