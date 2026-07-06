# Agent log: /signals/[slug] page

Implemented the longitudinal signal history page recommended in
`docs/agent-logs/signals-timeline-design.md`, now unblocked by `signal_id`
existing on every Signal.

## Changes

- `web/lib/reports.ts`: added `signal_id?: string` to `TopSignal`, added
  `signal_id?` to `TimelineEntry` (populated in `getTimelineEntries()`), and
  added two functions: `getSignalHistory(slug)` (all occurrences of a
  `signal_id` across reports, sorted chronologically oldest-first) and
  `getAllSignalSlugs()` (distinct non-empty `signal_id` values across all
  reports, for static params).
- `web/app/signals/[slug]/page.tsx`: new page, following the exact
  `generateStaticParams`/`generateMetadata`/async-params pattern from
  `web/app/reports/[date]/page.tsx`. Renders signal name, first-seen date,
  occurrence count, then a plain chronological list per occurrence (date
  linking to `/reports/[date]`, confidence, volatility, source sectors,
  evidence, index note). No forecast/trend arrow, per the design doc.
  `notFound()` if slug has zero occurrences.
- `web/app/timeline/page.tsx`: signal name now links to `/signals/[signal_id]`
  when `signal_id` is present; falls back to plain text otherwise.
- `web/app/reports/[date]/page.tsx`: signal name/heading in "Observed
  Signals" now links to `/signals/[signal_id]` when present, plain text
  fallback otherwise (no crash on empty/missing `signal_id`, per older data).

Copy stayed in existing wire-service voice — no new hype language added,
no rising/falling framing.

## Verification

`npx tsc --noEmit` — clean. `npx next build` — clean; build output confirms
`/signals/[slug]` as an SSG route with paths including
`sheer-layering`, `soft-tailoring`, plus additional slugs from
`2026-07-13.json` (built concurrently by another agent; that file was not
edited here).

No commit made, per instructions.
