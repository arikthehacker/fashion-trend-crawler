# Facet filtering implementation

Implements the simpler half of `search-discoverability-design.md`: client-side
facet filtering only. Full-text search over report prose (Pagefind) is
deliberately deferred — it's a real build-step dependency addition (postbuild
`pagefind --site out` + indexing decisions) that deserves its own scoped run,
not bundled into this one.

## Changes

- `web/lib/reports.ts`: added `SearchableSignal` interface and
  `getSearchIndex()`, mirroring `getTimelineEntries()`'s flatten pattern.
  Flattens every signal across all reports (not deduped by `signal_id`) with
  `name`, `signal_id`, `report_date`, `source_sectors`, `confidence`,
  `volatility`, `origin_classification`, `evidence`, `index_note`.
- `web/app/search/page.tsx` (new): server component, masthead + intro copy in
  wire-service voice, calls `getSearchIndex()` and passes it to the client
  component. Static — no props beyond the pre-built array.
- `web/app/search/SearchClient.tsx` (new): `"use client"` component. Three
  `<select>` dropdowns (source sector, confidence, volatility) built from the
  index's own distinct values, exact-match filtering via `useMemo`/`useState`,
  no library. Results list mirrors `/timeline`'s row layout (date, name
  linking to `/signals/[slug]` when a `signal_id` exists, confidence,
  volatility). Empty state: "No signals on file match this combination of
  filters."
- Added "Search" links to the `/archive` and `/timeline` footers for
  discoverability.

## Not touched

`web/lib/trends.ts` and `web/app/page.tsx` — per instructions, unrelated
pending decision.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both clean. `/search`
prerenders as static content (○), consistent with the rest of the site's
static export.

## Scope note for later

Pagefind full-text search over `executive_summary`, `limitations`,
`cultural_references`, etc. remains the second half of the original proposal
— add as a postbuild step (`next build && pagefind --site out`) in a
dedicated run, per this project's convention of disjoint-file agent scoping.
