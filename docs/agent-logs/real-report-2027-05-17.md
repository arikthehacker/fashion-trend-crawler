# Real report: 2027-05-17 (47th weekly window)

Created `data/reports/2027-05-17.json`, collection window May 11-17, 2027.

## Dior Cruise 2027 (LACMA) lands in this window, clears the corroboration bar

The 2027-05-10 report flagged Dior's Cruise 2027 show (LACMA, May 13) as
bracketing just past its close. It now falls inside this window. WebSearch
found real, consistent multi-outlet editorial coverage (WWD, The Hollywood
Reporter, LAmag, The Impression, Whitewall, Modern Luxury) of Jonathan
Anderson's debut Cruise collection for Dior: an Old Hollywood/Marlene
Dietrich-referencing show at LACMA's new Geffen Galleries wing, a reworked
Dietrich-era Dior Accacias jacket, an Ed Ruscha shirting collaboration,
Philip Treacy millinery, and a celebrity front row. Logged as
`dior-cruise-2027-lacma-debut` -- `designer_signal`, `editorial` sector,
`flash` volatility, `designer_originated` origin, `source_corroboration_count: 6`.

Confidence was manually set to `high`, overriding `derive_confidence()`'s
`medium` (six sources but a single sector). `human_editor_note` documents
the override explicitly: single-sector convergence here reflects a fast,
photographed runway event rather than genuine uncertainty about whether it
happened, since no other sector would plausibly weigh in this quickly.
`validate_all_reports.py`'s non-blocking confidence check correctly flagged
this as a WARNING, not a failure -- expected, and consistent with the
override rationale already written into the signal.

## Met Gala 2027: gap reaffirmed a third consecutive window

Re-checked once more (per task brief) for any theme/co-chair/red-carpet
coverage at any point. None found -- same result as 2027-05-03 and
2027-05-10. Logged in `limitations`/`archive_tags`, not re-litigated beyond
noting the gap is now three windows long.

## Not re-litigated

Wales Bonner/Hermes and CFDA Fashion Fund/Awards were not re-checked, per
SKILL.md workflow note 10 and the task brief -- no new coverage surfaced
for either regardless.

## Verification

- Checked existing `signal_id`s across all 46 prior reports before writing
  -- `dior-cruise-2027-lacma-debut` has no collision.
- `python -m py_compile src/*.py` -- passed.
- `python src/validate_all_reports.py` -- `OK: all 47 report(s)... passed
  schema validation.` (plus the expected non-blocking confidence WARNING
  described above).
- Saved via `report_schema.save_report()`.
- Scratch script (`scratch_build_report.py`, repo root) deleted after use.

Not committed, per instructions.
