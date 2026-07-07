# Doc consistency audit — run 14

Cross-checked `README.md`, `docs/PROJECT_STRUCTURE.md`, and
`.claude/skills/ari3lla-index/SKILL.md` against actual repo state.

**Sanity check:** `git ls-files | grep -c trends` → 1 (only
`docs/agent-logs/trends-ts-fate-proposal.md`, historical record, fine to keep).
`git ls-files | grep -c "trends_raw\|trends_summary"` → 0. Legacy cache files
and `web/lib/trends.ts` are confirmed gone from tracked files.

**Fixes made:**

- **SKILL.md**: file map no longer lists `web/lib/trends.ts`; added
  `web/app/rss.xml/route.ts` and `web/lib/site.ts`, noted homepage now reads
  `reports.ts`. Moved the trends.ts retirement item in "Common next steps"
  from "pending sign-off" to "resolved run 13."
- **README.md**: removed the `trends_raw.json`/`trends_summary.json` migration
  roadmap/limitations bullets (files no longer exist), added a "homepage
  rebuilt off reports.ts" roadmap checkmark, updated the Project Structure
  tree (dropped `trends.ts` and legacy JSON files, added `search/`,
  `rss.xml/`, `site.ts`), and corrected the dated-report count from 4 to 7
  (actual: 2026-05-07 through 2026-08-10).
- **PROJECT_STRUCTURE.md**: removed the legacy `trends_raw.json`/
  `trends_summary.json` entries under `src/` and root; fixed the stale
  `run.sh` description (it was still marked "KNOWN STALE / never calls
  summarize.py" — that was fixed run 1 per SKILL.md); marked `/timeline` and
  `/signals/[slug]` as built (run 3/4) instead of planned-only; added
  `search/`, `rss.xml/route.ts`, and `lib/site.ts`; rewrote the Notes section
  to reflect legacy-file removal instead of a pending cleanup.

No changes touched `web/` code, so the `tsc`/`next build` verification step
was not run (not applicable — docs-only change).
