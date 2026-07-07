# Periodic confidence + coverage audit — run 49

Ran across 41 reports (one new report since run 48: 2027-04-05).

## Confidence audit

`audit_confidence.py`: 94 signals checked, 49 mismatches (up from 48 in
run 47/48, tracking the new report). Reviewed the full list — every
mismatch is still `assigned < derived` (editor conservatism), same
pattern as runs 46-48. The one new entry is 2027-04-05 "'Glamoratti'
80s power-dressing revival surfaces via Pinterest Predicts data"
(assigned=medium, derived=high, source_sectors social+editorial) —
reasonable to hold conservative given social-origin amplification.
No `assigned=high, derived=low/medium` case anywhere. Nothing
genuinely concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37/39/41/43-48 (`confidence_source` remains the
one intentionally backend-only field).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable across 16+ consecutive
checks now (runs 26 onward per TODO.md). CI's real GitHub-Actions
pass/fail status remains genuinely unconfirmed — manual YAML
read-throughs only.

## Dormancy / prolonged-silence check

Walked all unique `signal_id`s across 41 reports via
`is_prolonged_silence()`. Same four flagged as run 47/48, all still
correctly handled — no new occurrence since their last-tracked windows
(`cfda-fashion-fund-winner`/`cfda-fashion-awards-2026` last at
2027-01-04, `wales-bonner-hermes-debut`/`paris-post-show-coverage-gap`
last at 2027-03-08), each carrying reasoned close-out/continuation
prose, not boilerplate "still open." The new 2027-04-05 report only
mentions `paris-post-show-coverage-gap` in passing inside its
limitations text (not a new tracked occurrence), so no fix needed.
No new signal_id has crossed into prolonged silence since run 48.

**`getRecurringSignals({styleOnly: true})` spot-check (added run 48):**
Recomputed the raw recurrence counts directly from `data/reports/*.json`
(occurrences >= 4): `cfda-fashion-fund-winner` (11, type
`institutional_policy`), `cfda-fashion-awards-2026` (6,
`institutional_policy`), `wales-bonner-hermes-debut` (8,
`designer_signal`), `paris-post-show-coverage-gap` (6,
`institutional_policy`) — none are in `STYLE_AESTHETIC_TYPES`, so
`styleOnly: true` correctly filters all four out, returning an empty
list rather than throwing or misclassifying. Behaving as designed.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 41 reports pass

No fixes were needed this run — all checks came back clean, consistent
with runs 46-48. No commits made, per instructions.
