# Periodic confidence + coverage audit — run 55

Ran across 47 reports (one new report since run 54, 2027-05-17). `gh`
CLI cadence check skipped this run per instructions (not due until
run 60).

## Confidence audit

`audit_confidence.py`: 99 signals checked, 51 mismatches (up from 50
in run 54 — the one new report added no new mismatch of its own type
beyond the documented override, see below). Reviewed the full output:
every mismatch except one is `assigned < derived` (editor conservatism,
e.g. `assigned='low'/'medium'` vs. `derived='medium'/'high'`) —
nothing genuinely concerning there, no fix applied.

The one `assigned > derived` case is `2027-05-17.json`'s "Dior Cruise
2027 at LACMA" signal (`assigned='high'`, `derived='medium'`,
corroboration_count=6, single sector `editorial`). Confirmed this is
the deliberate, documented override called out in this run's
instructions: `human_editor_note` explains the reasoning (discrete,
photographed, celebrity-attended runway event with matching factual
detail across 6 independent editorial outlets; no institutional/retail
sector is expected to weigh in on a runway show this quickly, so
penalizing single-sector convergence here would mistake a sourcing-mix
gap for real uncertainty). Reasoning still holds — not a bug, no
change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as run 54 (`confidence_source` remains the one intentionally
backend-only field).

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s across all 47 reports via
`is_prolonged_silence()`. Same four flagged as runs 47-54 — no new
occurrence:

- `cfda-fashion-fund-winner`
- `cfda-fashion-awards-2026`
- `wales-bonner-hermes-debut`
- `paris-post-show-coverage-gap`

The new 2027-05-17 report doesn't reference any of these signal_ids
(it's a standalone Dior Cruise runway event), so no close-out
language was owed there. No signal_id newly crossed the
prolonged-silence threshold this run.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 47 reports pass
  (one non-blocking confidence WARNING, expected: the documented
  Dior Cruise override)

No fixes were needed this run. No commits made, per instructions.
