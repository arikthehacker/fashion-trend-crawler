# Doc-sync check, run 55

**Result: one real gap found and fixed. Everything else checked out accurate.**

## What was checked

1. **Recently-shipped files/routes present in all three docs** (README.md,
   docs/PROJECT_STRUCTURE.md, SKILL.md's file map):
   - `generate_archive_manifest.py` (run 43) — present in all three (fixed run 47).
   - `copy-reports.mjs` (run 45/46) — present in all three (fixed run 47).
   - Open Graph metadata (`web/app/layout.tsx` `openGraph`/`twitter` blocks) — exists in
     code, not specifically named in docs, but no doc makes a false claim about it either
     (layout.tsx's own comment just says "keep in sync with rebrand"). No fix needed.
   - Recurring-signals archive section and dieworkwear.com source (run 54, added to
     `FASHION_SOURCES` with a detailed inline comment) — dieworkwear.com is a data
     addition, not a structural file; no doc makes a source-count/list claim that it
     would invalidate. README already points readers to the live `FASHION_SOURCES` list
     rather than hardcoding a count (per convention #8). No fix needed.
   - **`web/app/icon.tsx` (run 53) was genuinely missing from all three docs.** It's a
     Next.js route-segment metadata file that auto-generates the site favicon via
     `ImageResponse` (needs `dynamic = "force-static"` for static export, same pattern as
     `sitemap.ts`/`robots.ts`). PROJECT_STRUCTURE.md listed `favicon.ico` as the favicon
     but didn't mention that `icon.tsx` is what Next actually serves. Added an entry to
     README.md's structure tree, PROJECT_STRUCTURE.md's `app/` tree (with a note
     distinguishing it from the static `favicon.ico` fallback), and SKILL.md's file map.

2. **`FASHION_SOURCES` count/list vs. any doc claim.** No doc states a hardcoded source
   count — README explicitly says "see `src/crawler.py`'s `FASHION_SOURCES` list for the
   current, up-to-date set," per convention #8 (established runs 18/23/24 after repeated
   staleness). No fix needed.

3. **SKILL.md workflow-conventions numbered list.** Confirmed 1 through 11, sequential,
   no duplicate numbers, no internally contradicting entries (checked #8/#9 on stale
   counts + field-visibility, #10 on prolonged-silence signals, #11 on `gh`-cadence — all
   still consistent with each other and with the rest of the doc).

## Files changed

- `README.md`
- `docs/PROJECT_STRUCTURE.md`
- `.claude/skills/ari3lla-index/SKILL.md`

Docs-only change; `tsc`/`py_compile` not required and not run. Not committed per task
instructions.
