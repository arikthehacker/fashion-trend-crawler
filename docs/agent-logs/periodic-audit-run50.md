# Periodic confidence + coverage audit — run 50

Ran across 42 reports (one new report since run 49: 2027-04-12).

## Confidence audit

`audit_confidence.py`: 95 signals checked, 50 mismatches (up from 49 in
run 49). Reviewed the full list and specifically grepped for
`assigned='high'` — zero matches. Every mismatch is still
`assigned < derived` (editor conservatism), same pattern as runs
46-49. The one new entry is 2027-04-12 "'Glamoratti' 80s power-dressing
revival: continued, broadening but non-independent amplification"
(assigned=medium, derived=high, source_sectors social+editorial) —
reasonable to hold conservative given social-origin amplification
language explicit in the signal name itself. No `assigned=high,
derived=low/medium` case anywhere. Nothing genuinely concerning; no
fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43-49 (`confidence_source` remains the
one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 18+ consecutive
checks now (runs 26 onward per TODO.md). CI's real GitHub-Actions
pass/fail status remains genuinely unconfirmed — manual YAML
read-throughs only.

## Dormancy / prolonged-silence check

Walked all 52 unique `signal_id`s across 42 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-49, all still
correctly handled — no new occurrence since their last-tracked windows
(`cfda-fashion-fund-winner`/`cfda-fashion-awards-2026` last at
2027-01-04, `wales-bonner-hermes-debut`/`paris-post-show-coverage-gap`
last at 2027-03-08), each carrying reasoned close-out/continuation
prose, not boilerplate "still open." No new signal_id has crossed into
prolonged silence since run 49.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 42 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-49. No commits made, per instructions.
