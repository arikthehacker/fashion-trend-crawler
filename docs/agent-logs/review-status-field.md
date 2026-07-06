# review_status / reviewed_by fields

Gap identified in `docs/agent-logs/ai-journalism-standards-research.md`: no
auditable per-report review record and no draft-vs-published status
distinction.

Added to `Report` in `src/report_schema.py`:

- `review_status: str = "reviewed"` — one of `"draft"` / `"reviewed"`
  (`REVIEW_STATUS_VALUES`). Defaults to `"reviewed"` because every report
  saved before this field existed already went through the loop's
  consolidation process, so treating them as unreviewed would be a false
  regression, not a more honest label.
- `reviewed_by: str = ""` — free-text provenance (e.g.
  `"loop-consolidation"` or a human name).

## Design choice: soft metadata, not a hard gate

This is deliberately a **soft** field. `validate_report()` only checks that
`review_status` is in vocabulary and `reviewed_by` is a string — it does not
require `reviewed_by` to be non-empty, and does not block `save_report()` on
`review_status == "draft"`.

That's intentional, not an oversight: this project already has
`human_editor_note` serving as the substantive, enforced review record (it's
the field that actually carries editorial judgment and is treated as a hard
gate elsewhere). Making `reviewed_by` a second required field would just
create a parallel, easily-desynced way of asserting "this was reviewed"
without adding real signal — the same anti-pattern already avoided for
`signal_status`/volatility (see `get_signal_status_history` docstring).
`review_status`/`reviewed_by` exist purely so a report can be marked
`"draft"` while still being saved/inspected, and so tooling can later query
"who/what last touched this" without over-constraining today's callers.

Both fields are optional and backward compatible: old reports without them
validate and default to `review_status="reviewed"`, `reviewed_by=""`.
Verified via `python -m py_compile src/*.py` and
`python src/validate_all_reports.py` (8/8 reports still pass).
