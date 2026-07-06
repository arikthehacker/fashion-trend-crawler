# Periodic confidence + coverage audit — run 44

Ran across 36 reports (2026-05-07 through 2027-03-01, one new report since
run 43).

## Confidence audit

`audit_confidence.py`: 87 signals checked, 44 mismatches, every one still
`assigned < derived` (editor conservatism — Wales Bonner/Hermes debut
coverage assigned=medium/derived=high, CFDA prolonged-silence entries
assigned=low/derived=medium, etc). No `assigned=high, derived=low/medium`
case anywhere. Nothing concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43 (`confidence_source` remains the one
intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 10+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s via `get_signal_status_history()` /
`is_prolonged_silence()`. Same four flagged as run 43, now further along:

- `cfda-fashion-fund-winner` (11 windows) / `cfda-fashion-awards-2026`
  (6 windows): already carry the "untracked going forward pending new
  information" close-out prose from 2027-01-04. No fix needed.
- `wales-bonner-hermes-menswear-debut-2027` (now 7 consecutive windows,
  through 2027-03-01) and `paris-january-2027-weeks-post-show-coverage-gap`
  (now 5 windows): both notes explicitly cite the 2027-03-08 checkpoint set
  by a prior report as the deliberate transition point, and the current
  latest report (2027-03-01) is one window short of it — so holding at
  active tracking for one more window is correct, not a missed transition.
  No fix needed this run; re-check once the 2027-03-08 report exists, since
  that's the window where the "untracked going forward" language should
  actually land.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 36 reports pass

No fixes were needed this run — all three checks came back clean against
the established baseline, and the two prolonged-silence signals are
correctly still one window away from their previously-committed
transition checkpoint. No commits made, per instructions.
