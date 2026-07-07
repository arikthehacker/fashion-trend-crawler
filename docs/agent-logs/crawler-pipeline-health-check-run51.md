# Crawler pipeline health check — run 51

Scope: verify `crawler.py` still works end-to-end against the current live
`FASHION_SOURCES` list, and check whether existing report metadata overclaims
what `sources_scanned`/`items_collected` actually measure. No process-gap
"fix" attempted — that decision (named in
`docs/agent-logs/gap-analysis-50-report-milestone-run50.md`) stays with the
user.

## 1. Real crawler run

`python src/crawler.py` executed directly (no summarize.py, no report
generated). `src/crawler.py`'s `FASHION_SOURCES` currently has **12** entries
(list has shrunk since the "40/46" figure cited in the task — several
geographic-diversity additions/removals happened across runs 17-41; 12 is
the present count, confirmed by reading the list in code).

Result: **12/12 sources returned real content**, no source came back empty
or errored. 108 pages crawled (depth 0-1), 454 headline strings extracted,
saved to `trends_raw.json` (deleted after inspection — not a deliverable).
Two URLs were correctly skipped as `[blocked by robots.txt]`
(`vogue.com/search`, `vogue.mx/search`) — expected, not a failure, the
crawler is respecting robots.txt as designed.

Conclusion: the crawler infrastructure itself is healthy right now. The gap
identified in run 50 is not "the crawler is broken" — it demonstrably still
works — it's that reports are authored via WebSearch instead of by invoking
this working pipeline.

## 2. Metadata provenance check

Checked `sources_scanned`/`items_collected` field definitions
(`src/report_schema.py`) and their only rendering site
(`web/app/reports/[date]/page.tsx:227-228`, labeled "Sources scanned: N" /
"Items collected: N" verbatim, no caveat). Also checked
`web/app/methodology/page.tsx`'s "AI Involvement" section, which stated
plainly: "AI assists with crawling source material... and drafting
summaries" — read straight, this implies the automated crawler produced the
scan counts shown on report pages. Per run 50's finding, that's true for
only 2 of ~43 reports; the rest are WebSearch-based counts of sources
reviewed, not live-crawled pages, but the site draws no distinction.

This is a real overclaim, same category as the `reviewed_by` self-attribution
issue already disclosed at methodology page line 104. Fixed narrowly:
added one clarifying sentence to `web/app/methodology/page.tsx`'s "AI
Involvement" section stating that most collection windows to date have used
AI-directed research rather than the automated `crawler.py` fetching live
pages, and that "sources scanned"/"items collected" counts reflect sources
reviewed either way, not exclusively a live-crawl count. No historical
report JSON content was touched — only the site's own description of what
the field means.

## Verification

`python -m py_compile src/*.py` — passes, no errors.

## Not done (explicitly out of scope)

- Did not run `summarize.py` or generate/save a new dated report.
- Did not change any `data/reports/*.json` file's substantive content.
- Did not decide the underlying process question (real crawls on cadence vs.
  disclosed WebSearch methodology) — that's the user's call per run 50.
