# Citation line

Added a small "Cite as" footer line to `web/app/reports/[date]/page.tsx`, per the
LoC-derived recommendation in `docs/agent-logs/accessibility-seo-research.md` (stable
identifiers + self-contained citation metadata for archived items).

## What was added

A single monospace `<p>` placed after the existing "Archive checksum" line, additive only
(no restructuring of surrounding JSX, to stay out of the way of the two concurrent agents
touching heading hierarchy and JSON-LD in the same file):

```
Cite as: ARI3LLA INDEX, {report.report_date}, /reports/{report.report_date}
 (checksum {first 12 chars of content_hash})
```

## Notes / decisions

- No canonical domain exists anywhere in the codebase yet (checked `web/app/layout.tsx`
  and grepped the whole `web/` tree — no `metadataBase`, no hostname string outside
  `node_modules`/lockfiles). Rather than invent one, the citation uses the site-relative
  path (`/reports/<date>`), matching the pattern already used for internal `<Link>`s on
  this page. Once a real domain/`metadataBase` is established (flagged as a to-do in the
  research doc), this should be updated to a full absolute URL.
- Reused `report.content_hash` (already displayed as "Archive checksum" a few lines
  above) rather than duplicating the full hash — only shows it if present, matching the
  existing conditional.
- Kept to plain wire-service voice per skill voice rules, no styling changes to the rest
  of the page.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean. Build output shows
all three report dates statically generated with no errors; sitemap.xml/robots.txt from
the concurrent SEO work are present and unaffected.

Not committed, per instructions.
