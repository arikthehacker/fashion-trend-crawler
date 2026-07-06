# Search / faceted discoverability — research + design proposal

Status: research + design only, nothing implemented. For a future dedicated run.

## Problem

The site (`web/app/archive`, `/timeline`, `/signals/[slug]`) is browse-only:
chronological lists, no way to ask "every report mentioning denim" or "every
high-confidence, low-volatility, designer-origin signal." All pages are built
via `generateStaticParams()` (confirmed in `web/app/reports/[date]/page.tsx`
and `web/app/signals/[slug]/page.tsx`) — fully static export, no server/API
route to run search queries against at request time.

## Research

**Client-side static search options** (no backend, works with Next.js static
export):
- **Pagefind** — indexes already-rendered HTML post-build (`pagefind --site
  out`), ships the index as static files served from the same CDN, ships no
  UI of its own. Zero Node/PHP backend needed; works on GitHub Pages/Netlify/
  Cloudflare Pages. Best fit for full-text search across report prose
  (executive summaries, index_notes, evidence text) because it indexes
  rendered content rather than requiring a hand-built document array.
  ([petemillspaugh.com](https://www.petemillspaugh.com/nextjs-search-with-pagefind), [staticsignal.io](https://staticsignal.io/posts/static-site-search-with-pagefind/))
- **lunr.js / Fuse.js** — client-side JS libraries that search a JSON index
  you build yourself and ship as a static asset, loaded and queried in the
  browser. More control over the exact document shape (e.g. attaching
  structured facet fields per signal) but requires hand-rolling the index
  build step and UI, unlike Pagefind's automatic HTML indexing.

**Faceted search in archival/library science**: faceted navigation over
controlled-vocabulary metadata is a well-established discovery pattern
(Ranganathan's 1933 colon classification is the origin point), shown to
improve discoverability by exposing structured attributes users wouldn't
think to search by name. The literature also warns that facets expose
metadata quality problems — vocabulary must be maintained and applied
consistently or facets become misleading. This maps directly onto this
project's `taxonomy.py` controlled vocabularies (source_sectors, confidence,
volatility, origin_classification) — they already are controlled vocabulary,
which is the precondition faceted search needs.
([tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/01639374.2023.2222120), [Wikipedia](https://en.wikipedia.org/wiki/Faceted_search))

## Proposal

**Combine both patterns rather than picking one:**

1. **Facet filtering (`/archive` enhanced, or new `/search`)** — a client
   component reading a pre-built static JSON index (small enough to inline or
   fetch once), with checkbox/toggle filters for `source_sectors`,
   `confidence`, `volatility`, `origin_classification`, and free-text over
   `name`/`index_note`/`evidence`. This is plain array filtering in the
   browser (no library needed) since the corpus is tiny (5 reports today,
   maybe hundreds of signals ever) — Fuse.js only earns its weight if
   free-text needs fuzzy matching later.
2. **Full-text search across report prose** — Pagefind, run as a postbuild
   step (`next build && pagefind --site out`), for searching
   `executive_summary`, `limitations`, `cultural_references` etc. that aren't
   structured per-signal. Complements facets rather than replacing them.

**Data shape needed in `web/lib/reports.ts`**: a new
`getSearchIndex(): SearchableSignal[]` mirroring `getTimelineEntries()`'s
flatten pattern, adding the fields timeline omits — `volatility`,
`origin_classification`, `evidence`, `index_note`, `report_date` — one entry
per signal occurrence (not deduped by `signal_id`, since the same signal
recurring across weeks is meaningful history, per `/signals/[slug]`'s
existing model). This flat array is what a client-side filter component would
receive as static JSON props; Pagefind would run independently over the
rendered HTML output.

**Scope note**: kept deliberately narrow here. Actual page layout, filter UI
component, and Pagefind build wiring should be their own scoped run per this
project's convention of disjoint-file agent scoping.
