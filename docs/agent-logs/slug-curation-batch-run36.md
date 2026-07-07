# Slug curation batch (run 36)

Follow-up to run 35's flagged list of 12 overly-long `signal_id`s. Confirmed
first that `web/app/signals/[slug]/page.tsx` uses `generateStaticParams()` +
`getAllSignalSlugs()`/`getSignalHistory(slug)` (data-driven), and
`web/app/timeline/page.tsx` links via `entry.signal_id` — no hardcoded slugs
anywhere. Renaming in the JSON data is safe.

Checked `report_schema.py`: `signal_id` only lives in `top_signals[].signal_id`
(no separate cross-reference field), so each rename only needed a single-field
swap per occurrence. Used `save_report(revision_reason=..., corrected_at=
"2026-07-06")` for every touched file — no hand-editing. `data/reports/2027-01-11.json`
was excluded (being written by another concurrent agent).

## Renames applied (same new slug used everywhere the old one recurred)

| old | new |
|---|---|
| `lfw-eligibility-wholesale-requirement-dropped` | `lfw-wholesale-eligibility-dropped` |
| `pfw-ss27-schedule-date-inconsistency` | `pfw-schedule-inconsistency` |
| `versace-mulier-debut-timing-unconfirmed` | `versace-mulier-debut-unconfirmed` |
| `armani-post-founder-transition-continues` | `armani-founder-transition` |
| `cfda-vogue-fashion-fund-2026-winner` | `cfda-fashion-fund-winner` |
| `cfda-vogue-fashion-fund-2026-finalists` | `cfda-fashion-fund-finalists` |
| `nyfw-ss27-trend-forecast-content-integrity-flag` | `nyfw-forecast-integrity-flag` |
| `mfw-ss27-schedule-date-inconsistency` | `mfw-schedule-inconsistency` |
| `back-to-school-2026-y2k-preppy` | `school-y2k-preppy` |
| `2026-black-friday-cyber-monday-outcome` | `bfcm-outcome` |
| `2026-black-friday-early-retail-calendar` | `bfcm-retail-calendar` |
| `pantone-fall-2026-devil-wears-prada-tie-in` | `pantone-prada-tie-in` |

All 12 candidates from run 35 were completed (including the recurring
`cfda-vogue-fashion-fund-2026-winner`, which spans 7+ reports and is subject
to the "prolonged silence" FACTUAL-question convention — its identity/history
is preserved, only the slug string changed).

Pre-rename collision check confirmed none of the 12 new slugs already existed
elsewhere in `data/reports/`.

## Files touched

19 report files got a new `revision_history` entry and updated
`top_signals[].signal_id`: 2026-08-31, 09-07, 09-14, 09-21, 09-28, 10-05,
10-12, 10-19, 10-26, 11-02, 11-09, 11-16, 11-23, 11-30, 12-07, 12-14, 12-21,
12-28, and 2027-01-04.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 28 reports pass
- `cd web && npx tsc --noEmit && npx next build` — OK; build output confirms
  `/signals/cfda-fashion-fund-winner` and other renamed slugs generate
  correctly under `generateStaticParams()`.

No commits made, per instructions.
