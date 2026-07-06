# revision_history implementation

Implemented the design in `retention-versioning-design.md`, scoped only to
`src/report_schema.py`.

## Changes

- `Report.revision_history: list = field(default_factory=list)` added —
  each entry is `{previous_content_hash, corrected_at, reason}`.
- `save_report(data, validate=True, revision_reason=None, corrected_at=None)`
  now, before writing: loads any existing report file for `data["report_date"]`,
  and if its `content_hash` differs from the newly computed one, requires
  both `revision_reason` (non-empty str) and `corrected_at` (non-empty ISO
  date string, caller-supplied — no `datetime.now()` call, keeping this
  deterministic/testable) or raises `SchemaValidationError`. On a valid
  correction, appends `{previous_content_hash: <old hash>, corrected_at,
  reason: revision_reason}` to `revision_history` before computing/writing
  the new `content_hash`. First save for a date (no existing file) needs
  neither param and gets `revision_history: []`. Re-saving identical content
  (same hash) is a no-op for history and just carries forward the existing
  `revision_history`.
- `validate_report()` extended: `revision_history` is optional (defaults to
  `[]` for old reports), validated as a list of dicts each requiring
  `previous_content_hash` (64-char hex sha256), non-empty `corrected_at`
  string, and non-empty `reason` string.

## Verification

- `python -m py_compile src/*.py` — passed.
- Scratch script (removed after use): created a report, saved it (empty
  `revision_history`), modified `top_signals`, then called `save_report()`
  again — without `revision_reason`/`corrected_at` it correctly raised
  `SchemaValidationError` in both cases; with both supplied it succeeded and
  recorded one `revision_history` entry with the old content_hash, and
  `validate_report()` accepted the result.
- Confirmed all 4 existing reports in `data/reports/` (`2026-05-07`,
  `2026-07-06`, `2026-07-13`, `2026-07-20`) still `validate_report()` cleanly
  with `revision_history` defaulting to `[]` — no data files were modified.

No other files touched; `save_report()` call sites in `summarize.py`/CLI
etc. are unchanged (existing calls without the new kwargs behave exactly as
before for first-time saves).
