# Skill doc refresh — SKILL.md factual audit

Corrected `.claude/skills/ari3lla-index/SKILL.md` only.

## Fixes
- `run.sh`: removed the "KNOWN STALE" note (false since run 1). It now correctly runs
  `crawler.py` → `summarize.py`, confirmed by reading the current file.
- `test_tools.py` note softened — still tests the old raw-cache pipeline, but no longer
  pointed at a run.sh follow-up that already happened.
- File map was missing: `src/manual_sample.py`, `src/validate_all_reports.py`,
  `web/app/timeline/page.tsx`, `web/app/signals/[slug]/page.tsx`, `web/app/sitemap.ts`,
  `web/app/robots.ts`, and `.github/workflows/validate-reports.yml`. Added all, each with
  a one-line note on what it does and when it landed (verified against `Glob` of `src/*.py`,
  `web/app/**/*.tsx`, and `.github/workflows/*`).
- "Common next steps" section was stale (referenced wiring summarize.py into run.sh,
  building `/timeline`/`/signals/[slug]` — all done). Replaced with a pointer to `TODO.md`
  (the authoritative, per-run-updated list) plus the 3 highest-priority open items pulled
  from TODO.md's "Next up (run 7 candidates)" section: no live-crawl report yet, no
  corrections/transparency policy on-site, and the legacy `trends_raw.json` migration
  (in progress, one step at a time per `docs/agent-logs/legacy-migration-plan.md`).

## Not changed
Concept/voice sections, workflow conventions, and overall structure/tone left untouched —
only factual/file-map corrections and the next-steps pointer were in scope.
