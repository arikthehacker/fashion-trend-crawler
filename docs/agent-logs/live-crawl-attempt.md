# Live crawl attempt — 2026-07-06

## Result: the pipeline works end to end

Ran `python src/crawler.py` then `python src/summarize.py` from a clean checkout,
using only credentials already present in the environment (root `.env` has
`ANTHROPIC_API_KEY`; `python-dotenv`, `requests`, `beautifulsoup4`, `anthropic` all
already installed). No network blocks encountered — Vogue, Who What Wear, and
Hypebeast were all reachable.

**Crawl**: 30 pages crawled across the 3 default `FASHION_SOURCES` (one
`vogue.com/search` URL was correctly skipped, blocked by robots.txt). Real
`trends_raw.json` produced, 119 headlines collected.

**Summarize**: first attempt failed — `json.decoder.JSONDecodeError: Unterminated
string` at `summarize.py:149`. Root cause: `max_tokens=2000` in the
`client.messages.create` call (`summarize.py:141`) is too small for the JSON
response shape once `top_signals` has more than 1-2 entries with real headline
volume; Claude's response was cut off mid-string. Bumped `max_tokens` to 4000
locally to confirm the theory — second run succeeded, produced a genuine,
schema-valid report (`sources_scanned: 30`, `items_collected: 119`,
`collection_status: "thin"`, real executive summary referencing Vogue/Hypebeast/Who
What Wear coverage). This fix was **not committed** — `summarize.py` was reverted
to its original `max_tokens=2000` afterward, per instructions not to leave working-tree
changes from this exploration. The bug is real and worth fixing for the next
run (recommend `max_tokens=4000` or higher).

**Collision found**: `data/reports/2026-07-06.json` already existed (hand-authored,
14 sources/31 items) since `report_date` defaults to `date.today()` and today is
2026-07-06. Running `summarize.py` for real silently overwrote it. That overwrite
was reverted via `git checkout`; the genuine live-crawl output was preserved
separately at `docs/agent-logs/live-crawl-2026-07-06-real-output.json` instead of
being placed in `data/reports/` under the same name, to avoid clobbering existing
curated data without a human decision. It passed `validate_all_reports.py` when
tested in `data/reports/`.

**Also confirmed harmless**: an em-dash appeared as `�` when `print()`'d to the
Windows terminal (cp1252 console) but is correctly stored as `—` in the
UTF-8 JSON file — not a data bug, just a console-encoding display artifact.

## What's needed to make this reliably reproducible for real runs

1. Fix `max_tokens` in `summarize.py` (2000 -> at least 4000) so responses aren't
   truncated once headline volume is realistic.
2. Decide a collision policy for `summarize.py`/`save_report()` when a report for
   `date.today()` already exists — currently it silently overwrites. Should
   probably error, version, or require `--force`.
3. No credentials were created or embedded for this test — the existing root
   `.env` `ANTHROPIC_API_KEY` was used as-is and was sufficient.
