# THIS WEEK'S INDEX placement decision

## Decision

Does NOT belong duplicated on `/archive` as a full metrics module. Added only
a one-line navigational pointer instead (implemented in
`web/app/archive/page.tsx`).

## Reasoning

Doc §27 frames THIS WEEK'S INDEX around a "what would people check
daily/weekly" thesis — explicitly a live, current-moment glance (weather/AQI
analogy), not a per-week historical artifact. `/archive`'s own copy says the
opposite: "a historical record... each entry reflects the source material
collected during its stated window and is **preserved as issued**." Those two
framings conflict if merged: showing a live "current index" box inline with a
list of frozen past weeks implies every entry should carry one, or that the
box itself is historical, which it isn't (its `risingTerm`/`dominantMood`
fields are diffed against "last report" and only make sense as "now").

Rather than skip the connection entirely, added a small text pointer above
the report list linking to `/` and labeling it explicitly as the "current
snapshot... rather than the historical record" — this serves the real user
need (someone landing on the archive may actually want the live index) without
misrepresenting the module as archival content or duplicating 8 fields that
already live on the homepage via `getThisWeeksIndex()`.

## What was touched

- `web/app/archive/page.tsx`: imported `getThisWeeksIndex` from
  `web/lib/reports.ts` (already exported, no changes needed there), added a
  conditional one-line pointer before the report list section.
- `web/lib/reports.ts`: untouched (read-only, confirmed `getThisWeeksIndex()`
  already exported by the prior module build).

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean, 65 routes
generated, no new errors/warnings.
