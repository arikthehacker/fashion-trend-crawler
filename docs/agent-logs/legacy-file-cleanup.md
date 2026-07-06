# Legacy trends_raw.json / trends_summary.json cleanup — NOT DONE

Checked whether the 4 legacy files (`trends_raw.json`, `trends_summary.json` at repo
root and in `src/`) are safe to delete now that `run.sh` runs crawl -> summarize.
They are **not safe to delete** — left in place.

## Findings (grep of exact filenames across `src/`)

- `src/crawler.py:144` — `crawl_all_sources(sources, output_file="trends_raw.json")`,
  the default output path used by `run.sh`'s `python crawler.py` step. Still writes it.
- `src/summarize.py:33` — `summarize()` opens `trends_raw.json` directly by that literal
  path to build the Claude prompt. This is the file `run.sh` step 2 depends on.
- `src/server.py:36,45,48,57,60` — MCP tools `crawl_fashion_trends`,
  `get_cached_trends`, and `search_trends` all read/write `trends_raw.json` by the
  same literal path (not `trends_summary.json`).
- `src/test_tools.py:16` — `CACHE_FILE = "trends_raw.json"`, tests the old raw-cache
  pipeline against this exact file.
- `src/report_schema.py:7` — comment reference only, no read/write.

## Conclusion

`trends_raw.json` is not legacy — it is the live intermediate artifact the current
crawl -> summarize pipeline reads and writes, and `server.py`'s MCP tools depend on
it too. `trends_summary.json` has no current readers/writers found by grep, but since
`trends_raw.json` (its sibling file, same origin) is load-bearing, all 4 files were
left untouched rather than deleting a subset. No files were deleted.

## Next step for a future pass

If `trends_raw.json` is meant to be retired, `crawler.py`, `summarize.py`, and
`server.py` all need to be repointed to a new path/format first — this is a code
change, not a file-deletion task.
