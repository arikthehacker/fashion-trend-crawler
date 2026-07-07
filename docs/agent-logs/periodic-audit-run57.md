# Periodic confidence + coverage audit — run 57

Ran across 50 reports (up from 48 in run 56; a concurrent agent this run
gave Met Gala 2027 a real tracked signal_id, not duplicated here). `gh`
CLI cadence check skipped per instructions (not due until run 60).

## Confidence audit

`audit_confidence.py`: 100 signals checked, 52 mismatches — same count
and same pattern as run 56. All but one are `assigned < derived`
(editor conservatism, not a bug). The one `assigned > derived` case is
again 2027-05-17.json's "Dior Cruise 2027 at LACMA" signal
(`assigned='high'`, `derived='medium'`, corroboration_count=6, single
sector `editorial`). Re-read the `human_editor_note`: reasoning
unchanged from runs 55/56 (discrete, photographed, celebrity-attended
event corroborated by 6 independent editorial outlets; no
institutional/retail sector expected to weigh in this fast). Confirmed
still correctly reasoned — no change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean.

## Dormancy / prolonged-silence check

`is_prolonged_silence()` flagged the same four signal_ids as prior
runs: `cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `paris-post-show-coverage-gap`. The first
three already carry explicit "untracked going forward pending new
information" language every window (confirmed current as of
2027-05-31.json).

**Found and fixed a real gap**: `paris-post-show-coverage-gap` was
tracked as a `top_signals` entry through 2027-03-08 (6 windows), then
continued only in `limitations` prose through 2027-04-26 (twelve
consecutive zero-coverage windows, well past the prolonged-silence
threshold) — but then it silently vanished from every report from
2027-05-03 through 2027-05-31 (5 consecutive windows) with **no**
close-out note, unlike the explicit transition Wales Bonner/CFDA
received at their own checkpoints. This is exactly the "gone silent
long enough to warrant a close-out that hasn't been applied" case.
Fixed via `save_report()` on 2027-05-31.json: added a `limitations`
entry documenting the gap and formally applying the "untracked going
forward pending new information" treatment per SKILL.md note 10, with
`revision_reason`/`corrected_at='2027-05-31'` recorded in
`revision_history`.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 50 reports pass (one
  non-blocking confidence WARNING, expected: the documented Dior
  Cruise override)

No commits made, per instructions.
