# Accessibility, SEO & Archival-Permanence Research + Audit

Research/audit only — nothing implemented. Feeds into TODO.md.

## Research findings

**(a) Accessibility — headings/semantic HTML**
WCAG requires headings to have "an appropriate hierarchical relationship" (no skipped
levels) and to be marked up with real `<h1>`–`<h6>` elements, not styled `<p>`/`<div>`s,
so assistive tech can navigate by outline (W3C WAI, [Headings tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/);
[WCAG H42 technique](https://www.w3.org/TR/WCAG20-TECHS/H42.html); [A11Y Collective guide](https://www.a11y-collective.com/blog/accessibility-headings/)).
Each heading should be meaningful and directly precede the content it labels — same
guidance doubles as an SEO signal for how search/AI systems parse page structure.

**(b) SEO / structured data**
Google recommends JSON-LD (placed in `<head>`) using `Article` for evergreen content or
`NewsArticle` for news-cycle content, with `headline`, `datePublished`/`dateModified`,
`author`, and `image` (≥1200×675px) ([Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/article);
[schema.org/Article](https://schema.org/Article), [schema.org/NewsArticle](https://schema.org/NewsArticle)).
A sitemap should be submitted/kept current, and pages must not be blocked by robots.txt
or noindex ([Google guidance](https://developers.google.com/search/docs/appearance/structured-data/article)).

**(c) Archival permanence**
Library of Congress digital-preservation guidance emphasizes stable identifiers, durable
formats, and consistent metadata for long-term citability, per OAIS/PREMIS-derived
standards ([LoC Digital Preservation Resources](https://www.digitalpreservation.gov/about/resources.html);
[LoC Standards](https://www.loc.gov/librarians/standards)). Applied to a small JSON
archive: each dated report needs a stable, permanent URL/identifier and self-contained
citation metadata (issue date, source, title) so an item remains referenceable even if
site navigation changes.

## Codebase audit

- `web/app/layout.tsx`: no `lang` issue (has `lang="en"`), but site-wide metadata is
  title/description only — no JSON-LD, no canonical URL, no Open Graph tags.
- `web/app/reports/[date]/page.tsx`: only one real heading (`<h1>` for the date). Every
  other section label ("Executive Summary," "Observed Signals," etc.) is a styled `<p>`,
  not `<h2>`/`<h3>` — this breaks WCAG heading-hierarchy navigation for screen-reader
  users and forfeits an SEO structure signal. `generateMetadata` sets title/description
  per report but emits no `Article`/`NewsArticle` JSON-LD, no `datePublished`, no
  canonical link, no citation identifier beyond the URL path itself.
- No `sitemap.xml`, `robots.txt`, or `next-sitemap` config found anywhere under `web/`
  (checked via glob for `sitemap`/`robots*` and Next's file-convention docs) — Next.js
  App Router supports these natively via `app/sitemap.ts` and `app/robots.ts`, neither
  exists.
- No JSON-LD found anywhere in `web/app/**`.

## Concrete next steps (do not implement now — add to TODO.md)

1. In `web/app/reports/[date]/page.tsx`, promote section `<p style={labelStyle}>` labels
   to real `<h2>` elements (keep the visual style, change the tag), preserving current
   nesting order top to bottom.
2. Add `app/sitemap.ts` generating entries for `/`, `/archive`, `/methodology`,
   `/taxonomy`, `/sources`, `/about`, `/case-study`, and every `/reports/[date]` via
   `getAllReportDates()`.
3. Add `app/robots.ts` allowing all crawl + pointing to the new sitemap.
4. Add `Article`/`NewsArticle` JSON-LD (`<script type="application/ld+json">`) to
   `web/app/reports/[date]/page.tsx`, populated from `report.report_date`,
   `report.executive_summary`, and a fixed `author`/`publisher` ("ARI3LLA INDEX").
5. Add canonical URL + basic Open Graph/Twitter metadata to `generateMetadata` in both
   `web/app/layout.tsx` and `reports/[date]/page.tsx`.
6. Consider a stable citation line per report (e.g. "ARI3LLA INDEX, `<date>`,
   `https://.../reports/<date>`") near the footer, in line with LoC-style archival
   citation practice, so archived reports remain independently citable.
