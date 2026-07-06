# Periodic confidence + coverage audit — run 52

Ran across 45 reports (two new since run 51's 43, from concurrent agents).

## Confidence audit

`audit_confidence.py`: 98 signals checked, 50 mismatches. Reviewed the
full list; every mismatch is `assigned < derived` (editor conservatism —
e.g. `assigned='medium' derived='high'`), the same pattern as runs
46-51. No `assigned='high', derived='low'/'medium'` case anywhere.
Nothing genuinely concerning; no fix applied.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43-51 (`confidence_source` remains the
one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found` (exit 127). This is the **20th consecutive check**
confirming non-availability (runs 26-51, now 52) — a round-number
milestone, but the honest status hasn't changed: CI's real
GitHub-Actions pass/fail state remains genuinely unconfirmed in this
environment, manual YAML read-throughs only. Given 20 consecutive
identical results, this is very unlikely to change without an
environment change (not a code fix) — future runs can probably drop to
a lighter-touch spot-check unless the environment changes.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s across all 45 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-51, all still
correctly handled — no new occurrence since their last-tracked windows
(`cfda-fashion-fund-winner`/`cfda-fashion-awards-2026` last at
2027-01-04, `wales-bonner-hermes-debut`/`paris-post-show-coverage-gap`
last at 2027-03-08). Confirmed via grep that later reports
(2027-03-08 through 2027-04-26) reference these ids only in
already-applied "untracked going forward" prose, not as re-opened
active tracking. No new signal_id has crossed into prolonged silence
since run 51.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 45 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-51. No commits made, per instructions.
