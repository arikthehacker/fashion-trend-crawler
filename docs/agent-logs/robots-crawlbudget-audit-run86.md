# Robots.txt / crawl-budget audit — run 86

## Scope

Re-audit `web/app/robots.ts` and `web/app/sitemap.ts` now that the site has crossed
~190 total static routes (78 dated reports + 96 signal pages + ~14 static pages, plus
`/rss.xml`, `/robots.txt`, `/sitemap.xml`, `/icon`, confirmed via a real `npm run build`
— Pagefind's postbuild step reported "Indexed 186 pages"). Checked: crawl-delay guidance,
disallow rules for framework-internal/query-string routes, sitemap size/index-splitting
thresholds, and canonical-tag coverage for pages reachable via multiple paths.

## Current state (read in full)

- `web/app/robots.ts`: `userAgent: "*"`, `allow: "/"`, points to `${SITE_URL}/sitemap.xml`.
  No disallow rules, no crawl-delay.
- `web/app/sitemap.ts`: single flat sitemap (not a sitemap index), lists all static pages,
  report routes, and signal routes with `lastModified`/`changeFrequency`/`priority`.
  Already documents (correctly) that Google ignores `changeFrequency`/`priority` as of
  2025+ and that `lastModified` is the only field with real effect.
- `/search` (`web/app/search/page.tsx` + `SearchClient.tsx`): the facet filter is plain
  client-side array filtering with no query-string routes. Pagefind (loaded via
  `SearchClient.tsx`) is a client-side-only JS/WASM bundle imported from `/_pagefind/` —
  no server-rendered `/search?q=...` result pages exist anywhere in the app.
- Canonical tags: `web/app/reports/[date]/page.tsx` sets `alternates: { canonical: ... }`
  in `generateMetadata`. `web/app/signals/[slug]/page.tsx` does not set a canonical tag.
  Both route types have exactly one static path per report/signal (from
  `generateStaticParams()` over `getAllReportDates()`/`getAllSignalSlugs()`) — neither
  report pages nor signal pages are reachable via more than one URL path, so there is no
  live duplicate-content case for canonical tags to resolve today.

## Research (WebSearch, current as of this audit)

1. **Crawl-delay**: Googlebot does not support it — Google's own robots.txt spec doc
   states other fields like crawl-delay "aren't supported" and are discarded during
   parsing (developers.google.com/crawling/docs/robots-txt/robots-txt-spec). Bing does
   still honor it, but omitting it is standard and not a gap; Search Console's crawl-rate
   setting is the supported lever if ever needed.
2. **Disallowing Next.js internal routes** (`/_next/`, `/_vercel/`): not recommended.
   Googlebot needs `/_next/static/*` and `/_next/image` to render pages for rendering/CWV
   evaluation; blanket-blocking `/_next/` risks render failures. The only sub-path
   sometimes blocked is `/_next/data/` (JSON payloads for client-side nav, not
   user-facing), which is low-value and unnecessary for a static export where these paths
   are internal, unlinked build assets rather than crawlable content anyway
   (nextjs.org/docs/app/api-reference/file-conventions/metadata/robots).
3. **Sitemap limits** (developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap;
   sitemaps.org/protocol.html): max **50,000 URLs** and **50MB uncompressed** per sitemap
   file; the same caps apply to a sitemap index (max 50,000 sub-sitemap entries). At ~190
   URLs the site is roughly **0.4% of the URL-count threshold** — a single flat
   `sitemap.xml` remains correct; a sitemap index is not warranted until multiple orders
   of magnitude more routes exist.
4. **Client-side search and duplicate content**: the duplicate-content/crawl-budget risk
   from search only exists when a search feature produces server-rendered, crawlable,
   query-string result URLs that get indexed as thin/duplicate pages. Pagefind here runs
   entirely client-side via a JS import with no server-rendered result routes — there is
   nothing for a crawler to discover or index, so no Disallow rule is warranted. This
   would change if the project ever added a server-side search route emitting indexable
   URLs.

## Conclusion

No real gap found. At current and near-future scale (hundreds, not tens of thousands, of
routes; a purely static export; a client-side-only search widget with no crawlable
result URLs; report/signal pages each reachable via exactly one canonical path), the
existing `robots.ts` (allow-all, no crawl-delay, no disallow rules) and `sitemap.ts`
(single flat sitemap) remain appropriate and match current Google/Next.js guidance.

The one asymmetry worth naming for future reference (not fixed here, since it is not
current duplicate-content risk): report pages set an explicit `alternates.canonical` in
metadata, signal pages do not. This is inert today because neither page type has more
than one reachable path, but if signal pages ever become reachable via more than one URL
(e.g. an alias, a query-param variant, or a future taxonomy-based route), canonical tags
should be added to `signals/[slug]/page.tsx` at that time, following the existing pattern
in `reports/[date]/page.tsx`.

## Validation

- `cd web && npx tsc --noEmit` — clean (baseline, before this audit; no code changed).
- `npx eslint .` — clean (baseline, before this audit; no code changed).
- `npm run build` — succeeded; confirmed 78 report routes + 96 signal routes + static
  pages via build output and Pagefind's "Indexed 186 pages" postbuild log.

No files were modified as part of this audit — `robots.ts` and `sitemap.ts` were read
only, not edited.
