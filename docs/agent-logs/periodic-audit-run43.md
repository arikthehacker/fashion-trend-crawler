# Periodic confidence + coverage audit — run 43

Ran across 35 reports (2026-05-07 through 2027-02-22).

## Confidence audit

`audit_confidence.py`: 85 signals checked, 44 mismatches, every one still
`assigned < derived` (editor conservatism — e.g. Wales Bonner/Hermes
menswear debut anticipation coverage assigned=medium, derived=high; the
long-running CFDA prolonged-silence entries assigned=low, derived=medium).
No `assigned=high, derived=low/medium` case anywhere. Nothing concerning;
no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41 (`confidence_source` remains the one
intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 9+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all 47 unique `signal_id`s via `get_signal_status_history()` /
`is_prolonged_silence()`. Four flagged as currently past the threshold:

- `cfda-fashion-fund-winner` / `cfda-fashion-awards-2026`: already carry
  the "untracked going forward pending new information" close-out prose
  from the 2027-01-04 report (per SKILL.md note 10) — that's why they
  haven't reappeared since. No fix needed.
- `wales-bonner-hermes-menswear-debut-2027` (6 consecutive windows,
  2027-01-18 through 2027-02-22) and
  `paris-january-2027-weeks-post-show-coverage-gap` (4 consecutive
  windows, 2027-02-01 through 2027-02-22): both are past
  `is_prolonged_silence()`'s default threshold, but their `index_note`/
  `human_editor_note` explicitly acknowledge this, cite SKILL.md note 10's
  "~3 windows past crossing" convention, and defer the "untracked going
  forward" transition to a stated future checkpoint (2027-03-08) rather
  than either repeating a bare "still open" note or prematurely declaring
  the questions resolved/closed. This is a correct, deliberate application
  of note 10 (these are factual/institutional-coverage questions, not
  style signals, so no `EDITORIAL CLOSE-OUT` applies). No fix needed this
  run; worth re-checking once the 2027-03-08 report exists.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 35 reports pass

No fixes were needed this run — all three checks came back clean against
the established baseline, and the two newly-flagged prolonged-silence
signals already carry correctly-deferred, self-documenting notes rather
than needing an intervention. No commits made, per instructions.
