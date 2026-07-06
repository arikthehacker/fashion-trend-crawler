# Migration step 1 — crawler.py output path constant

This is **step 1 of 5** from `docs/agent-logs/legacy-migration-plan.md`
(retiring `trends_raw.json`/`trends_summary.json`). Only `src/crawler.py`
was touched, as scoped.

## What changed
`crawl_all_sources()` already took an `output_file` parameter defaulting to
the literal `"trends_raw.json"`. Per the plan, that signature stays as-is
(no rename, no behavior change). What was added: a module-level
`DEFAULT_OUTPUT_FILE = "trends_raw.json"` constant, and the function default
now reads `output_file=DEFAULT_OUTPUT_FILE` instead of the inline string
literal. This gives later steps (summarize.py, server.py) one named constant
to import/reference instead of each hardcoding the string independently —
without changing any actual runtime path or default today.

## Verification
- `python -m py_compile src/*.py` — passed, no errors.
- Re-read `summarize.py`, `server.py`, `test_tools.py`: none call
  `crawl_all_sources` with an explicit `output_file` override except
  `server.py:36`, which passes the literal `"trends_raw.json"` — identical
  to the new constant's value, so behavior is unchanged there too.
  `summarize.py`'s `load_trends()` and `test_tools.py`'s `CACHE_FILE` still
  independently hardcode `"trends_raw.json"` (untouched, as instructed —
  those are step 2 and step 4 respectively).

## Next: step 2
Per the plan, step 2 changes `summarize.py`: parameterize `load_trends()`
to accept a `path` argument (default `"trends_raw.json"` for CLI
compatibility), and/or add an optional `pages` argument to `summarize()` so
a future orchestrator can pass already-crawled data in-memory, skipping the
JSON round-trip. Not done in this pass — reserved for a future run per
scope instructions.
