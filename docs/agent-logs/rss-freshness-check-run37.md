# RSS feed freshness check — run 37

Follow-up on run 36's `dateModified` fix on report-page JSON-LD, checking whether
`web/app/rss.xml/route.ts` had the same staleness gap.

## Findings

It did. Each `<item>`'s `<pubDate>` was built solely from `report.report_date` via
`toRfc822()`, with no reference to `revision_history[].corrected_at` anywhere —
identical to the bug run 36 fixed in the report page's `dateModified`. A corrected
report's RSS entry would still show its original publish date, giving subscribers
(and feed readers that dedupe/sort by `pubDate`) no signal that content changed.

XML escaping (`escapeXml()`) was re-checked and is still fine: handles `&`, `<`, `>`,
`"`, `'` via ordered `.replace()` calls (order matters — `&` first — and it is first),
applied consistently to title/link/guid/description across all items. No regression
since run 15's verification.

## Change made

`web/app/rss.xml/route.ts`: each item now computes `lastUpdated` from the last entry
in `report.revision_history` (`corrected_at`) when present, falling back to
`report.report_date` otherwise, and uses that for `<pubDate>` instead of always the
original report date. Mirrors the run-36 report-page fix. No schema changes, no other
files touched.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean, all 88 static pages
generated, `○ /rss.xml` listed as a static route.

## Not committed

Per instructions, no commit was made.
