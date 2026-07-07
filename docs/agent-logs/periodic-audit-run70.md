# Periodic confidence + coverage audit — run 70

Ran across 62 reports (2027-08-16 "Chanel acquires Charvet" and 2027-08-23
"Martens' Margiela debut reception" added since run 69's 61). `gh` cadence
check skipped this run per instructions. Domain classification work for
fhcm.paris/laforma.club left to the concurrent agent handling that —
not duplicated here.

## Confidence audit

`audit_confidence.py`: new entries (2027-08-16, 2027-08-23, plus the
previously-seen 2027-08-30) all follow the established pattern —
`assigned='medium'`/`derived='high'` with 'unclear' absorbing what would
otherwise be a distinct corroborating sector, inflating `derive_confidence()`'s
cross-sector bump. Editor conservatism, not a bug, consistent with every
`assigned < derived` case since run 61. The single `assigned > derived`
case, 2027-05-17.json's Dior Cruise/LACMA signal (`assigned='high'`,
`derived='medium'`), re-checked: `human_editor_note` reasoning (discrete,
photographed, celebrity-attended event, 6 independent editorial outlets,
no institutional/retail sector expected to weigh in this fast) still holds.
Confirmed as the documented deliberate override — not touched.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean, unchanged.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

62 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings raised —
same count and same four reports as runs 62-69 (2026-09-14, 2026-09-28,
2026-10-05, 2027-06-28). Read each flagged report's JSON directly: all four
remain the documented negation/precedent-mention false-positive pattern
(explicit "is not carried forward" / "not re-asserted" language, or citing
a prior signal_id as precedent rather than claiming reuse of it). No genuine
mismatch, no growth in count — baseline holds at 4.

## Dormancy / prolonged-silence check

Ran `get_signal_status_history()`/`is_prolonged_silence()` across all 73
distinct signal_ids in the archive (62 reports). Same five `True` as run 69:
`cfda-fashion-fund-winner` and `cfda-fashion-awards-2026` (last seen
2027-01-04), `wales-bonner-hermes-debut` and `paris-post-show-coverage-gap`
(last seen 2027-03-08), `met-gala-2027-coverage-gap` (last seen 2027-07-05).
All five already carry "untracked going forward pending new information"
annotations from prior runs; none of the new 2027-08-16/23/30 reports
reference them. Nothing new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 62 reports pass (same one
  non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run (no genuine mismatches
found requiring `save_report(revision_reason=..., corrected_at=...)`).
No commits made, per instructions.
