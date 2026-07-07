# Periodic confidence + coverage audit — run 69

Ran across 61 reports (2027-08-30 "Demna's Gucci debut reception" added
since run 68's 60). `gh` cadence check skipped, not due until run 70
(next run). Colors/aesthetic_terms vocabulary audit left to the concurrent
agent handling that this run — not duplicated here.

## Confidence audit

`audit_confidence.py`: new 2027-08-30 entry (assigned='medium',
derived='high', corroboration=5, source_sectors=['editorial','unclear'])
follows the same established pattern as 2027-08-09/16/23 — most
corroborating domains land in `taxonomy.py`'s 'unclear' bucket rather than
a distinct sector, so `derive_confidence()`'s cross-sector bump overstates
real corroboration. Editor conservatism, not a bug. All other
`assigned < derived` cases unchanged from run 68. The one `assigned >
derived` case, 2027-05-17.json's Dior Cruise/LACMA signal (`assigned='high'`,
`derived='medium'`), re-checked: `human_editor_note` reasoning (discrete,
photographed, celebrity-attended event, 6 independent editorial outlets,
no institutional/retail sector expected to weigh in this fast) still holds
— confirmed as the documented deliberate override, not touched.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean, unchanged.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

61 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings raised
— same count and same four reports as runs 62-68 (2026-09-14, 2026-09-28,
2026-10-05, 2027-06-28). Read each flagged report's JSON directly: all
four remain the documented negation/precedent-mention false-positive
pattern. No genuine mismatch, no growth in count — baseline holds at 4.

## Dormancy / prolonged-silence check

Ran `get_signal_status_history()`/`is_prolonged_silence()` across all 72
distinct signal_ids in the archive. Same five `True` as run 68:
`cfda-fashion-fund-winner` and `cfda-fashion-awards-2026` (last seen
2027-01-04), `wales-bonner-hermes-debut` and `paris-post-show-coverage-gap`
(last seen 2027-03-08), `met-gala-2027-coverage-gap` (last seen 2027-07-05).
All five already carry "untracked going forward pending new information"
annotations from prior runs; the new 2027-08-30 report doesn't reference
any of them. Nothing new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 61 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run (no genuine mismatches
found requiring `save_report(revision_reason=..., corrected_at=...)`).
No commits made, per instructions.
