# Doc-sync check, run 63

**Result: one real gap found and fixed; report-count convention and workflow-conventions
numbering both checked clean.**

## What was checked

1. **`check_signal_reuse_claims.py` (added run 61, wired into periodic-audit routine as
   SKILL.md convention #12 at run 62) was missing from README.md and
   `docs/PROJECT_STRUCTURE.md`'s file trees — present only in SKILL.md's file map.** Fixed:
   added an entry to both, next to `generate_archive_manifest.py`, noting what it does, that
   it's not wired into CI, and that it's a standing periodic-audit step per run 62.

2. **Report-count/date-range hardcoding (run-24 convention):** re-checked both README.md
   and PROJECT_STRUCTURE.md. Both still use pointer phrasing ("see `/archive` or
   `data/reports/` for the current count") with no hardcoded numbers or stale date-range
   lists. No drift found — convention holding.

3. **SKILL.md's numbered "Workflow conventions" list:** re-confirmed items 1-12 are
   sequential with no duplicate or skipped numbers, and #12 (check_signal_reuse_claims.py
   as a standing periodic-audit step, decided run 62) is internally consistent with the
   rest of the list and with the file-map entry above it. No changes needed.

## Files changed

- `README.md`
- `docs/PROJECT_STRUCTURE.md`

Docs-only change; `py_compile`/`tsc` not required and not run. Not committed per task
instructions.
