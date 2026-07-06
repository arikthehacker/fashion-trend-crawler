# Longitudinal signal tracking — research + audit (run 76)

## Question

Does the project already have adequate longitudinal signal tracking, or is
`/signals/[slug]` (flagged as a "later page" in early runs) still a gap?

## Finding: the page already exists

`web/app/signals/[slug]/page.tsx` shipped run 4 (per SKILL.md's file map) and
was still live and building at run 76. `getAllSignalSlugs()`/`getSignalHistory()`
in `web/lib/reports.ts` back it. `reports/[date]/page.tsx` links each signal
into its `/signals/[slug]` page (run 63, anchor-id work). So the "later page"
noted in doc section 40/SKILL.md's next-steps has already been built — this
research task itself is somewhat stale relative to current state.

## Research: how real trackers/timelines present a single tracked entity

- Wikipedia's own timeline guidance (`Wikipedia:Timeline`, `Wikipedia:Timeline
  standards`) recommends bulleted-list or table entries over prose paragraphs
  ("proselines" are discouraged), one entry per dated event.
- General knowledge of promise-tracker / live-story-tracker formats (e.g.
  PolitiFact-style trackers, NYT-style running trackers): a short status read
  near the top of the page (e.g. "In Progress" / "Stalled" / "Kept") so a
  reader doesn't have to scroll every dated entry to tell current state, plus
  a reverse- or forward-chronological list of dated updates below.
- FiveThirtyEight / Our World in Data: general search didn't surface
  page-design specifics (results were mostly org overviews), so this part
  is thin — noting the limitation rather than overstating confidence.

Sources: en.wikipedia.org/wiki/Wikipedia:Timeline, en.wikipedia.org/wiki/Wikipedia:Timeline_standards.

## Audit against that pattern

What the page already does well, matching the researched pattern:
- One dated entry per occurrence, reverse... actually chronological
  (oldest-first) — matches the "list of dated updates" pattern.
- Surfaces `evidence`, `index_note`, and `human_editor_note` per occurrence.
  Read against real data (`cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`
  across data/reports/2026-10-26.json .. 2027-01-04.json): the project's own
  editorial prose already does the "status" narration a real tracker would
  want (explicit "N consecutive windows", explicit
  `is_prolonged_silence()`-backed claims, explicit "untracked going forward
  pending new information" per SKILL.md workflow note 10). This is by design
  — SKILL.md/`is_prolonged_silence()`'s docstring are explicit that dormancy/
  resolution is an editorial judgment call belonging in prose, not a schema
  enum, so I did not add one.

Gap found: unlike a real tracker, the page had **no status read near the top**
— a reader had to open every occurrence and read through (in the CFDA case)
up to 11 paragraphs of `human_editor_note` to find out whether a signal is
still active or has gone quiet. `getSignalHistory()` had all the data needed
to state this as a plain, non-editorializing fact (how many published reports
have passed since the signal's last occurrence) but nothing computed or
surfaced it.

## What I implemented

- `web/lib/reports.ts`: added `getSignalRecencyStatus(slug)` — purely
  computed from existing `getSignalHistory()`/`getAllReports()` output, no
  new schema field, no Python change. Returns `{ lastSeen, isMostRecentReport,
  reportsSinceLastSeen }`.
- `web/app/signals/[slug]/page.tsx`: renders one extra header line: either
  "Appeared in the most recently published report." or "Last appeared
  `<date>` — N published reports since, with no further occurrence on file."

This deliberately does NOT introduce a "dormant/closed/active" verdict or
duplicate `is_prolonged_silence()`'s threshold logic in TypeScript — that
would either desync from the Python source of truth or preempt the editorial
judgment call the project has repeatedly and deliberately kept as prose
(SKILL.md note 10, `is_prolonged_silence()` docstring, and the run-76-era
`cfda-fashion-awards-2026` entries explicitly declining to add a new status
enum "without broader review"). It only states an unopinionated, already-true
fact the underlying data already supports.

Validated: `npx tsc --noEmit`, `npx eslint .`, `npm run build` — all clean,
169 pages generated including 83 `/signals/[slug]` paths.

## Not implemented / not needed

- A full "timeline of X" cross-signal comparison view: out of scope for this
  run and not clearly warranted — `/timeline` already gives the reverse-
  chronological cross-report index; `/signals/[slug]` already gives the
  single-signal deep view. No gap found that needs a third page type.
- Confidence-trajectory chart/sparkline: the existing per-occurrence
  confidence/volatility line already gives this in text form; a visual chart
  would be a legitimate future enhancement but is a "nice to have," not a bug,
  so left for a future run per the task's instruction not to rush scope.
