# Migration step 3 — server.py constant reference

This is **step 3 of 5** from `docs/agent-logs/legacy-migration-plan.md`
(retiring `trends_raw.json`/`trends_summary.json`). Only `src/server.py` was
touched, as scoped. Per updated instructions, this pass did the narrow,
lowest-risk version of step 3: replace the hardcoded `"trends_raw.json"`
string literal with the `DEFAULT_OUTPUT_FILE` constant imported from
`crawler.py`, and nothing else. The plan's original step 3 (repointing reads
to `data/cache/latest.json` with a fallback) was intentionally NOT done here
— that's more invasive and out of scope for this pass.

## What changed
- Added `DEFAULT_OUTPUT_FILE` to the `from crawler import ...` line.
- `crawl_fashion_trends` (line 36): `output_file="trends_raw.json"` ->
  `output_file=DEFAULT_OUTPUT_FILE`.
- `get_cached_trends` (lines 45, 48): both `"trends_raw.json"` references ->
  `DEFAULT_OUTPUT_FILE`.
- `search_trends` (lines 57, 60): both `"trends_raw.json"` references ->
  `DEFAULT_OUTPUT_FILE`.
- No function names, parameter names, docstrings, or return shapes changed.
  `list_reports`/`get_report` untouched.

## Verification
- `python -m py_compile src/*.py` — passed, no errors.
- `DEFAULT_OUTPUT_FILE` in `crawler.py` is defined as the literal
  `"trends_raw.json"` — same value as what was previously hardcoded in
  `server.py`, so this is a pure refactor (single source of truth), zero
  runtime behavior change.
- Manually traced all three functions:
  - `crawl_fashion_trends`: still calls `crawl_all_sources(sources,
    output_file="trends_raw.json")` (via the constant), writing the same file
    in the same format as before.
  - `get_cached_trends`: still checks existence of and reads raw text from
    `trends_raw.json` (via the constant), same error JSON on missing file.
  - `search_trends`: still checks existence of, `json.load`s, and searches
    `trends_raw.json` (via the constant), same match/return shape.

## Next: step 4
Per the plan, step 4 addresses `test_tools.py`, whose `CACHE_FILE =
"trends_raw.json"` (line 16) drives its whole suite. Since this step did not
change what `get_cached_trends`/`search_trends` actually read from (still
`trends_raw.json`, just via a named constant), `test_tools.py` is not yet
stale — but a human decision is still needed before the plan's original step
3 (repointing to `data/cache/latest.json`) is later attempted: whether to
rewrite `CACHE_FILE` to track the new cache path at that time, or retire the
file in favor of tests against `report_schema.py`/`data/reports/`. Not
decided or touched in this pass.
