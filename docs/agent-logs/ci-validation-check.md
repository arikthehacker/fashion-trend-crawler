# CI validation check (TODO.md run-4 item 1)

Added `src/validate_all_reports.py`: a standalone script that imports
`report_schema.py`, calls `list_report_dates()` to enumerate
`data/reports/*.json`, loads each report, and runs `validate_report()`
on it. Any load/parse error or `SchemaValidationError` is collected
(not aborted on first failure) so a single run reports every bad
report at once, with the report's filename and the exact validation
error. Exits 0 if all reports pass, 1 if any fail. Runnable as
`python src/validate_all_reports.py` from the repo root or from
`src/`.

Repo had no `.github/workflows/` directory, so created
`.github/workflows/validate-reports.yml`: a minimal job on
push/pull_request that runs `python -m py_compile src/*.py` followed
by `python src/validate_all_reports.py` on Python 3.11/ubuntu-latest.

## Verification

- `python src/validate_all_reports.py` (from repo root) and from
  `src/` directly: both exit 0, "OK: all 3 report(s) ... passed
  schema validation" — confirms the three current reports (including
  `2026-05-07.json`, now fixed) are valid.
- `python -m py_compile src/*.py`: succeeds.
- Failure-mode test: loaded a real report into a scratch temp dir,
  corrupted one signal's `confidence` to an out-of-vocab value,
  monkeypatched `report_schema.REPORTS_DIR` to point at the temp dir,
  then called `validate_all_reports.main()`. Correctly returned exit
  code 1 with message: `2099-01-01.json: top_signals[0].confidence
  'totally-not-a-real-level' not in ['low', 'medium', 'high',
  'archival']`. No repo files were touched for this test.

Not committed per instructions — changes are: `src/validate_all_reports.py`,
`.github/workflows/validate-reports.yml`, this log file.
