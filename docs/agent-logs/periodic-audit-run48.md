# Periodic confidence + coverage audit — run 48

Ran across 40 reports (one new report since run 47).

## Confidence audit

`audit_confidence.py`: 93 signals checked, 48 mismatches (up from 47 in
run 47, tracking the one new report). Reviewed the full list — every
mismatch is still `assigned < derived` (editor conservatism: Sheer
layering/Soft tailoring/Archival romanticism/Peplum rechecks, CFDA
prolonged-silence entries, Wales Bonner pre-show coverage, Milan
date-inconsistency, Golden Globes pending coverage, FW27-28 opening,
plus new 2027-03-15/03-22/03-29 forecast-terminology entries). No
`assigned=high, derived=low/medium` case anywhere. Nothing genuinely
concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43/44/45/46/47 (`confidence_source`
remains the one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 15+ consecutive
checks now (runs 26 onward per TODO.md). CI's real GitHub-Actions
pass/fail status remains genuinely unconfirmed — manual YAML
read-throughs only.

## Dormancy / prolonged-silence check

Walked all 51 unique `signal_id`s across 40 reports via
`is_prolonged_silence()`. Same four flagged as run 47, all still
correctly handled:

- `cfda-fashion-fund-winner` and `cfda-fashion-awards-2026`: carry the
  "untracked going forward pending new information" close-out prose.
  No fix needed.
- `paris-post-show-coverage-gap`: index_note still correctly reasons
  this is a fixed institutional-calendar fact, not an open factual
  question — routine tracking continues. No fix needed.
- `wales-bonner-hermes-debut`: still carries the "untracked going
  forward pending new information" transition. No fix needed.

No new signal_id has crossed into prolonged silence since run 47.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 40 reports pass

No fixes were needed this run — all three checks came back clean, same
as runs 46-47. No commits made, per instructions.
