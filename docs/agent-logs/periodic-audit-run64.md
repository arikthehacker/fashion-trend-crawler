# Periodic confidence + coverage audit — run 64

Ran across 56 reports (2027-07-05.json added by a concurrent agent since
run 63's 55). `gh` cadence check skipped, not due until run 70.

## Confidence audit

`audit_confidence.py`: 65 mismatches, same count as run 62/63. All but
one are `assigned < derived` (editor conservatism, consistent pattern).
The one `assigned > derived` case is again 2027-05-17.json's Dior Cruise
at LACMA signal (`assigned='high'`, `derived='medium'`, corroboration=6,
editorial-only). Re-read the `human_editor_note` reasoning (discrete,
photographed, celebrity-attended event, 6 independent editorial outlets,
no institutional/retail sector expected to weigh in this fast) — still
sound, confirmed not a bug, no change made. The new 2027-07-05.json
report contributes zero mismatches.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean,
unchanged from run 62/63.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, standing per convention #12)

56 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings raised
— same count and same four reports as run 62/63 (2026-09-14, 2026-09-28,
2026-10-05, 2027-06-28). Read each flagged report's actual JSON directly:
all four are still the documented negation/precedent-mention
false-positive pattern ("is not carried forward," "continuing-but-quiet
... not re-asserted," citing a prior signal_id as precedent rather than
claiming reuse). No genuine mismatch, no growth in count.

## Dormancy / prolonged-silence check

Checked `cfda-fashion-fund-winner` (11 occurrences), `cfda-fashion-awards-2026`
(6), `wales-bonner-hermes-debut` (8), `paris-post-show-coverage-gap` (6),
and `met-gala-2027-coverage-gap` (5) via `get_signal_status_history()` /
`is_prolonged_silence()` — all `True`, but all were already transitioned
to "untracked going forward pending new information" in prior runs.
Read the new 2027-07-05.json directly: its `limitations` explicitly
confirm Met Gala's tenth consecutive check with no new coverage and
correctly note Wales Bonner/CFDA were "not re-litigated ... per SKILL.md
workflow note 10." `wimbledon-tenniscore-polka-dot` has only 1
occurrence, not prolonged. Nothing new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 56 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run. No commits made, per
instructions.
