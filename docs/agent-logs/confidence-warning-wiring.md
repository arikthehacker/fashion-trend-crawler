# Confidence warning wiring in validate_all_reports.py

Per `docs/agent-logs/confidence-audit.md` recommendation #1: wired
`derive_confidence()` into `src/validate_all_reports.py` as a **non-blocking**
validation warning, not auto-adoption or a hard failure.

## What changed

- `src/validate_all_reports.py`: after schema validation passes for a report,
  it now calls a new `find_high_confidence_warnings(report_date, data)`
  helper (imports `derive_confidence` from `report_schema.py` — reuses the
  same formula `audit_confidence.py` uses, no logic duplicated). It flags
  only the one pattern the audit called genuinely concerning: assigned
  `confidence == "high"` but `derive_confidence()` returns `"medium"` or
  `"low"`. Matches print as clearly labeled `WARNING:` lines after the `OK:`
  message. Schema failures still return exit code 1 and skip the confidence
  check for that report; warnings alone never change the exit code (still 0).
- `.github/workflows/validate-reports.yml`: renamed the validate step to
  "Validate reports against report_schema.py (schema errors block;
  confidence mismatches print as non-blocking warnings)" to reflect the new
  behavior. No new steps added — same script call.

## Deliberately not done

Per audit recommendation #2, did not wire the reverse case (formula says
higher than assigned) — those downgrades are defensible editorial judgment,
not auto-corrected or warned on.

## Verification

`python src/validate_all_reports.py` → `OK: all 4 report(s) ... passed schema
validation.`, exit code 0. No warnings printed against current data — the
one known "Resale/secondhand retail growth" mismatch in
`data/reports/2026-07-13.json` (being resolved concurrently by another
agent) is either fixed or unaffected pending that file's edit; did not touch
that file. Confirmed the warning logic itself fires correctly via an
isolated in-memory fixture calling `find_high_confidence_warnings` directly.

Files touched: `src/validate_all_reports.py`,
`.github/workflows/validate-reports.yml`. `src/audit_confidence.py`
untouched, per scope.
