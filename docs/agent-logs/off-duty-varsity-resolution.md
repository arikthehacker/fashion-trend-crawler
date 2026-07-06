# off-duty-varsity resolution

Used `get_signal_status_history("off-duty-varsity", all_reports)` across all 7 reports
(`list_report_dates()`): trend is `flash` (07-13, low) -> `declining` (07-20, low) ->
`declining` (07-27, low), then absent from 08-03 and 08-10 entirely. Three-plus weeks
of silence after a signal that was explicitly tied to the 2026 FIFA World Cup (ended
July 19) confirms the event-driven-noise reading the prior reports flagged but never
closed.

**Correction note on scope:** the task premise ("only mentioned in limitations text
after 07-20") doesn't fully hold — `off-duty-varsity` is a full `top_signals` entry in
both 2026-07-13.json and 2026-07-27.json, not just 2026-07-20.json. Per explicit
instruction, only `2026-07-20.json` was touched; the 07-13 and 07-27 entries were left
as-is since they're historical snapshots of the signal's state at the time, not the
final call.

**Change made to `data/reports/2026-07-20.json`:**
- `volatility` was already `"declining"` (set correctly in the original report) — no
  change needed there.
- Appended an "EDITORIAL CLOSE-OUT (2026-08-10)" note to the `human_editor_note`,
  explicitly declaring the signal resolved/closed, citing the World Cup end date and
  the 3-window silence, and instructing future reports not to re-flag `off-duty-varsity`
  absent new evidence.
- Recomputed `content_hash` via `save_report()` with `revision_reason` explaining the
  close-out and `corrected_at: "2026-08-10"`; a new `revision_history` entry was
  appended (this report already had one prior revision from 2026-07-06).

**Verification:** `python -m py_compile src/*.py` clean; `python
src/validate_all_reports.py` — all 7 reports pass.
