# Design note: /signals/[slug] and /timeline (not implemented)

## 1. Is 3 reports enough?

Borderline — lean toward waiting one more cycle. Checked `data/reports/*.json`:

- 2026-05-07 → Sheer layering, Soft tailoring, Archival romanticism
- 2026-07-06 → Sheer layering, Soft tailoring, 1990s minimalism revival, Micro-bag styling
- 2026-07-13 → Quiet luxury backlash/maximalist pivot, 1970s boho revival, Resale growth,
  Menswear aspirational realism, Layered tops (social), Coastal-cowgirl evolution,
  Textured maximalist layering

Only two exact-name repeats ("Sheer layering", "Soft tailoring", both across the first two
dates), and the third report renames/reframes similar territory ("Textured maximalist
layering," "Layered tops") without reusing the exact `name` string. `top_signals[].name` is
freeform text, not a controlled vocabulary — there's no slug/id field in `report_schema.py`
today, so recurrence can't be detected by exact match alone; it needs fuzzy/editorial
linking. Building `/signals/[slug]` now would mean either (a) shipping a page with 2 real
entries and calling it a feature, or (b) inventing a matching heuristic under-tested against
real data. `/timeline` is lower-risk (it doesn't require signal identity matching, just
chronological display) and could be built sooner. Recommendation: hold `/signals/[slug]`
until 4-5 reports exist and a `signal_id`/slug field is added at summarize-time; `/timeline`
could go first as a stepping stone.

## 2. Data layer additions needed (`web/lib/reports.ts`)

- Add `signal_id?: string` to the `Signal` schema (`report_schema.py`) — assigned by
  `summarize.py` or a human editor note, not inferred at read time. Until that exists,
  timeline/signals pages must key on normalized `name.toLowerCase().trim()`, which is
  fragile (see above).
- New functions: `getAllSignalsAcrossReports(): {report_date, signal}[]` (flatten all
  reports' `top_signals` with their date), `getSignalHistory(slug: string)` (filter by
  normalized name/id), `getTimelineEntries()` (all reports, sorted, with signal counts per
  date for a summary strip).

## 3. Wireframe in prose

`/timeline` — reverse-chronological list of report dates as sections (like `/archive` but
denser); under each date, a compact row per signal (name, type, confidence badge, one-line
evidence snippet), linking to `/reports/[date]#signal-anchor`. A thin visual rule (not a
graph) marks where a signal's name matches one from a prior date. No sparkline/chart —
wire-service register, not an analytics dashboard.

`/signals/[slug]` — header with the signal name and first-seen date; a plain chronological
list of appearances (date, source_sectors, confidence, volatility, evidence, index_note per
occurrence); a short "editorial note on continuity" field (human-written, not generated) if
the name changed across appearances. No forecast, no "rising/falling" arrow — state what
recurred and where, let the reader infer trajectory.

Inspiration taken loosely from NYT topic pages (chronological list, no editorializing chrome)
and Pitchfork genre pages (plain index, not a dashboard) — explicitly not Google Trends'
graph-forward style, which reads as hype/forecasting and conflicts with project voice.

## 4. Status

This is a recommendation only for the next loop run. No code, schema, or page files were
changed as part of this task.
