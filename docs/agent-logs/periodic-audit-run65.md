# Periodic confidence + coverage audit — run 65

Ran across 57 reports (2027-07-12, 2027-07-19, 2027-07-26 added by
concurrent agents since run 64's 56). `gh` cadence check skipped, not
due until run 70.

## Confidence audit

`audit_confidence.py`: 65 mismatches, same count as run 62-64. All but
one are `assigned < derived` (editor conservatism). The one
`assigned > derived` case is again 2027-05-17.json's Dior Cruise at
LACMA signal (`assigned='high'`, `derived='medium'`, corroboration=6,
editorial-only). Re-read the `human_editor_note` reasoning (discrete,
photographed, celebrity-attended event, 6 independent editorial
outlets, no institutional/retail sector expected to weigh in this
fast) — still sound, confirmed not a bug, no change made. The three
new reports (couture-week reception, LV waterfall backlash) contribute
zero mismatches.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean,
unchanged from prior runs.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

57 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings
raised — same count and same four reports as runs 62-64 (2026-09-14,
2026-09-28, 2026-10-05, 2027-06-28). Read each flagged report's actual
JSON directly: all four remain the documented negation/precedent-
mention false-positive pattern. No genuine mismatch, no growth in
count.

## Dormancy / prolonged-silence check

Ran `get_signal_status_history()`/`is_prolonged_silence()` across every
signal_id in the archive. Five are `True`: `cfda-fashion-fund-winner`
and `cfda-fashion-awards-2026` (last seen 2027-01-04),
`wales-bonner-hermes-debut` and `paris-post-show-coverage-gap` (last
seen 2027-03-08), and `met-gala-2027-coverage-gap` (last seen
2027-07-05). All five were already transitioned to "untracked going
forward pending new information" in prior runs; read 2027-07-12 and
2027-07-26 directly and confirmed both correctly state Met Gala/Wales
Bonner/CFDA "were not re-litigated this window per SKILL.md workflow
note 10" rather than repeating stale carry-forward prose. The new
couture-reception and LV-waterfall signal_ids are single-occurrence,
not prolonged. Nothing new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 57 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run. No commits made, per
instructions.
