# Periodic confidence + coverage audit — run 39

Ran across 31 reports (a 32nd, `2027-01-25.json`, landed mid-run from a
concurrent agent — included in the spot-check below).

## Confidence audit

`audit_confidence.py`: 77 signals checked, 44 mismatches, all still
assigned-lower-than-derived (editor conservatism), including the new
`2027-01-25.json` Wales Bonner / Paris menswear signals (assigned=medium,
derived=high). No `assigned=high, derived=low/medium` case found anywhere.
Nothing concerning; no fix needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Same clean
baseline as runs 25/32/37 (`confidence_source` remains the one
intentionally backend-only field, called out in the script's own output).

## gh CLI

Still unavailable: `gh --version` and `gh auth status` both return
`command not found`. Confirmed unavailable in this environment across 7+
consecutive checks now (runs 26 onward per TODO.md). CI's real
GitHub-Actions pass/fail status remains genuinely unconfirmed —
manual YAML read-throughs only.

## Spot-check (early / mid / recent)

- **2026-05-07** (earliest): 3 signals (`sheer-layering`, `soft-tailoring`,
  `archival-romanticism`), no human_editor_note yet (predates that field's
  adoption), limitations prose reads consistently with the report's own
  editorial/social skew claim.
- **2026-10-12** (mid): 1 signal (`lfw-wholesale-eligibility-dropped`,
  the run-36/38 renamed short-form slug — no stale reference), one
  human_editor_note correctly framing "declining" as a reporting-activity
  statement, limitations correctly cross-reference `mfw-schedule-inconsistency`
  / `pfw-schedule-inconsistency` as closed-by-elapse rather than re-asserted.
- **2027-01-25** (most recent, added concurrently this run): 2 signals,
  both with human_editor_notes; correctly carries forward the Wales
  Bonner/Hermes signal from `2027-01-18.json` without re-editing that
  file, notes explicitly state no correction was made since nothing
  changed. No contradictions found.

No fixes were needed this run — all three checks came back clean against
the established baseline.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all reports pass

No commits made, per instructions.
