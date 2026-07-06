# Run 23 — frontend site health sweep

Browsed the site as a first-time visitor: homepage -> archive -> two report pages
(thin 2026-05-07, busy 2026-07-13) -> timeline -> a signal page -> glossary ->
search -> methodology -> about.

## Fixed directly

- **Search page was orphaned from primary navigation.** `/search` existed and was
  linked from the *footers* of `/archive`, `/timeline`, `/signals/[slug]`, and
  `/reports/[date]`, but was missing from the header "Site sections" nav on all
  seven pages that carry one (`/`, `/about`, `/methodology`, `/taxonomy`,
  `/sources`, `/glossary`, and implicitly the homepage). A first-time visitor
  landing anywhere except the four footer-linked pages had no way to discover
  search existed. Added a `Search` entry to the header nav array on all seven
  pages: `web/app/page.tsx`, `web/app/about/page.tsx`,
  `web/app/methodology/page.tsx`, `web/app/taxonomy/page.tsx`,
  `web/app/sources/page.tsx`, `web/app/glossary/page.tsx`.
- **Homepage header nav was missing `Glossary`.** Every other page's nav included
  it; the homepage's did not, so first-time visitors starting from `/` (the most
  likely entry point) couldn't reach the glossary except by clicking through to
  another page first. Added to `web/app/page.tsx`.

Both fixes are one-line array additions, consistent with the existing pattern
already used on other pages — no new components or design decisions.

## Verified consistent (no action needed)

- `/about` and `/methodology` claims about capabilities (source sectors,
  confidence/volatility, corrections, AI-assistance, thin-window handling)
  match what's actually implemented — schema fields, `getConsecutiveThinWeekCount`,
  `revision_history` correction rendering on report pages, etc. No stale claims
  found post-22-runs.
- Report pages: spot-checked an old thin report (2026-05-07) and a dense recent
  one (2026-07-13) — both render cleanly, `collection_status: "thin"` framing on
  the homepage teaser and the correction-history section both degrade gracefully
  when absent.
- Timeline, signal, glossary, and archive pages all cross-link correctly; no
  broken internal `href`s found.
- Note: while investigating, saw another concurrent agent actively editing
  `web/app/reports/[date]/page.tsx` / `web/lib/reports.ts` (adding
  `revision_history`/correction-history rendering) — did not touch those files
  per the shared-tree git safety rule; left them alone and confirmed the final
  state type-checks and builds clean.

## Flagged, not fixed (needs real design work)

- No sitewide design-system inconsistency found significant enough to flag this
  run — page structure (masthead / nav / content / footer) is applied uniformly
  across all 13 pages checked.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean (67 static
pages generated).
