# RSS/sitemap verification — run 28

Verified `web/app/rss.xml/route.ts` and `web/app/sitemap.ts` against real static
export output (`web/out/`) now that the archive has grown to 20 reports / 37
signal_ids and static export actually works (run 22 fix).

## Method

Ran `cd web && npx tsc --noEmit && npx next build`, then parsed the generated
`out/rss.xml` and `out/sitemap.xml` with Python's `xml.dom.minidom` (fails hard
on any malformed/unescaped XML) and cross-checked counts against
`data/reports/*.json`.

## Findings

1. **RSS completeness**: `getAllReports()` reads every file in `data/reports/`
   with no slice/cap — `out/rss.xml` contains all 20 `<item>` entries, newest
   first (`lastBuildDate` = 2026-11-09). Not stale, not capped.
2. **XML escaping**: `escapeXml()` in the route handler escapes `&`, `<`, `>`,
   `"`, `'` before interpolation. Grepped `data/reports/*.json` for raw
   `&`/`<`/`>` — found only an arrow (`->`) inside one `index_note` string
   (2026-10-12) and one long line in 2026-07-20; neither breaks XML since
   `escapeXml` handles them unconditionally regardless of content. minidom
   parsed `out/rss.xml` without error, confirming well-formedness.
3. **Sitemap completeness**: found a genuine bug — `web/app/sitemap.ts`'s
   `staticRoutes` list predated `/glossary` and `/search` (both real pages
   under `web/app/`) and never included them, so they were silently missing
   from `sitemap.xml`. Fixed by adding `"/glossary"` and `"/search"` to the
   `staticRoutes` array (same route object shape/defaults — monthly,
   priority 0.6 — as the other secondary pages).
4. Post-fix, `out/sitemap.xml` has 67 `<url>` entries: 10 static pages
   (including the two fixed) + 20 report routes + 37 signal routes, matching
   `getAllReportDates()`/`getAllSignalSlugs()` output exactly.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both clean. Build output
lists `/glossary` and `/search` as static routes, `/rss.xml` and
`/sitemap.xml` generated correctly, 20 report + 37 signal SSG paths.

## Files touched

- `web/app/sitemap.ts` — added `/glossary`, `/search` to `staticRoutes` (bug
  fix, genuine gap found).
- `web/app/rss.xml/route.ts` — not modified, verified correct as-is.

Not committed, per instructions.
