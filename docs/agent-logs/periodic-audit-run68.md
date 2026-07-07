# Periodic confidence + coverage audit — run 68

Ran across 60 reports (2027-08-23 "Martens' Margiela debut reception"
added since run 67's 59). `gh` cadence check skipped, not due until run 70.

## Confidence audit

`audit_confidence.py`: new 2027-08-23 entry (assigned='medium',
derived='high', corroboration=6, source_sectors=['editorial','unclear'])
— read the report directly: `human_editor_note` gives the same reasoned
call as 2027-08-09/2027-08-16 (only 2 of 6 corroborating domains land in
`taxonomy.py`'s `DOMAIN_SECTOR_MAP`; the other 4 classify 'unclear', so
counting that as genuine cross-sector confirmation would reward a domain-
map gap, not real corroboration). Ordinary editor conservatism, not a bug.
All other `assigned < derived` cases unchanged from run 67. The one
`assigned > derived` case remains 2027-05-17.json's Dior Cruise/LACMA
signal (`assigned='high'`, `derived='medium'`). Re-confirmed the
`human_editor_note` reasoning (discrete, photographed, celebrity-attended
event, 6 independent editorial outlets, no institutional/retail sector
expected to weigh in this fast) — still sound, no change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean, unchanged.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

60 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings raised
— same count and same four reports as runs 62-67 (2026-09-14, 2026-09-28,
2026-10-05, 2027-06-28). Read each flagged report's actual JSON directly:
all four remain the documented negation/precedent-mention false-positive
pattern (e.g. "is not carried forward this window" / citing a prior
signal_id as precedent rather than claiming reuse of it). No genuine
mismatch, no growth in count.

## Dormancy / prolonged-silence check

Ran `get_signal_status_history()`/`is_prolonged_silence()` across every
signal_id in the archive (71 distinct ids). Same five `True` as run 67:
`cfda-fashion-fund-winner` and `cfda-fashion-awards-2026` (last seen
2027-01-04), `wales-bonner-hermes-debut` and `paris-post-show-coverage-gap`
(last seen 2027-03-08), and `met-gala-2027-coverage-gap` (last seen
2027-07-05). All five already transitioned to "untracked going forward
pending new information" in prior runs; the new 2027-08-23 report
explicitly reconfirms this in its `archive_tags` for met-gala,
wales-bonner, and cfda, without re-litigating them. Nothing new to close
out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 60 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run (no genuine mismatches
found requiring `save_report(revision_reason=..., corrected_at=...)`).
No commits made, per instructions. Note: did not touch/investigate the
historical godet-skirt garments/silhouettes overlap backfill question —
left for the concurrent agent handling that.
