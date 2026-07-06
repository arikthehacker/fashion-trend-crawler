# Signal ID backfill + fixity backfill

Only `src/report_schema.py` and `data/reports/*.json` touched.

## Changes

1. **`Signal.signal_id: str = ""`** added to `report_schema.py` — a
   URL-safe slug for cross-report recurrence tracking (see
   `docs/agent-logs/signals-timeline-design.md`). Optional/backward
   compatible: `validate_report()` only checks shape (lowercase
   alphanumeric + hyphens, no leading/trailing/double hyphen) when
   non-empty; reports without it still validate.

2. **Backfilled `signal_id` on all 12 signals across the 3 reports**,
   slugified from each signal's `name`. Used the same slug for verbatim
   recurring names: `sheer-layering` and `soft-tailoring` both appear
   in 2026-05-07 and 2026-07-06, now matchable for `/signals/[slug]`.

3. **Backfilled `source_corroboration_count` and `content_hash`** on
   the two older example reports (2026-05-07, 2026-07-06), which
   predate those fields. Corroboration counts set from the number of
   distinct `source_sectors` per signal (1 for social-only signals, up
   to 3 for multi-sector ones). `content_hash` computed via the
   existing `compute_content_hash()` over each file's `top_signals`.
   2026-07-13 already had these fields from a prior pass.

## Verification

- `python -m py_compile src/*.py` — passed.
- Script loading + validating all 3 reports: **2026-07-06** and
  **2026-07-13** pass. **2026-05-07** fails — but on a pre-existing,
  unrelated defect: `top_signals[0].volatility` is `"seasonal/recurring"`,
  which is not in `VOLATILITY_LABELS`. Confirmed via `git show HEAD:...`
  that this file failed validation *before* any of my edits too, so it's
  not a regression from this task and outside the touched-fields scope
  (I did not modify `volatility` values). Flagging for a follow-up fix,
  not corrected here since it's outside this task's file/field scope.
