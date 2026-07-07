# Doc-sync check, run 59

**Result: real gaps found and fixed in all three docs; workflow-conventions list checked
clean.**

## What was checked and fixed

1. **`requirements.txt` (added run 55) was missing everywhere.** README.md's setup
   instructions still hardcoded `pip install requests beautifulsoup4 mcp anthropic`
   (no `brotli`, not using the real dependency file); its structure tree also omitted the
   file entirely. Fixed: README now runs `pip install -r requirements.txt mcp` (mcp isn't
   in requirements.txt, kept separate) and lists `requirements.txt` in the tree.
   PROJECT_STRUCTURE.md and SKILL.md's file maps both got a `requirements.txt` entry
   noting its contents and the brotli rationale (dieworkwear.com Brotli-encoding bug,
   run 55).

2. **Accessibility/dark-mode: real, shipped, undocumented.** `web/app/layout.tsx` renders
   a site-wide skip-to-content link (verified across all 117 generated pages per
   `agent-logs/skip-link-verification-run57.md`), and `web/app/globals.css` has a
   `prefers-color-scheme: dark` block for automatic OS-driven dark mode. Neither was
   mentioned in PROJECT_STRUCTURE.md or SKILL.md's file maps (README doesn't list
   layout.tsx/globals.css individually, so nothing stale there). Added brief, accurate
   notes to both docs' entries for `layout.tsx`/`globals.css`.

3. **Met Gala signal tracking (run 57) and glossary curation (runs 40/58):** these are
   data-content changes (a `Signal` added to specific report JSON files; curated
   definition text in glossary data), not structural files or new pages — same category
   as the dieworkwear.com source addition that run 55 correctly ruled "no doc fix needed."
   No doc makes a claim these would invalidate. No fix needed.

4. **SKILL.md's numbered workflow-conventions list (1-11):** re-confirmed sequential,
   no duplicate numbers, no contradictions. #11 (gh CLI cadence, added run 53, next due
   run 60) is internally consistent with everything else — no changes since run 55's
   check.

## Files changed

- `README.md`
- `docs/PROJECT_STRUCTURE.md`
- `.claude/skills/ari3lla-index/SKILL.md`

Docs-only change; `tsc`/`py_compile` not required and not run. Not committed per task
instructions.
