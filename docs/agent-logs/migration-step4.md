# Migration step 4 — test_tools.py constant reference

This is **step 4 of 5** from `docs/agent-logs/legacy-migration-plan.md`
(retiring `trends_raw.json`/`trends_summary.json`). Only `src/test_tools.py`
was touched, as scoped. Following the same narrow, lowest-risk pattern as
step 3: replaced the hardcoded `"trends_raw.json"` string literal with the
`DEFAULT_OUTPUT_FILE` constant imported from `crawler.py`. No test logic,
assertions, or behavior changed — purely the constant reference.

## What changed
- Added `from crawler import DEFAULT_OUTPUT_FILE`.
- `CACHE_FILE = "trends_raw.json"` -> `CACHE_FILE = DEFAULT_OUTPUT_FILE`.
- Nothing else in the file was modified.

## Verification
- `python -m py_compile src/*.py` — passed, no errors.
- Ran `python src/test_tools.py` standalone from the `src/` directory (it
  needs no MCP server or network — it just reads the cache JSON file
  directly). All 9/9 tests passed:
  cache file exists, cache is not empty, all entries have required fields,
  titles are strings, keyword search returns results, search results have
  correct shape, fake-keyword search returns nothing, depth values valid,
  urls start with http.
- Note: running the script raised a `UnicodeEncodeError` on Windows
  (cp1252 console encoding can't print the decorative unicode heart
  characters in the banner text) unless `PYTHONIOENCODING=utf-8` is set.
  This is a pre-existing issue unrelated to this change (same literal
  banner string existed before this edit) and was not touched, per scope.

## Next: step 5
`crawler.py` is now the single source of truth for the cache filename —
`server.py` (step 3) and `test_tools.py` (this step) both import
`DEFAULT_OUTPUT_FILE` rather than hardcoding `"trends_raw.json"`. No file in
`src/` still hardcodes the literal string for this purpose. Step 5 (deleting
the legacy `trends_raw.json`/`trends_summary.json` files at repo root and in
`src/`, and removing the Step 3 compatibility fallback paths) is unblocked,
pending one final verification pass: a full `crawler.py` -> `summarize.py`
pipeline run with the legacy files absent beforehand, confirming no
`FileNotFoundError`, followed by re-running `test_tools.py` and the Step 3
MCP server smoke test.
