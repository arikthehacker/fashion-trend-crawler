# Stale slug reference audit — run 38

Follow-up to run 37, which found and fixed 2 stale long-form slug
references (`versace-mulier-debut-timing-unconfirmed`,
`armani-post-founder-transition-continues`) after run 36's slug renaming.
Confirmed those 2 do not reappear anywhere in `data/reports/*.json`.

Grepped the raw text (not just `signal_id` fields) of every report for all
12 old long-form slugs from run 36's table. Found many more stale
references than run 37 caught — run 36's rename only updated the current
`signal_id` field per report; historical/narrative prose in later reports
that name-checked a signal by its old string was untouched.

## Stale references found and fixed (17 files)

- `back-to-school-2026-y2k-preppy` → `school-y2k-preppy`: 2026-09-07,
  2026-09-14
- `lfw-eligibility-wholesale-requirement-dropped` →
  `lfw-wholesale-eligibility-dropped`: 2026-09-28, 2026-10-05, 2026-10-12,
  2026-10-19, 2026-10-26, 2026-12-07
- `mfw-ss27-schedule-date-inconsistency` → `mfw-schedule-inconsistency`:
  2026-10-05, 2026-10-12
- `pfw-ss27-schedule-date-inconsistency` → `pfw-schedule-inconsistency`:
  2026-10-12
- `cfda-vogue-fashion-fund-2026-winner` → `cfda-fashion-fund-winner`:
  2026-11-02, 2026-11-09, 2026-11-16, 2026-11-23, 2026-11-30, 2026-12-07,
  2026-12-14, 2026-12-21, 2026-12-28, 2027-01-04

No stale references found for: `versace-mulier-debut-timing-unconfirmed`,
`armani-post-founder-transition-continues` (confirmed already fixed by run
37 and did not reappear), `cfda-vogue-fashion-fund-2026-finalists`,
`nyfw-ss27-trend-forecast-content-integrity-flag`,
`2026-black-friday-cyber-monday-outcome`,
`2026-black-friday-early-retail-calendar`,
`pantone-fall-2026-devil-wears-prada-tie-in`.

## Method

Every occurrence was a literal identifier mention inside sentences (e.g.
`"lfw-eligibility-wholesale-requirement-dropped (September 21) is
continuing-but-quiet..."`, `get_signal_status_history('cfda-vogue-fashion-fund-2026-winner',
...)`), so a straight string substitution of the old slug for the new one
reads naturally in every case — the surrounding sentence structure treats
the slug as a bare identifier, not as a rendered display name. Applied via
`save_report(revision_reason=..., corrected_at="2026-07-06")` per file, one
call per report, listing the specific old slug(s) fixed in that file's
revision reason.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 30 reports pass
- Re-grepped all 12 old slugs across `data/reports/*.json` after the fix:
  the only remaining matches are inside the new `revision_history[].reason`
  entries this run added (which name the old slug as documentation of what
  was fixed) — no stale references remain in `index_note`,
  `human_editor_note`, `executive_summary`, or `limitations` prose.

No commits made, per instructions.
