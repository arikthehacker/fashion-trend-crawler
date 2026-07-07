# Doc sync (run 33)

Scope: `README.md` and `docs/PROJECT_STRUCTURE.md` only.

**Run 24's "pointer to live archive" fix held.** No hardcoded report counts
or date lists found back in either file — README's Limitations/Roadmap
sections and PROJECT_STRUCTURE's `data/reports/` entry still point at
`data/reports/`/`/archive` instead of a number. Good.

**Drift found and fixed (src/ additions from runs 25/29 not reflected):**
- `src/check_field_coverage.py` (run 25) and `src/check_heading_patterns.py`
  (run 22/29) existed in the repo but were missing from both README's
  Project Structure tree and PROJECT_STRUCTURE.md's `src/` listing. Added
  both, plus `audit_confidence.py` (run 7) which was also missing from
  README's tree (it was already in the skill doc but not README).
- `docs/agent-logs/` has grown to 166+ files; PROJECT_STRUCTURE.md still
  enumerated only ~15 by name (stale placeholder list). Replaced with a
  count + pointer to `ls docs/agent-logs/`, matching the same
  don't-hardcode convention already applied to report counts.

**Spot-checks against actual code (not just presence):**
1. README's CI description ("validate re-runs schema validation... lint-web
   runs ESLint incl. jsx-a11y") matches `.github/workflows/validate-reports.yml`
   exactly: `validate` job runs `py_compile` + `validate_all_reports.py`;
   `lint-web` job runs `npx eslint .` in `web/`. Holds up.
2. `revision_history` claim (required reason+timestamp on overwrite) —
   confirmed in `src/report_schema.py` lines ~297-537 (schema field,
   validation of required keys, append-on-revision logic). Holds up.
3. `/search` Pagefind claim — confirmed `web/package.json` has `pagefind`
   devDependency and `postbuild: "pagefind --site out --output-subdir
   _pagefind"`. Holds up.

Nothing under `web/` was edited, so `tsc --noEmit` was not run (not
required per task instructions).
