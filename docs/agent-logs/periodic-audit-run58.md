# Periodic confidence + coverage audit — run 58

Ran across 50 reports (2027-06-07.json added by a concurrent agent since
run 57, replacing net file count at 50). `gh` cadence check skipped per
instructions (not due until run 60).

## Confidence audit

`audit_confidence.py`: 103 signals checked, 55 mismatches. All but one
are `assigned < derived` (editor conservatism — includes the newly
added `Met Gala 2027 coverage gap` signal, assigned='low'/derived='medium',
which is conservative, not concerning). The one `assigned > derived` case
is again 2027-05-17.json's Dior Cruise at LACMA signal (`assigned='high'`,
`derived='medium'`, corroboration_count=6, single sector `editorial`).
Re-read the `human_editor_note`: reasoning unchanged (discrete,
photographed, celebrity-attended event corroborated by 6 independent
editorial outlets; no institutional/retail sector expected to weigh in
this fast). Confirmed still correctly reasoned — no change made. No
genuinely concerning high/low-medium mismatches found.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean.

## Dormancy / prolonged-silence check

`is_prolonged_silence()` over current top_signals flags the same four
signal_ids as run 57: `cfda-fashion-fund-winner`,
`cfda-fashion-awards-2026`, `wales-bonner-hermes-debut`,
`paris-post-show-coverage-gap`. All four already carry the
"untracked going forward pending new information" close-out language
applied at their own checkpoints (paris- one fixed in run 57); no new
gap found.

**Met Gala consistency check**: the concurrent agent's 2027-06-07.json
references Met Gala again via `limitations` prose ("checked a sixth
consecutive window... treated as a genuine, unresolved coverage gap...
not evidence of cancellation") and an `archive_tags` entry
(`met-gala-2027-postevent-coverage-gap-sixth-window`), rather than a
repeated `top_signals` entry with the `met-gala-2027-coverage-gap`
signal_id. This mirrors the established convention for
Wales Bonner/CFDA (prose-only continuation after the initial tracked
entry) and correctly frames it as SKILL.md note-10 factual-silence, not
style-dormancy. Consistent — no fix needed.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 50 reports pass (one
  non-blocking confidence WARNING, expected: the documented Dior
  Cruise override)

No commits made, per instructions.
