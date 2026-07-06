# Confidence derivation implementation

Implements the formula from `confidence-scoring-research.md` in
`src/report_schema.py` only. No changes to `summarize.py`'s prompt.

## What was added

- `HIGH_RELIABILITY_SECTORS`: filters `("editorial", "designer_origin",
  "institutional")` against `taxonomy.SOURCE_SECTORS` so only real sector
  names are used.
- `derive_confidence(signal) -> str`: standalone helper, accepts a `Signal`
  instance or a plain dict. Rules: "archival" passes through unchanged if
  already set; "high" needs corroboration_count >= 2 and >= 2 distinct
  source_sectors; "medium" for same-sector corroboration (count >= 2, one
  sector) or a single high-reliability-sector source (count == 1); else
  "low". Not called automatically anywhere — summarize.py or a human can
  invoke it to cross-check/override the LLM's assignment.
- `Signal.confidence_source: str = "manual"` — new optional field marking
  whether `confidence` was hand-set (default) or produced by
  `derive_confidence()` ("derived"). `CONFIDENCE_SOURCE_VALUES = ["manual",
  "derived"]`.
- `validate_report()` now checks `confidence_source` per signal if present,
  defaulting to `"manual"` for old reports — backward compatible.

## Verification

- `python -m py_compile src/*.py` — passes.
- Ad hoc script constructing `Signal`s for all four tiers (high, medium via
  same-sector, medium via high-reliability single source, low, plus an
  archival-passthrough case and a dict-input case) — all assertions pass.
- All three existing reports in `data/reports/` (`2026-05-07.json`,
  `2026-07-06.json`, `2026-07-13.json`) still pass `validate_report()`
  unchanged, confirming the new optional `confidence_source` field doesn't
  break old data.

## Not done (by design, per task scope)

- `save_report()` does not call `derive_confidence()` automatically.
- `summarize.py`'s prompt is untouched — wiring the derived value in as a
  cross-check is left for a future run.
