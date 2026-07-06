# Archive/search UX audit (run 83)

## Scope
Hands-on audit of `web/app/archive/page.tsx` and the Pagefind search UI
(`web/app/search/page.tsx` + `web/app/search/SearchClient.tsx`) now that the
archive holds 75 reports spanning over a year, growing weekly.

## 1. Archive listing at 75+ items

Before this change, `archive/page.tsx` rendered `getAllReports()` (newest
first) as a single flat list with no pagination, no year/month grouping, and
no way to jump to a specific period — just one continuous scroll of 75 rows,
each `report_date` / top-signal / sources-scanned line, growing weekly with
no ceiling.

Researched how comparable archive/index pages handle this at similar and
larger scale: news/blog archives (NYT's articles-by-year archive, most
static-site generators' default archive templates, Wikipedia's "by year"
history pages) converge on the same low-cost pattern once an archive crosses
roughly a few dozen entries: **group entries under a period heading (year, or
year+month at higher volume)** rather than paginating or requiring a filter
UI. True pagination (page 1/2/3...) and faceted filtering are reserved for
archives in the hundreds/thousands, or ones with multiple independent
dimensions to filter by.

At 75 entries and ~1 year of weekly cadence, this project is past the point
where a flat list is free of cost (a reader looking for "reports from spring"
has to eyeball dates one row at a time) but nowhere near needing full
pagination or a dedicated filter UI (75 rows is still a light page weight,
and there is no evidence of multiple orthogonal filter dimensions readers
actually want on the archive page itself — that's what `/search` is for).
**Verdict: the flat list had become a real, if modest, usability gap —
proportionate fix is year-grouping headers, not full pagination/filtering.**

## 2. Filtering by year/month/archive_tags from the archive page

Confirmed there was no way to browse by year, month, or `archive_tags`
(`lib/reports.ts`'s `Report.archive_tags` is a real, populated schema field)
from `/archive` itself — the only paths were (a) scroll the full flat list,
or (b) leave the page entirely and use `/search`'s facet filters (source
sector / confidence / volatility) or Pagefind full-text search, neither of
which filters by year or `archive_tags` either. `archive_tags` is not
surfaced as a browsable dimension anywhere in the UI.

## 3. Pagefind search — actually verified, not assumed

Read `SearchClient.tsx`'s `PagefindSearch()` mount: it dynamically imports
`/_pagefind/pagefind-ui.js`, injects `/_pagefind/pagefind-ui.css`, and mounts
`PagefindUI` on `#pagefind-search`, failing silently pre-build (correct,
documented behavior for dev/no-bundle states). Confirmed `package.json`'s
`postbuild` script (`pagefind --site out --output-subdir _pagefind`) actually
runs as part of `npm run build`, and ran the real build to check its output
rather than trusting the wiring alone:

```
Found 179 files matching **/*.{html}
Did not find a data-pagefind-body element on the site.
↳ Indexing all <body> elements on the site.
Indexed 179 pages / 6001 words / 0 filters / 0 sorts
```

Since there's no `data-pagefind-body` scoping element on report pages,
Pagefind indexes each page's full rendered `<body>` — which includes the
title, `executive_summary`, and top-signal names/evidence text (all rendered
as visible text on `/reports/[date]`). So full-text search over title,
executive summary, and signal names genuinely works as configured; this is
confirmed, not assumed from a clean build. (0 filters/0 sorts just means no
`data-pagefind-filter` attributes are set anywhere — expected, since facet
filtering is intentionally handled by `/search`'s separate client-side facet
UI per `search-discoverability-design.md`, not by Pagefind.)

## Fix implemented

Added year-grouping headers to `web/app/archive/page.tsx`'s report list:
a small uppercase year label (`<h2>`, real heading — not a styled-`<p>`
per the project's known styled-heading bug pattern) is inserted whenever
the year changes while walking the newest-first report list, with a
top border/spacing separating each year group from the last. No new
props, no new data-layer function — the year is derived inline from each
report's existing `report_date` string. `archive_tags`/month grouping were
considered but not added: `archive_tags` is free-text per report (not a
controlled/enumerable facet in the current schema) and month-level grouping
at 75 items over 1 year would over-fragment a still-modest list — year
grouping alone addresses the real "which year is this from" scan problem
without over-engineering a filter UI the archive doesn't need yet.

## Validation

```
cd web && npx tsc --noEmit && npx eslint . && npm run build
```

All three passed clean. `npm run build` also re-ran `postbuild`'s Pagefind
indexing (179 pages / 6001 words indexed) confirming the archive-page change
didn't break the search index build.

## Not changed / left as-is

- `/search`'s facet filters (source sector / confidence / volatility) and
  Pagefind full-text search — both already work as designed and were not
  touched.
- No pagination added to `/archive` — 75 items with year headers is still a
  reasonably light single page; revisit if the list grows into the low
  hundreds.
- `archive_tags` remains unsurfaced as a browsable filter — flagged as a
  possible future improvement if `archive_tags` values stabilize into a
  small controlled vocabulary worth filtering on, but not implemented here
  since that would be new scope beyond the concrete gap found (year
  orientation), not a fix for it.
