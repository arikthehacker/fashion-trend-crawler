# Sitemap, robots.txt, and JSON-LD

Implements items 2-4 from `docs/agent-logs/accessibility-seo-research.md`.

## Changes

- `web/lib/site.ts` (new): `SITE_URL` (from `NEXT_PUBLIC_SITE_URL` env, placeholder
  fallback) and `SITE_NAME` ("ARI3LLA INDEX") shared constants.
- `web/app/sitemap.ts` (new): App Router `MetadataRoute.Sitemap`. Lists the 8 static
  pages (`/`, `/archive`, `/methodology`, `/taxonomy`, `/sources`, `/about`,
  `/case-study`, `/timeline`) plus every `/reports/[date]` (via
  `getAllReportDates()`) and every `/signals/[slug]` (via `getAllSignalSlugs()`)
  from `lib/reports.ts`.
- `web/app/robots.ts` (new): App Router `MetadataRoute.Robots` — allows all
  crawling, points `sitemap` at `${SITE_URL}/sitemap.xml`.
- `web/app/reports/[date]/page.tsx`: added `NewsArticle` JSON-LD
  (`<script type="application/ld+json">`), inserted additively as the first child
  of `<main>` — no restructuring of existing markup, done alongside another
  agent's concurrent heading-hierarchy edits to the same file (re-read/re-applied
  the edit a few times due to concurrent writes; final diff is additive only).
  `headline` is derived from the first sentence of `executive_summary` (fallback
  generated title), `datePublished`/`dateModified` from `report_date`, `author`
  and `publisher` are both the `Organization` "ARI3LLA INDEX" (no personal name,
  per doc section 2 no-first-person/no-personal-brand voice rule).

## Verification

`cd web && npx tsc --noEmit` — clean, no errors.
`npx next build` — clean build. Confirmed `/sitemap.xml` and `/robots.txt` appear
as generated static routes in the build output, alongside all `/reports/[date]`
and `/signals/[slug]` static paths.

## Notes / follow-ups

- `SITE_URL` uses a placeholder domain (`https://ari3lla-index.example.com`) until
  a real production domain is set — set `NEXT_PUBLIC_SITE_URL` at deploy time.
- Canonical URL + Open Graph/Twitter metadata (research doc's item 5) and the
  layout.tsx JSON-LD are not part of this pass — left for a follow-up.
