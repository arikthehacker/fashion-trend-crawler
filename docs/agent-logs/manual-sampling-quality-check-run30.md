# Manual-sampling quality check (run 30)

Read all three manual-sampling exercise logs and cross-referenced them against
the actual stored JSON for the three manually-sampled signals: `off-duty-varsity`
(`data/reports/2026-07-13.json`, later carried into `2026-07-20.json`),
`poetcore-aesthetic` (`data/reports/2026-07-20.json`), and
`funmaxxing-maximalist-play-aesthetic` (`data/reports/2026-11-09.json`).

## Found: genuine drift, fixed

`src/manual_sample.py`'s `build_manual_signal()` only ever wrote the observer's
judgment into `index_note`. But `Signal` (in `src/report_schema.py`) had no
`human_editor_note` field at all, and the site (`web/app/reports/[date]/page.tsx`)
renders `index_note` ("Index note: ...") and `human_editor_note` ("Editor
review: ...") as two separate, both-optional fields — with `human_editor_note`
already established as a real convention across ~15+ existing report files.
Result: the first exercise (`off-duty-varsity`) got a `human_editor_note` key
only because someone manually patched it in after the fact (visible as a
literal duplicate of `index_note` in the JSON); the second and third exercises
(`poetcore-aesthetic`, `funmaxxing-maximalist-play-aesthetic`) never got one,
so their "Editor review" note silently never rendered on the live site despite
the workflow's own docs (template + `manual_sample.py`'s enforced-non-empty
rule) treating this as the required human-in-the-loop field. Same failure
pattern as the `human_editor_note`/`revision_history`/`thin_week_note`
"populated but never rendered" bugs from runs 21/23/24.

**Fix applied:**
- Added `human_editor_note: str = ""` to the `Signal` dataclass.
- `build_manual_signal()` now sets both `index_note` and `human_editor_note`.
- Backfilled the missing `human_editor_note` key on `poetcore-aesthetic` and
  `funmaxxing-maximalist-play-aesthetic` via `save_report(revision_reason=...,
  corrected_at="2026-07-06")` (recomputes `content_hash`, appends
  `revision_history`).

## Found: dormancy needing close-out

`get_signal_status_history()` showed `poetcore-aesthetic` appeared in exactly
one report (2026-07-20) and never again across 18 subsequent collection
windows (through 2026-11-30) — well past its own note's "re-check next
quarter." Added an `EDITORIAL CLOSE-OUT` note (same pattern as the existing
`off-duty-varsity`/`layered-tops-styling` close-outs) stating it's resolved,
no further re-checks needed.

`funmaxxing-maximalist-play-aesthetic` has appeared in only one window so far
(2026-11-09) with two later reports existing (2026-11-16, 2026-11-23) since —
too early to call dormant per the project's own precedent (3-4+ silent windows
before close-out); no action taken beyond the field backfill.

`off-duty-varsity` and `layered-tops-styling` were already correctly closed
out by a prior run — no changes needed there.

## Verification

`python -m py_compile src/*.py` — passed.
`python src/validate_all_reports.py` — `OK: all 23 report(s) ... passed schema
validation.`

No commit made (per instructions).
