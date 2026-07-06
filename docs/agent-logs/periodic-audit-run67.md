# Periodic confidence + coverage audit — run 67

Ran across 59 reports (2027-08-16 "Chanel acquires Charvet" added since
run 66's 58). `gh` cadence check skipped, not due until run 70.

## Confidence audit

`audit_confidence.py`: mismatches up by exactly +1 for the new
2027-08-16 entry (assigned medium vs. derived high) — ordinary editor
conservatism, not a bug. All other `assigned < derived` cases unchanged
from run 66. The one `assigned > derived` case remains 2027-05-17.json's
Dior Cruise at LACMA signal (`assigned='high'`, `derived='medium'`,
corroboration=6, editorial-only). Re-confirmed the `human_editor_note`
reasoning (discrete, photographed, celebrity-attended event, 6
independent editorial outlets, no institutional/retail sector expected
to weigh in this fast) — still sound, no change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean,
unchanged from prior runs.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

59 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings
raised — same count and same four reports as runs 62-66 (2026-09-14,
2026-09-28, 2026-10-05, 2027-06-28). Read each flagged report's actual
JSON directly: all four remain the documented negation/precedent-
mention false-positive pattern (e.g. "is not carried forward this
window" / citing a prior signal_id as precedent rather than claiming
reuse). No genuine mismatch, no growth in count.

## Dormancy / prolonged-silence check

Ran `get_signal_status_history()`/`is_prolonged_silence()` across every
signal_id in the archive. Same five `True` as run 66:
`cfda-fashion-fund-winner` and `cfda-fashion-awards-2026` (last seen
2027-01-04), `wales-bonner-hermes-debut` and `paris-post-show-coverage-gap`
(last seen 2027-03-08), and `met-gala-2027-coverage-gap` (last seen
2027-07-05). All five already transitioned to "untracked going forward
pending new information" in prior runs; the newest report (2027-08-16)
doesn't reference any of them, so no re-carrying-forward risk. Nothing
new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 59 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run (no genuine mismatches
found requiring `save_report(revision_reason=..., corrected_at=...)`).
No commits made, per instructions.
