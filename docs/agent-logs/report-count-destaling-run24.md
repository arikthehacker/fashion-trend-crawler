# Report-count de-staling (run 24)

Scope: `README.md`, `docs/PROJECT_STRUCTURE.md`, `.claude/skills/ari3lla-index/SKILL.md`.
Markdown-only, no `web/` changes, no build verification needed.

**Problem:** doc-sync runs 18 and 23 both had to fix hardcoded report counts/date
lists in README and PROJECT_STRUCTURE that drifted out of date as new reports
were added. A third manual fix would just recur again next report.

**Fix applied (option a — phrasing that doesn't need updating):**
- README Limitations: replaced "15 dated reports as of this writing" with a
  pointer to `ari3lla.com/archive` or `data/reports/` for the current count,
  plus a reference to the two prior stale-doc logs.
- README Project Structure code block: replaced the enumerated 15-file date
  list with a comment pointing at `/archive` / `ls data/reports/` instead of
  restating the list.
- `docs/PROJECT_STRUCTURE.md`: updated the "last synced" note to flag the
  removal, and collapsed the full 15-entry `data/reports/` listing down to a
  few illustrative entries (first report, real-crawl-verified report, thin-week
  start/end, fashion-month start) plus a `...` and a pointer comment — keeps
  useful context (which dates matter and why) without a maintained full list.

**Prevention:** added a numbered workflow convention (#8) to
`.claude/skills/ari3lla-index/SKILL.md` recommending future doc edits avoid
hardcoded counts/date-ranges that will go stale, preferring pointers to the
live `/archive` page or `data/reports/`, or an explicit "count as of <date>"
tag when a specific number is genuinely needed.

**Verification:** markdown-only changes; no `web/` files touched, so
`tsc --noEmit`/`next build` not run per task instructions. Visually reviewed
both diffs for broken markdown/table formatting — none found.
