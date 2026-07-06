# Periodic confidence + coverage audit — run 45

Ran across 37 reports (2026-05-07 through 2027-03-08, one new report since
run 44).

## Confidence audit

`audit_confidence.py`: 89 signals checked, 44 mismatches, every one still
`assigned < derived` (editor conservatism — Sheer layering/Peplum/CFDA
prolonged-silence/Wales Bonner pre-show entries all assigned lower than
derived). No `assigned=high, derived=low/medium` case anywhere. Nothing
concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43/44 (`confidence_source` remains the one
intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 11+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s via `get_signal_status_history()` /
`is_prolonged_silence()`. Four flagged, all correctly handled:

- `cfda-fashion-fund-winner` (11 windows) / `cfda-fashion-awards-2026`
  (6 windows): carry the "untracked going forward pending new information"
  close-out prose from 2027-01-04. No fix needed.
- `paris-post-show-coverage-gap` (6 windows): index_note explicitly
  reasons that SKILL.md note 10's transition convention doesn't apply here
  (it's a fixed institutional-calendar fact, not an open factual
  question), so routine tracking correctly continues. No fix needed.
- `wales-bonner-hermes-debut`: the 2027-03-08 report (the checkpoint the
  2027-03-01 report explicitly set) **has already made the transition** —
  name/index_note/human_editor_note all now read "untracked going forward
  pending new information," citing SKILL.md note 10 by name. Verified it
  is genuinely excluded from re-appearing as an active top-signal claim:
  the entry documents the deprioritization honestly (not a resolution
  claim) and instructs future agents to resume tracking immediately if
  real coverage appears. Convention correctly applied — no fix needed.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 37 reports pass

No fixes were needed this run — all three checks came back clean, and the
Wales Bonner transition flagged as pending in run 44 has since landed
correctly and was verified in detail. No commits made, per instructions.
