# Full-archive coherence review (23 reports, 2026-05-07 through 2026-11-30)

Read all `top_signals` arrays across all 23 dated reports in `data/reports/`. No fixes were
made — the archive holds together well across its full span, not just adjacent windows.

## (a) signal_id continuity — checked, no collisions found

Traced every recurring concept's signal_id across non-adjacent reports:
- `sheer-layering` / `soft-tailoring`: same id 2026-05-07 -> 2026-07-06 -> 2026-08-03
  (dormancy check), never re-slugged.
- `off-duty-varsity`: same id across 2026-07-13, 07-20, 07-27 despite three different
  framings ("summer uniform" -> "checked at World Cup close" -> "post-tournament check").
- `layered-tops-styling`, `peplum-waist-revival` (3 consecutive windows), `lfw-eligibility-
  wholesale-requirement-dropped` (4 windows), `versace-mulier-debut-timing-unconfirmed`,
  `armani-post-founder-transition-continues`, `cfda-vogue-fashion-fund-2026-winner` (6
  windows), `back-to-school-2026-y2k-preppy`: all stable single ids tracked to closure.
- Deliberate *new* ids for genuinely different facts, correctly not collapsed into an
  existing id: `nyfw-ss27-schedule-finalization` (planning) -> `nyfw-ss27-week-underway`
  (execution) -> `nyfw-ss27-close` (concluded) — each report's `index_note` explicitly
  states "resolves signal_id X" when retiring the prior one. Same pattern for
  `cfda-vogue-fashion-fund-2026-finalists` (09-07, announcement of finalists) vs.
  `-winner` (10-26 onward, a different fact) — correctly distinct ids, not a collision.
- No case found of the same underlying concept given two different slugs without an
  acknowledged handoff.

## (b) cross-report factual contradictions — none found

Checked the multi-window threads most likely to drift (NYFW/LFW/MFW/PFW schedule facts,
Versace/Armani succession timing, DVF/Zankov). Every report that revises or supersedes a
prior claim does so explicitly via `index_note` and/or `limitations` (e.g. 2026-09-21's
"NYFW SS27 concludes..." entry explicitly resolves the two items 2026-09-14 flagged as
"pending" — Thom Browne's closing show and Sabyasachi's debut — rather than silently
restating or contradicting them). Versace/Armani timing evolves (unconfirmed ->
confirmed/delayed) consistently across 2026-09-28 and 2026-10-05 with no reversal.

## (c) archive health at scale

- `python src/validate_all_reports.py`: **OK, all 23 reports pass schema validation.**
- `python src/check_field_coverage.py`: **0 warnings** — all 34 Report/Signal fields are
  either typed+rendered or intentionally backend-only (`confidence_source`, `content_hash`).
- `python src/audit_confidence.py`: 32 assigned-vs-derived mismatches across 61 signals,
  all in the conservative direction (assigned lower than the formula would derive) — e.g.
  single-sector corroboration, "unconfirmed"/"pending" signals, or explicit editorial-
  integrity flags. This is a non-blocking, non-CI script by design, and every mismatch
  matches a documented rationale in that signal's own `index_note`/`human_editor_note`,
  not an unexplained drift.
- `python -m py_compile src/*.py`: compiles clean.

**Conclusion:** no corrective `save_report()` calls were needed this run.
