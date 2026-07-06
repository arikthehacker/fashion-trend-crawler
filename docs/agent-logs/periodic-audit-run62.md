# Periodic confidence + coverage audit — run 62

Ran across 54 reports (2027-07-05.json added since run 61). `gh` cadence
check skipped per instructions (not due until run 70).

## Confidence audit

`audit_confidence.py`: 113 signals checked, 65 mismatches. All but one are
`assigned < derived` (editor conservatism, consistent with every prior
run). The one `assigned > derived` case is again 2027-05-17.json's Dior
Cruise at LACMA signal (`assigned='high'`, `derived='medium'`). Re-read
the `human_editor_note` reasoning (discrete, photographed, celebrity-
attended event, 6 independent editorial outlets, no institutional/retail
sector expected to weigh in this fast) — still sound, no change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean, unchanged.

## Signal reuse claims (`check_signal_reuse_claims.py --all`, as requested)

54 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings
raised. Read each flagged report's actual JSON directly rather than
trusting the tool output:

- 2026-09-14, 2026-09-28, 2026-10-05: each flagged text explicitly states
  the named signal_id was *not* carried forward this window ("is not
  carried forward", "continuing-but-quiet... not re-asserted") — these
  are prose *acknowledging absence*, not claims of reuse into this
  report's own top_signals. All false positives, exactly the negation
  blind spot the script's own docstring calls out ("does not understand
  negation").
- 2027-06-28: met-gala-2027-coverage-gap's own index_note mentions
  `wales-bonner-hermes-debut` only as a citation of precedent for the
  untracked-transition pattern, not a reuse claim about that signal in
  this report. False positive, same root cause.

No genuine mismatches found. Tool is working as documented; no fix
needed to the script or to any report.

## Dormancy / prolonged-silence check

Checked `cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `paris-post-show-coverage-gap`,
`met-gala-2027-coverage-gap`, and the newer `wimbledon-tenniscore-
polka-dot` via `get_signal_status_history()`/`is_prolonged_silence()`.
First five are `is_prolonged_silence() == True` but all were already
transitioned to "untracked going forward pending new information" in
prior runs (met-gala in run 61) and 2027-07-05's own prose for met-gala
correctly continues that transitioned state without re-litigating.
Wimbledon has only 1 occurrence, not prolonged. Nothing new to close out.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 54 reports pass (same
  one non-blocking Dior Cruise WARNING, expected)

No changes made to any report or script this run. No commits made, per
instructions.
