# THIS WEEK'S INDEX module (doc §27/§28)

Built the condensed metrics module identified as missing in
`docs/agent-logs/full-doc-reread-run19.md`. Doc §27 frames the whole site
around an AQI/stock-index behavioral thesis and specifies this exact module:

> THIS WEEK'S INDEX
> sources scanned: 12
> items collected: 25
> top signal: sheer layering
> rising term: soft tailoring
> recurring material: lace
> dominant mood: restrained romanticism
> highest volatility sector: TikTok
> overall confidence: medium

§28 lists the underlying metric vocabulary (source count, item count, source
diversity, signal recurrence, signal volatility, editorial saturation, social
volatility, retail adoption, designer-origin clarity, archive recurrence,
confidence score, noise level) that the module's fields are meant to sample
from — the module itself picks 8 of those for a glanceable homepage box.

## What was built

- `getThisWeeksIndex()` in `web/lib/reports.ts` — derives all 8 fields from
  real report data, no hardcoding:
  - `topSignal`: latest report's first `top_signals` entry.
  - `risingTerm`: a `repeated_keyword` present this week absent last week
    (diffed against the prior report; not a subjective "trending" call).
  - `recurringMaterial`: a material appearing in >1 of the last 5 reports.
  - `dominantMood`: latest report's first `aesthetic_terms` entry; if the
    latest report has none (e.g. the NYFW-logistics-heavy 2026-09-14 window),
    walks backward to the most recent report that has one and flags
    `dominantMoodSourceDate` so the UI discloses it's carried forward rather
    than presenting stale data as current.
  - `highestVolatilitySector`: sums a volatility weight (flash=3,
    emerging/seasonal=2, recurring/declining=1, stable/dormant=0) across each
    signal's `source_sectors`; null if nothing this window is volatile.
  - `overallConfidence`: mode of `top_signals[].confidence` this window.
- Homepage module in `web/app/page.tsx`, inserted between the masthead and
  the existing latest-report teaser: a plain `<dl>` grid, same
  Franklin/Instrument type and uppercase-label wire-service styling as the
  rest of the site, no color/gauge/chart treatment. Every "no data" case
  (null field) renders a plain factual fallback sentence instead of hiding
  the row or faking a value.

Voice check: rising term is described as "new since last report," not
"trending" or hyped; dominant-mood carryover is disclosed rather than
silently presented as fresh.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean (57 routes
generated, no errors/warnings introduced).

Note: `/glossary` (the other run-19 gap) was already built by a concurrent
agent by the time this build ran — not touched here.
