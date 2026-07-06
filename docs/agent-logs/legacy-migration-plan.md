# Migration plan: retire trends_raw.json / trends_summary.json

Confirmed external dependency: `.codex/config.toml` registers `server.py` as an
MCP server (`mcp_servers.fashion-trend-crawler`, launched via `python server.py`).
Tool names (`crawl_fashion_trends`, `get_cached_trends`, `search_trends`,
`list_reports`, `get_report`) are discovered live over MCP by whatever client
loads this config — there's no hardcoded tool schema checked into the repo, but
a running/connected client (Codex, Claude Desktop, etc.) may have cached tool
names or descriptions from a prior session. **Do not rename or remove any
existing `@mcp.tool()` function** in this migration; only change what they do
internally. Add new tools alongside if new capability is needed.

## Target end state
- `crawler.py` writes crawl output to a path passed in by the caller (or an
  in-memory return value), not a hardcoded `trends_raw.json` default.
- `summarize.py` consumes that same in-memory/parameterized data instead of
  re-opening `trends_raw.json` from disk.
- `server.py`'s cache-reading tools (`get_cached_trends`, `search_trends`) read
  from the newest file in `data/reports/` (or a new `data/cache/latest.json`)
  instead of root-level `trends_raw.json`.
- `test_tools.py` is retired or repointed (it explicitly tests "the OLD
  raw-cache pipeline" per the skill file — confirm with a human whether to
  delete it or rewrite it against the new cache path).

## Step 1 — crawler.py: make output path explicit, keep default for compat
- `crawl_all_sources(sources, output_file="trends_raw.json")` (line 144): keep
  the parameter and default as-is for now (do not touch). This function is
  called by `server.py:36` (`crawl_fashion_trends`) and by `run.sh`'s
  `python crawler.py` step, both passing no explicit `output_file`.
- Verify: `python -m py_compile src/crawler.py` (no behavior change yet, so no
  functional test needed at this step).

## Step 2 — summarize.py: accept in-memory pages instead of re-reading the file
- Change `load_trends()` (lines 31-34) to `load_trends(path="trends_raw.json")`
  so callers can pass a path, OR add a new `summarize(pages)` entry point that
  takes already-crawled data directly and skip `load_trends()` when called that
  way. Recommended: keep `load_trends(path=...)` for CLI use (`__main__` block,
  line 153-154) but have `summarize()` accept an optional `pages` argument
  (default `None` → falls back to `load_trends()`), so a future orchestrator
  (run.sh replacement or a combined `crawl_and_summarize()` in a new module)
  can call `pages = crawl_all_sources(...); summarize(pages=pages)` without any
  JSON file round-trip.
- Verify: run `python src/summarize.py` manually against an existing
  `trends_raw.json` and confirm a report is still written to
  `data/reports/<date>.json` with the same shape as before (compare against a
  file already in `data/reports/` using `report_schema.validate_report`).

## Step 3 — server.py: repoint cache-reading tools to a durable cache location
This is the riskiest step since these are the external MCP contracts.
- `crawl_fashion_trends` (lines 30-37): keep writing to `trends_raw.json` (via
  `crawl_all_sources`'s default) for one more release so `get_cached_trends`/
  `search_trends` keep working during transition. Optionally also copy/write
  to `data/cache/latest.json` as the new canonical cache location.
- `get_cached_trends` (lines 39-49) and `search_trends` (lines 51-79): change
  the hardcoded `"trends_raw.json"` path (lines 45, 48, 57, 60) to read from
  `data/cache/latest.json` (or whatever new path Step 1 settles on), with a
  fallback to `trends_raw.json` if the new file doesn't exist yet, so existing
  deployments don't break mid-migration.
- Do NOT rename `crawl_fashion_trends`, `get_cached_trends`, `search_trends`,
  `list_reports`, or `get_report` — these are the MCP tool identities a
  connected client may reference by name.
- Verify: with the MCP server not running, manually call each changed function
  from a Python REPL (`import server; server.get_cached_trends()`) against a
  test fixture file, confirming JSON shape is unchanged from before. Then start
  the server (`python src/server.py`) and confirm no startup errors, before
  wiring an actual MCP client to it.

## Step 4 — test_tools.py: decide fate before deleting anything
- `CACHE_FILE = "trends_raw.json"` (line 16) drives the whole file. Once Step 3
  changes what `get_cached_trends`/`search_trends` read from, this test suite
  is testing the old path, not the new one it will diverge silently (still
  "pass" against a stale `trends_raw.json` while server.py reads elsewhere).
  Human decision needed: rewrite `CACHE_FILE` to point at the new cache path,
  or delete this file and replace with tests against `report_schema.py` /
  `data/reports/`. Do not silently repoint it without flagging the choice.
- Verify: `python src/test_tools.py` passes against whichever file it's
  pointed at.

## Step 5 — only after Steps 1-4 are individually verified and running in
production for at least one real crawl+summarize cycle: delete the 4 legacy
files (`trends_raw.json`, `trends_summary.json` at repo root and in `src/`)
and remove the compatibility fallback paths added in Step 3.
- Verify: full pipeline run (`crawler.py` → `summarize.py`) with the legacy
  files absent from disk beforehand, confirm no `FileNotFoundError` anywhere,
  then run `test_tools.py` and the MCP server smoke test from Step 3 again.

## What could break, ranked by risk
1. **server.py's MCP tool contracts** (highest) — any connected MCP client
   (per `.codex/config.toml`) expects these 5 tool names and their JSON return
   shapes to keep working; a client session started before this migration may
   have cached the old behavior/description text and could get confused by a
   silent behavior change without a restart.
2. **run.sh** — already known stale (doesn't call `summarize.py`); don't let
   this migration further diverge run.sh from the real pipeline without a
   follow-up fix (separate task per the skill file).
3. **test_tools.py** — will pass/fail against the wrong file if not
   deliberately updated in Step 4.
4. **summarize.py's `load_trends()` file format assumption** — expects a list
   of `{"url", "depth", "titles"}` dicts; any new cache format must preserve
   this shape or `compute_sector_breakdown`/`build_prompt` (lines 37-58) need
   matching updates.
