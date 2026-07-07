# Doc-sync + nav-consistency check (run 42)

Scope: README.md, docs/PROJECT_STRUCTURE.md, SKILL.md file map, site-wide nav audit.

## Doc-sync (README.md / PROJECT_STRUCTURE.md)

Both files are current and clean since run 33:
- `check_field_coverage.py`, `check_heading_patterns.py`, and `audit_confidence.py`
  are all listed in both README's Project Structure tree and PROJECT_STRUCTURE.md's
  `src/` listing.
- No new pages/routes exist beyond what's already documented (14 `.tsx` page files,
  all accounted for in both docs).
- `docs/agent-logs/` references use pointer phrasing ("see `ls docs/agent-logs/`")
  rather than a stale hardcoded count, in both README and PROJECT_STRUCTURE.md.

No changes needed to README.md or PROJECT_STRUCTURE.md.

## SKILL.md file map

Found and fixed one gap: `src/check_heading_patterns.py` (run 22/29) existed in the
repo and was already documented in README/PROJECT_STRUCTURE.md, but was missing from
`.claude/skills/ari3lla-index/SKILL.md`'s own architecture/file-map section. Added it
alongside the existing `check_field_coverage.py` entry.

## Site-wide nav audit

Read every `.tsx` page's nav/footer markup directly (not just grepped hrefs, since a
plain `grep` mis-parsed multi-item arrays earlier and produced false positives that
had to be re-verified with the Grep tool).

Confirmed two legitimate, consistent nav patterns already in place:
- **Pattern A** (home, methodology, taxonomy, sources, about, glossary): full
  9-item top masthead nav, tagline-only footer. All six pages' nav arrays contain
  all 9 sections minus a self-link — verified link-by-link, no gaps.
- **Pattern B** (archive, timeline, signals/[slug], search, reports/[date]): no top
  nav, footer with a subset of links (Archive/Timeline/Search/Home, reports/[date]
  additionally includes Methodology). Consistent across all five pages.

**Bug found and fixed:** `case-study/page.tsx` is thematically a Pattern-A static
reference page but had neither a top nav bar nor footer nav links — only a single
inline "ARI3LLA INDEX" link back to the homepage. Added the standard Pattern-A
9-item nav (this page as self, so 8 links: Report, Methodology, Taxonomy, Sources,
Glossary, Timeline, Archive, Search, About) to its masthead, matching the other five
Pattern-A pages exactly in markup/style.

Verified with `npx tsc --noEmit` and `npx eslint .` in `web/` — both clean.

Not committed per task instructions.
