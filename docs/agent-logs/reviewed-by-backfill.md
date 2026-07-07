# reviewed_by provenance backfill

`review_status`/`reviewed_by` were added to `Report` (see
`docs/agent-logs/review-status-field.md`) but every existing report had
`reviewed_by=""` — a placeholder, not real metadata. Backfilled honest
provenance strings for the 7 reports not being touched by the concurrent
dormancy close-out agent (left `2026-07-20.json` and `2026-08-24.json`
untouched):

- `2026-05-07.json` -> `hand-authored-placeholder-run0` (per
  `docs/changelog-entries/run-00-branch-setup.md`: a placeholder written
  before the schema even existed).
- `2026-07-06.json` -> `hand-authored-example-run1` (per
  `docs/agent-logs/data-pipeline.md`: hand-crafted schema-exercise example,
  not WebSearch or crawl output).
- `2026-07-13.json` -> `websearch-run-plus-manual-sample-worldcup-jersey`
  (base report via WebSearch per `docs/agent-logs/real-report-2026-07-13.md`,
  plus one manually-sampled Pinterest signal appended per
  `docs/agent-logs/manual-sample-exercised.md`).
- `2026-07-27.json`, `2026-08-03.json`, `2026-08-10.json`, `2026-08-17.json`
  -> `websearch-run-thin-week` (each a WebSearch-researched, honestly-labeled
  `collection_status: thin` report, per their respective
  `docs/agent-logs/real-report-*.md` logs).

Each update went through `save_report()` with
`revision_reason="backfill reviewed_by provenance metadata"` and
`corrected_at="2026-07-06"`, so each file's `revision_history` now records
this as a correction rather than silently rewriting `reviewed_by` in place.

**Verification:** `python -m py_compile src/*.py` passed. `python
src/validate_all_reports.py` -> "OK: all 8 report(s) ... passed schema
validation" (the concurrent agent's 9th report, `2026-08-24.json`, had not
landed yet at verification time — count will move to 9 once it does, per
instructions). No commit made.
