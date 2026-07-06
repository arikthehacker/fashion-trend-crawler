# Pipeline rerun / collision handling — design proposal

## Current behavior (confirmed by reading code)

`report_schema.save_report()` (src/report_schema.py) has no collision check at
all: it computes `content_hash`, optionally validates, then unconditionally
`open(path, "w")`s over `data/reports/<report_date>.json`. `summarize.py`'s
`summarize()` always derives `report_date = date.today()` and calls
`save_report(report)` with no date override or confirmation step. Net effect:
rerunning the pipeline on a date that already has a report **silently
overwrites it**, with no error, prompt, or record that a prior version
existed. This was observed directly in `docs/agent-logs/live-crawl-attempt.md`
— a live-crawl run clobbered a hand-authored 2026-07-06 report; the overwrite
had to be reverted via `git checkout` after the fact.

## Options

- **(a) Hard error + `--force`**: safest, but blocks legitimate same-day
  reruns (e.g. fixing a truncated-JSON failure like the max_tokens bug) with
  no path to keep both the failed context and a record of the retry.
- **(b) Auto-suffix (`-v2.json`)**: never blocks, but fragments one date
  across multiple files, breaking `list_report_dates()`/`report_path()`'s
  one-file-per-date assumption and complicating archive/timeline pages.
- **(c) Require `revision_history` with a mandatory reason**: keeps one
  canonical file per date (preserving the archive model) while making every
  overwrite an auditable event instead of a silent one.

## Recommendation: (c), gated by a hard stop, not a flag

When `save_report()` detects an existing file for `report_date` whose
`content_hash` differs from the incoming data, it should refuse to write
unless the caller supplies a non-empty correction reason, which it then
appends to `revision_history` (previous_content_hash, corrected_at, reason)
before saving. No reason -> raise, don't silently version or silently
overwrite. This directly extends two principles already established in this
project's own research: the DPC/NDSA fixity work that motivated
`content_hash` in the first place (an overwrite that isn't checksummed and
logged is exactly the failure mode fixity checking exists to catch), and the
Corrections-section transparency work's premise that corrections must be
visible and reasoned, not silent. (b)'s multi-file-per-date model would
undercut both by making "which file is authoritative" ambiguous; a bare
`--force` flag under (a) permits the exact silent, reasonless overwrite this
incident revealed.

This depends on `revision_history` landing in `report_schema.py` first (owned
by another agent concurrently) — not implemented here.
