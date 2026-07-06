# Schema: corroboration count + content hash

Implemented recommendations #1 and #3 from `docs/agent-logs/journalism-research.md`.
Only `src/report_schema.py` touched.

## Changes

1. **`Signal.source_corroboration_count: int = 1`** — number of independent
   sources reporting the signal. Defaults to 1 (single-source/unconfirmed),
   per AP/Reuters attribution norms distinguishing single-source vs
   corroborated claims. `validate_report()` requires it to be an int >= 1
   when present, but treats it as 1 if absent — old reports still validate.

2. **`Report.content_hash: str = ""`** — sha256 hex digest of the report's
   `top_signals` (canonical, sort-key JSON encoding, so ordering doesn't
   change the hash). Computed by a new `compute_content_hash(data)` helper
   and populated automatically inside `save_report()` before validation, so
   every freshly saved report is self-checksummed at write time (DPC/NDSA
   fixity guidance). `validate_report()` only checks the field's shape
   (64-char lowercase hex) when it's present/non-empty — reports without a
   `content_hash` still validate, so old example reports in `data/reports/`
   are unaffected until re-saved.

## Backward compatibility

Both fields are optional with safe defaults. `validate_report()` was
extended, not tightened: existing reports missing either field pass
unchanged. New/re-saved reports get a real corroboration count (still
1 unless the caller sets it) and a real content hash.

## Verification

- `python -m py_compile src/*.py` — passed.
- Ad hoc script: built a `Signal` with `source_corroboration_count=2`,
  wrapped in a `Report`, called `save_report()`, then `load_report()` +
  `validate_report()` on the result — succeeded, hash was a valid 64-char
  hex string. Then stripped both new fields from the loaded dict to
  simulate an old-format report and re-ran `validate_report()` — passed
  (backward-compat confirmed). Temp file removed after the test; no
  reports in `data/reports/` were modified.

Did not touch `summarize.py` — not strictly necessary for these two fields.
