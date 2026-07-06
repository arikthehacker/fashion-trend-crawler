# Agent log: /timeline page

Implemented the `/timeline` recommendation from `docs/agent-logs/signals-timeline-design.md`
(frontend only — did not touch `report_schema.py` or `data/reports/*.json`, left for the
concurrent `signal_id` agent).

## Changes

- `web/lib/reports.ts`: added `TimelineEntry` interface and `getTimelineEntries()`, which
  flattens `top_signals` from every report (via existing `getAllReports()`) into a flat list
  of `{report_date, signal_name, type, source_sectors, confidence}`. No `signal_id` used —
  keys only on name + date per instructions, since that field doesn't exist yet.
- `web/app/timeline/page.tsx` (new): plain reverse-chronological index grouped by report
  date, each date heading linking to `/reports/[date]`, with rows of signal name / type /
  confidence. No graph, no sparkline, no ranking language — matches the NYT/Pitchfork-style
  plain-index recommendation in the design doc and the archive page's visual conventions
  (masthead, red kicker, Instrument Serif heading, Libre Franklin body, `--border` rules).
- Nav wiring: added a "Timeline" link to the homepage nav bar (`web/app/page.tsx`), to the
  archive page footer (`web/app/archive/page.tsx`), and to the per-report footer
  (`web/app/reports/[date]/page.tsx`, alongside the existing "Full archive" / "Current
  report" links).

## Verification

`cd web && npx tsc --noEmit` — clean, no errors.
`npx next build` — succeeded; route table includes `○ /timeline` (static) alongside the
other static routes.

## Not done (out of scope)

- No signal-identity/recurrence matching (the visual "rule marking repeat signals" from the
  design doc) — that depends on the `signal_id` field being added by the other in-flight
  agent. Left as a follow-up once that field lands.
- `/signals/[slug]` — design doc recommends holding until 4-5 reports exist.
