# Periodic confidence + coverage audit — run 47

Ran across 39 reports (one new report since run 46).

## Confidence audit

`audit_confidence.py`: 92 signals checked, 47 mismatches. Reviewed the
full list — every mismatch is `assigned < derived` (editor conservatism:
Sheer layering/Soft tailoring/Archival romanticism/Peplum re-checks,
CFDA prolonged-silence entries, Wales Bonner pre-show coverage, Milan
date-inconsistency, Golden Globes pending coverage, FW27-28 opening,
etc.). No `assigned=high, derived=low/medium` case anywhere. Nothing
genuinely concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43/44/45/46 (`confidence_source` remains
the one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 13+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all 50 unique `signal_id`s via `is_prolonged_silence()`. Same
four flagged as run 46, all still correctly handled:

- `cfda-fashion-fund-winner` and `cfda-fashion-awards-2026` (both last
  seen 2027-01-04): carry the "untracked going forward pending new
  information" close-out prose. No fix needed.
- `paris-post-show-coverage-gap` (last seen 2027-03-08): index_note
  still reasons this is a fixed institutional-calendar fact, not an
  open factual question, so routine tracking correctly continues. No
  fix needed.
- `wales-bonner-hermes-debut` (last seen 2027-03-08): still carries the
  "untracked going forward pending new information" transition. No fix
  needed.

No new signal_id has crossed into prolonged silence since run 46.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 39 reports pass

No fixes were needed this run — all three checks came back clean, same
as run 46. No commits made, per instructions.
