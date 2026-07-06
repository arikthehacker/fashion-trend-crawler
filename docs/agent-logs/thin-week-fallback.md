# Thin-week fallback

Addresses gap-analysis-run6.md #4: no honest low-signal report state existed,
per Nieman Lab burnout/sustainability research — a fixed weekly cadence needs
a defined "thin week" state instead of silent skipping or manufactured
filler signals.

## Changes

`src/report_schema.py`:
- Added `COLLECTION_STATUS_VALUES = ["normal", "thin"]`.
- Added `Report.collection_status: str = "normal"` and
  `Report.thin_week_note: str = ""` fields — both optional, default to
  "normal"/empty so existing reports remain valid unchanged.
- `validate_report()` now checks `collection_status` against
  `COLLECTION_STATUS_VALUES` (defaulting to "normal" when absent, matching
  the pattern used for `confidence_source`/`content_hash`).

`src/summarize.py` (prompt text only, no control-flow changes):
- Added an instruction telling the model not to stretch/duplicate/manufacture
  signals to appear comprehensive when source material yields only a small
  number of genuinely distinct, well-supported signals — instead set
  `collection_status: "thin"` and explain briefly in `thin_week_note`.
- No fixed signal-count target was introduced (none existed before); the
  instruction is qualitative ("small number ... genuinely distinct").
- Added `collection_status` and `thin_week_note` to the expected JSON
  response shape in the prompt.

## Verification

- `python -m py_compile src/*.py` — passed.
- Loaded and ran `validate_report()` against all 4 existing files in
  `data/reports/` (`2026-05-07`, `2026-07-06`, `2026-07-13`, `2026-07-20`) —
  all validate unchanged, `collection_status` absent in each and correctly
  defaults to "normal".

No other files touched; no commits made.
