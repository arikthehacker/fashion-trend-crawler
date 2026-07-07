# IPTC metadata check — run 36

Follow-up on run 35's link-rot mitigation work, which flagged IPTC NewsArticle/rNews
metadata as a researched-but-not-pursued angle.

## Findings

IPTC's rNews standard (predecessor whose properties schema.org's `NewsArticle` type
derived from) and IPTC NewsCodes both emphasize distinguishing **original publication
date from last-modified/corrected date** as a core integrity signal for news content —
exactly the kind of provenance claim this project already tracks via
`revision_history[].corrected_at` in `src/report_schema.py`, but the site's JSON-LD
wasn't surfacing it.

Checked the existing JSON-LD in `web/app/reports/[date]/page.tsx`: it already includes
`headline`, `datePublished`, `url`, `mainEntityOfPage`, `description`, `author`,
`publisher`, and `keywords` (from `archive_tags`) — solid alignment already. The one
concrete gap: `dateModified` was hardcoded to `report.report_date`, identical to
`datePublished`, even for reports with a non-empty `revision_history`. That's the same
"claims not matching the actual data" pattern the skill's convention #9 warns about —
a corrected report was telling search engines/readers it was never modified.

`articleSection`/`about` entity mapping would require picking a canonical taxonomy
value per report (source sector? signal type?) — judged too speculative for a small
additive fix within scope, left as a future candidate rather than guessed at here.

## Change made

`web/app/reports/[date]/page.tsx`: `dateModified` now sources from the last
`revision_history` entry's `corrected_at` when one exists, falling back to
`report.report_date` for uncorrected reports. Small, additive, no schema changes.

## Verification

`cd web && npx next build` — compiled successfully, all 86 static pages generated
(TypeScript checked as part of the build; standalone `tsc` binary isn't hoisted to
`node_modules/.bin` in this repo, so `next build`'s internal type-check step was used
instead).
