# Periodic confidence + coverage audit — run 56

Ran across 48 reports (one new report since run 55, 2027-05-24). `gh`
CLI cadence check skipped this run per instructions (not due until
run 60).

## Confidence audit

`audit_confidence.py`: 100 signals checked, 52 mismatches (up from 51
in run 55). Reviewed the full output: every mismatch except one is
`assigned < derived` (editor conservatism) — nothing genuinely
concerning, no fix applied.

The one `assigned > derived` case remains `2027-05-17.json`'s "Dior
Cruise 2027 at LACMA" signal (`assigned='high'`, `derived='medium'`,
corroboration_count=6, single sector `editorial`). Re-read the
`human_editor_note`: reasoning is unchanged from run 55 (discrete,
photographed, celebrity-attended runway event corroborated by 6
independent editorial outlets; no institutional/retail sector is
expected to weigh in this fast, so penalizing single-sector
convergence here would mistake a sourcing-mix gap for real
uncertainty). Confirmed still correctly reasoned — not a bug, no
change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as run 55.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s via `is_prolonged_silence()`. Same four
flagged as runs 47-55, no new signal_id crossed the threshold:
`cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `paris-post-show-coverage-gap`.

Investigated Met Gala 2027 specifically, per this run's instructions.
It is *not* modeled as a `top_signals` entry with a `signal_id` — it
only appears in `limitations`/`archive_tags` free text
(`met-gala-2027-preevent-coverage-gap`,
`met-gala-2027-postevent-coverage-gap`, `...-fourth-window`) across
2027-05-03, 05-10, 05-17, and 05-24. That means
`is_prolonged_silence()` returns False for it (no top_signals history
to walk), and this run's 2027-05-24 report is only the **fourth**
consecutive zero-coverage window — i.e. it has just reached the
threshold `is_prolonged_silence()` uses (4), not yet the "~3 windows
past crossing" point at which section 10's "untracked going forward"
treatment applies (compare CFDA Fashion Fund winner, which wasn't
marked "untracked" until well past its own fourth window). Conclusion:
correctly still in normal "still watching" language this run
(`met-gala-2027-postevent-coverage-gap-fourth-window"`) — no close-out
or "untracked" language owed yet. Flag for the next 2-3 runs: if a
5th/6th/7th zero-coverage window occurs, apply the "untracked going
forward pending new information" treatment then, matching the
CFDA precedent.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 48 reports pass
  (one non-blocking confidence WARNING, expected: the documented
  Dior Cruise override)

No fixes were needed this run. No commits made, per instructions.
