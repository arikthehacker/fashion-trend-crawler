# Search facet + Pagefind verification (run 32)

**Result: both checks pass — no gap found, no fix needed.**

## Facet filters (1)

`web/lib/reports.ts`'s `getSearchIndex()` flattens `top_signals[]` across all
reports and copies `confidence`, `volatility`, `source_sectors` straight from
the report data — no hardcoded enum. `web/app/search/SearchClient.tsx` builds
each `<select>`'s options via `uniqueSorted()` over `index.map/flatMap` of
those same live fields (lines 86–97). There is no separate hardcoded value
list anywhere in either file to go stale.

Confirmed against current data (`data/reports/*.json`, archive now runs
through 2026-12-07):
- confidence: `high`, `low`, `medium` — all three selectable.
- volatility: `declining`, `emerging`, `flash`, `microtrend`, `recurring`,
  `revival`, `seasonal`, `stable`, `volatile` — all nine selectable (including
  `declining`, which the task flagged as a thing to check).
- source_sectors: `designer_origin`, `editorial`, `independent_criticism`,
  `institutional`, `retail`, `social` — all six selectable.

Since the dropdowns derive from the data at build time, any new value added to
a future report automatically appears next build — this can't drift out of
sync the way a hardcoded list could.

## Pagefind freshness (2)

- `cd web && npx tsc --noEmit` — clean.
- `npx next build` — succeeded, 82 static routes incl. 24 `/reports/[date]`
  pages (newest `2026-12-07`) and 42 `/signals/[slug]` pages.
- `npx pagefind --site out --output-subdir _pagefind` — walked `out/`, found
  and indexed 78 HTML files (up from 39 at run 15, consistent with archive
  growth), 3334 words.
- Verified freshness directly: decompressed the 78 `.pf_fragment` files
  (gzip) and grepped for text unique to the newest report
  (`data/reports/2026-12-07.json`'s top signal, "...seventh consecutive
  window..."). Found in 6 fragments (report page + related
  signal/timeline/archive pages), confirming the index reflects current data,
  not a stale prior build.

## Files touched

None — verification only, no gap found.
