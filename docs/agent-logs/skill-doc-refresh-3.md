# Skill doc refresh 3

Cross-checked `.claude/skills/ari3lla-index/SKILL.md`'s file map against actual
`web/app/`, `web/lib/`, `src/`, `docs/` trees.

Findings:
- `web/lib/trends.ts` was already gone (confirmed via glob) — no action needed there,
  but tightened the `reports.ts` note to say "confirmed gone — do not re-add" and added
  its run-13 `getConsecutiveThinWeekCount()`/`getLatestReport()` helpers, which were
  missing from the map.
- `src/audit_confidence.py` (added run 7, used for periodic confidence/dormancy review)
  was missing from the file map — added.
- `docs/PROMPT_CHANGELOG.md` (run 15) and the `fashion-week-calendar-research.md` agent
  log were missing from the docs section — added.
- `changelog-entries/*.md` range note updated from "run-01..run-12" to "run-00..run-16"
  to match the actual files present.

Updated "Common next steps" to point at `TODO.md`'s current "Run 17 candidates" list
(don't force `collection_status: "normal"` before ~Sept 8 2026; source-list diversity gap;
low-volatility framing follow-through; making bias-audit periodic) instead of the stale
run-12 items, which were all resolved by run 13.

Added a new "Institutional knowledge worth knowing before you start" section noting the
fashion-week calendar context (NYFW/LFW/MFW/PFW ~Sept 8 - Oct 6, 2026) so future runs
don't mistake the current 5-report thin-week streak for a crawl/sourcing bug — this fact
was previously buried in `docs/agent-logs/fashion-week-calendar-research.md` only.

Did not touch `docs/CHANGELOG.md`, `docs/changelog-entries/`, or the file's overall
format/structure, per instructions. No commit made.
