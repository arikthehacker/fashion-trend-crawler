# Periodic confidence + coverage audit — run 41

Ran across 34 reports (2026-05-07 through 2027-02-08).

## Confidence audit

`audit_confidence.py`: 81 signals checked, 44 mismatches, every single one
still `assigned < derived` (editor conservatism — e.g. Wales Bonner/Hermes
menswear debut assigned=medium, derived=high; the long-running CFDA
Fashion Fund/Awards prolonged-silence entries assigned=low, derived=medium).
No `assigned=high, derived=low/medium` case found anywhere. Nothing
concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39 (`confidence_source` remains the one
intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 8+ consecutive checks
now (runs 26 onward per TODO.md). CI's real GitHub-Actions pass/fail
status remains genuinely unconfirmed — manual YAML read-throughs only.

## Dormancy / prolonged-silence check

Walked all 47 unique `signal_id`s via `get_signal_status_history()` /
`is_prolonged_silence()` and flagged anything with a gap of 3+ report
windows since last appearance.

- `cfda-fashion-fund-winner` and `cfda-fashion-awards-2026`: both
  `is_prolonged_silence()`-True, but already received the "untracked
  going forward pending new information" close-out prose in the
  2027-01-04 report (per SKILL.md workflow note 10) — that's exactly why
  they haven't reappeared in the 5 windows since. No fix needed.
- `off-duty-varsity`, `sheer-layering`, `soft-tailoring`,
  `peplum-waist-revival`, `lfw-wholesale-eligibility-dropped`,
  `versace-mulier-debut-unconfirmed`: all inspected at their last
  appearance and each already carries a proper `EDITORIAL CLOSE-OUT` /
  retirement note in `human_editor_note`. Legitimately closed, not
  neglected.
- `golden-globes-2027-ceremony-date`, `paris-menswear-couture-fw27-calendar`:
  only 1 appearance so far, gap of 3-4 windows — too new to be a
  prolonged-silence case; not flagged.
- No signal_id found with a real, unaddressed gap requiring a new
  close-out this run.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 34 reports pass

No fixes were needed this run — all three checks came back clean against
the established baseline. No commits made, per instructions.
