# Pipeline wiring fix — run.sh

Fixed the known-stale `src/run.sh`, which ran `crawler.py -> test_tools.py ->
server.py` and never produced a saved dated report.

## What changed

- `src/run.sh` now runs `crawler.py` then `summarize.py`. Classification is
  not a separate shell step — `summarize.py` already calls
  `taxonomy.classify_source()` per page while building the Claude prompt and
  again in `compute_sector_breakdown()`, so crawl -> summarize covers
  crawl -> classify -> summarize -> save in two commands.
- Dropped the `test_tools.py` step (it tests the old raw-cache pipeline per
  the skill doc, unrelated to producing a report) and the `server.py` step
  (that's a long-running MCP server, not part of a one-shot report-generation
  pipeline; running it after summarize would block and never exit).
- Added `set -e` so the script stops on the first failure instead of
  continuing to a broken next stage.
- Checked `summarize.py`: it already has a working
  `if __name__ == "__main__": summarize()` entry point, so no changes were
  needed there — the "add a CLI entry point" fallback in the task instructions
  wasn't necessary.

## Verified

- `python -m py_compile src/*.py` — passes, no syntax errors.
- Read through `summarize.py` and `report_schema.py` to confirm `summarize()`
  loads `trends_raw.json` (written by `crawler.py`), classifies sources,
  calls Claude, fills in `source_sector_breakdown`, and calls
  `save_report()`, which validates against the schema and writes
  `data/reports/<date>.json`. Did not execute a live crawl (requires network
  + API key).

## Files touched

- `src/run.sh` only. No changes to `crawler.py`, `taxonomy.py`,
  `report_schema.py`, `summarize.py`, `server.py`, or `test_tools.py`.
