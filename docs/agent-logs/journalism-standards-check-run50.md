# Journalism-standards check — run 50: sitemap lastModified accuracy

## Topic

Sitemap `changefreq`/`priority`/`lastmod` conventions — not previously covered in
agent-logs (`sitemap-robots-jsonld.md` covers the initial build, not ongoing accuracy).

## Research

Confirmed via Google Search Central docs and community threads (2025 guidance):
Google explicitly **ignores** `<priority>` and `<changefreq>` in sitemaps — they have no
effect on crawling/indexing/ranking. The only field that matters is `<lastmod>`, and only
when it is "consistently and verifiably accurate." Google's own advice: spend effort on
accurate `lastmod`, not on tuning `changefreq`/`priority` numbers.

## Gap found

`web/app/sitemap.ts` set `changeFrequency`/`priority` on every route but had **no
`lastModified` at all** on the 10 static routes (`/`, `/archive`, `/methodology`,
`/taxonomy`, `/sources`, `/about`, `/case-study`, `/timeline`, `/glossary`, `/search`) or
on any `/signals/[slug]` route. Only `/reports/[date]` routes had `lastModified` (correctly,
via the report's own date). This is backwards from what actually matters: the site had
been polishing the field Google ignores and omitting the one it uses.

## Fix

Edited `web/app/sitemap.ts`:
- Added `lastModified: getLatestReport()?.report_date` to the archive-dependent static
  routes (`/`, `/archive`, `/timeline`, `/search`, `/glossary`) — their content genuinely
  changes whenever a new report ships, so this is an honest timestamp, not a guess.
- Left the fixed-prose pages (`/methodology`, `/taxonomy`, `/sources`, `/about`,
  `/case-study`) without `lastModified` rather than fabricating one — no reliable
  last-edit timestamp exists for them at build time.
- Added the same `lastModified` to `/signals/[slug]` routes (tracks the latest report
  date, since per-signal last-seen dates aren't exposed by `getAllSignalSlugs()`).
- Added a code comment explaining Google ignores changeFrequency/priority so a future
  agent doesn't spend effort re-tuning those numbers instead of `lastModified` accuracy.
- Left `/reports/[date]` routes unchanged (already correct) and added a comment noting
  why `changeFrequency: "yearly"` there is an honest floor (archival snapshots don't get
  revised).

## Verification

`cd web && npx tsc --noEmit` — no errors attributable to `sitemap.ts`. Pre-existing
unrelated errors in `app/glossary/page.tsx` (missing `fs`/`path` imports) are another
agent's concurrent work in progress, not touched here.

## Files touched

- `web/app/sitemap.ts` only.
