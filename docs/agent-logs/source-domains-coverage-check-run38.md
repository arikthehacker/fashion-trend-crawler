# source_domains coverage check across other signal-showing pages (run 38)

Followed up on run 37's `source_domains` wiring (report page only) by checking
whether the other pages that show per-signal detail should also render it.

## Checked

- `web/app/page.tsx` (homepage) — top-signal teaser cards show only
  `name`/`evidence` from a condensed `TopSignal` shape, no sectors/domains
  anywhere on this page today. Not a natural fit; adding source detail to a
  homepage teaser would be scope creep beyond the module's condensed intent.
- `web/app/timeline/page.tsx` — rows show name/type/confidence only, no
  evidence, no sectors, no per-occurrence detail at all. Not a natural fit.
- `web/app/search/SearchClient.tsx` — result rows show
  date/name/confidence/volatility; sectors are used only as a filter facet,
  never rendered per-row. Adding domains here would be the first per-row
  source detail on a page designed as a compact scanning list. Not a natural
  fit.
- `web/app/signals/[slug]/page.tsx` — **natural fit, added.** This page
  already renders full per-occurrence detail (confidence, volatility,
  `source_sectors`, evidence, index_note, human_editor_note) pulled from the
  full `Signal` object via `getSignalHistory()` in `lib/reports.ts`, which
  already includes `source_domains?: string[]` (confirmed at line 32).

## Change made

`web/app/signals/[slug]/page.tsx`: added a `Sources: {domain, domain}` span
to the existing per-occurrence metadata row, immediately after the Sectors
span, rendered only when `signal.source_domains` is non-empty — same
additive, no-new-heading pattern as run 37's report-page change.

## Verification

- `cd web && npx tsc --noEmit` — passed.
- `cd web && npx next build` — succeeded, all 91 pages generated (including
  all 45 `/signals/[slug]` static paths). Console warnings are pre-existing
  glossary `DEFINITIONS` gaps, unrelated to this change.

## Files touched

- `C:\Users\User\Desktop\fashion-trend-crawler\web\app\signals\[slug]\page.tsx`
