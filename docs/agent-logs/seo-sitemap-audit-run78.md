# Run 78 — sitemap/JSON-LD audit (no code changes)

## Research

- Google Search Central sitemap guidance: single sitemap limit is 50,000 URLs /
  50MB uncompressed; beyond that, split into multiple sitemaps + a sitemap
  index file. Never include noindex/redirect/4xx/canonical-variant URLs.
  Archive is currently ~164 URLs total (10 static + 70 reports + 84 signals) —
  nowhere near the split threshold; a sitemap index is not warranted yet.
  ([Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap),
  [Managing Large Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/large-sitemaps))
- Schema.org/Google guidance on structured data: `Article`/`NewsArticle` fits
  written journalistic content; `Dataset` fits an actual data collection meant
  to be discoverable via Dataset Search / Google's Dataset markup. For an
  archival research index publishing both narrative summaries and a
  downloadable raw-data file per date, using both types on the same page
  (one per artifact) is the correct match rather than picking a single type.
  ([Dataset Structured Data](https://developers.google.com/search/docs/appearance/structured-data/dataset))

## Audit findings

1. **Sitemap coverage — already complete.** `web/app/sitemap.ts` calls
   `getAllReportDates()` and `getAllSignalSlugs()` (`web/lib/reports.ts`),
   which read directly off `data/reports/*.json` filenames and every distinct
   `signal_id` across all reports, respectively — no filtering, no cap, no
   stale hardcoded list. Verified against a real build:
   `data/reports/*.json` = 70 files; built `sitemap.xml` contains exactly 70
   `/reports/<date>` URLs and 84 `/signals/<slug>` URLs (84 distinct
   signal_ids across the archive). Static pages (10) are also present. No
   gap.

2. **JSON-LD — already implemented, and correctly scoped.** A prior run
   (`docs/agent-logs/sitemap-robots-jsonld.md`) added JSON-LD to
   `web/app/reports/[date]/page.tsx` only (not site-wide) with two objects
   sharing an `@graph`-less pair: `NewsArticle` (headline derived from
   `executive_summary`, `datePublished`/`dateModified` from `report_date`,
   `author`/`publisher` both the `Organization` "ARI3LLA INDEX" — no personal
   byline, consistent with the no-first-person voice rule) and `Dataset` (an
   accurate `DataDownload` distribution pointing at the same JSON file backing
   the visible "download raw data" link). All fields trace to real
   `report_schema.py`/`Report` fields — nothing invented. This matches the
   research above: Article-family markup for the narrative report, Dataset
   markup for the actual downloadable data, applied only to the archival
   content pages (not homepage/listing/prose pages, where it would add no
   real value for a non-traffic-driven research archive).

## Judgment call

No further JSON-LD or sitemap change is a genuine gap for this project's
stated purpose. Expanding structured data to listing/prose pages (archive,
timeline, methodology, etc.) would be scope creep with no discoverability
benefit — those aren't discrete indexable "items," they're navigation/prose.
Splitting the sitemap into an index file is premature at ~164 URLs (limit is
50,000). Confirmed clean; no code changes made this run.

## Verification

- `cd web && npx tsc --noEmit` — clean.
- `npx eslint .` — clean.
- `npm run build` — clean; build output shows 70 `/reports/[date]` static
  paths and 84 `/signals/[slug]` static paths generated.
- Manually greped built `out/sitemap.xml`: 70 report `<loc>` entries, 84
  signal `<loc>` entries — matches source data exactly.
