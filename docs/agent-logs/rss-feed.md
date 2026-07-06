# RSS feed — agent log

Added an RSS 2.0 feed so readers can subscribe to new reports instead of
checking the archive manually.

## Files touched

- `web/app/rss.xml/route.ts` (new) — Route Handler that builds RSS 2.0 XML
  from `getAllReports()` in `lib/reports.ts`, newest first. Each `<item>`
  titles with `report_date`, links to `/reports/[date]` (built from
  `SITE_URL`), uses `executive_summary` as `<description>`, and sets
  `<pubDate>`/`<guid>` accordingly. Channel-level `<title>`/`<link>` use
  `SITE_NAME`/`SITE_URL` from `lib/site.ts` — no new site-identity constants
  introduced. Needed `export const dynamic = "force-static"` because the
  project builds with `output: export`; without it `next build` fails
  ("force-static"/revalidate not configured on route "/rss.xml").
- `web/app/layout.tsx` — added `alternates.types["application/rss+xml"]:
  "/rss.xml"` to the existing `metadata` object, which Next's metadata API
  renders as the standard `<link rel="alternate" type="application/rss+xml"
  href="/rss.xml">` tag. No other metadata changed.

## Not touched

`web/app/sitemap.ts`, `web/app/robots.ts`, `web/next.config.ts` — left alone
per instructions (other agent editing concurrently).

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean.
Build output lists `○ /rss.xml` as a static route alongside the other pages.

## Not committed

Per instructions, no commit was made.
