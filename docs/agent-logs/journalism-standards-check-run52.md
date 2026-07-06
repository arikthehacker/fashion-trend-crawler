# Journalism-standards check, run 52: Open Graph / social-card metadata

## Topic

Not previously covered in prior agent-logs list: whether sharing an ARI3LLA INDEX link
(homepage or a dated report) produces a sensible text-based preview card on
Slack/Twitter/iMessage/etc, given the site intentionally has no image assets.

## Standard checked against

Open Graph protocol (ogp.me) and Twitter Card docs: the five core OG tags are
`og:title`, `og:description`, `og:url`, `og:type`, `og:image`. Without an image, the
correct Twitter card type is `summary` (small card), not `summary_large_image` (which
silently fails/falls back without an image). `og:description` is technically optional
in the spec but effectively required — without it, platforms show no description or
scrape random page text instead.

## Gap found

`web/app/layout.tsx` only set plain `title`/`description` in the Next.js `Metadata`
object — no `openGraph` or `twitter` block anywhere in the app. `web/app/reports/[date]/page.tsx`'s
`generateMetadata` had the same gap for per-report pages. Result: sharing any link
would have produced either no preview card or one built from guessed/scraped content,
inconsistent with the site's otherwise deliberate metadata discipline (it already has
sitemap.ts, robots.ts, RSS, Dataset JSON-LD).

## Fix applied

- `web/app/layout.tsx`: added `metadataBase` (using existing `SITE_URL` from
  `lib/site.ts`), plus `openGraph` (siteName, title, description, url, type: "website")
  and `twitter` (card: "summary", title, description) blocks as site-wide defaults.
- `web/app/reports/[date]/page.tsx`: `generateMetadata` now also returns a per-report
  `openGraph` (type: "article", correct per-date url) and `twitter` block, plus a
  `canonical` alternate link that was also missing.
- Deliberately used `twitter:card: "summary"` (not `summary_large_image`) since the
  site has no image assets — matches actual capability rather than aspirational card
  type that would show a broken/empty image slot.

## Verification

`cd web && npx tsc --noEmit` — passes, no type errors.

## Not done / follow-up

Only `layout.tsx` (site-wide) and `reports/[date]/page.tsx` were touched. Other pages
(archive, timeline, signals/[slug], methodology, taxonomy, sources, search, about,
glossary, case-study) inherit the site-wide OG/twitter defaults from layout.tsx but
don't yet set page-specific `openGraph`/`twitter` overrides the way reports/[date] now
does. Reasonable next-run candidate if per-page social copy is wanted, but the site-wide
fallback means no page is currently broken/missing a card.
