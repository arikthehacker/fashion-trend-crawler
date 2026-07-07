# Periodic confidence + coverage audit — run 46

Ran across 38 reports (one new report since run 45).

## Confidence audit

`audit_confidence.py`: 91 signals checked, 46 mismatches. Reviewed every
one individually — every mismatch is still `assigned < derived` (editor
conservatism: Sheer layering/Soft tailoring/Peplum/CFDA prolonged-silence
entries, Wales Bonner pre-show/debut coverage, Milan date-inconsistency,
etc.). No `assigned=high, derived=low/medium` case anywhere. Nothing
genuinely concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43/44/45 (`confidence_source` remains the
one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 12+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s via `is_prolonged_silence()`. Same four
flagged as run 45, all correctly handled — verified by reading each
signal's latest actual entry (not just the trend summary):

- `cfda-fashion-fund-winner` (last seen 2027-01-04, 11th window) /
  `cfda-fashion-awards-2026` (last seen 2027-01-04, 6th window): both
  carry the "untracked going forward pending new information" close-out
  prose. No fix needed.
- `paris-post-show-coverage-gap` (last seen 2027-03-08): index_note still
  explicitly reasons this is a fixed institutional-calendar fact, not an
  open factual question, so routine tracking correctly continues rather
  than transitioning. No fix needed.
- `wales-bonner-hermes-debut` (last seen 2027-03-08): name/index_note/
  human_editor_note all read "untracked going forward pending new
  information," citing SKILL.md note 10. Transition (first applied
  2027-03-08, verified by run 45) remains intact and correctly excluded
  from active top-signal claims. No fix needed.

No new signal_id has crossed into prolonged silence since run 45.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 38 reports pass

No fixes were needed this run — all three checks came back clean, same
as run 45. No commits made, per instructions.
