# Run 63 — archival deep-linking: per-signal anchors within a report page

**Topic:** does the site support linking to a specific signal WITHIN a dated
report page (an anchor), or only to the whole page?

## Finding: real gap, now fixed

Before this run, `reports/[date]/page.tsx` had exactly one in-page anchor
target (`#correction-history`, added for the correction-notice link). Every
"Observed Signal" block — the actual citable unit inside a report — had no
`id`, so the only durable links available were: (a) the whole report page, or
(b) the signal's own `/signals/[slug]` longitudinal page (a different page,
tracking recurrence across reports, not "this signal as it appeared in this
specific dated report"). A reader wanting to cite "the third finding in the
07-06 report" had no URL for that — only "see the whole report and scroll."

Quick web check confirmed this is standard deep-linking/permalink practice
for long-form content with addressable sub-items (anchor ids per
section/finding so readers can link to one item without exhuming the whole
document) — not a novel requirement, closer to baseline expectation for an
archival index whose whole premise is citable, dated records.

## Fix

`web/app/reports/[date]/page.tsx`: each signal block now gets
`id={`signal-${signal.signal_id || i}`}` (falls back to index for older data
without a `signal_id`), plus a small visible `#` permalink anchor next to the
signal heading (`href="#signal-..."`, `aria-label` names the signal) so the
anchor is discoverable, not just present in markup.

`web/app/globals.css`: added `[id^="signal-"] { scroll-margin-top: 1.5rem; }`
so an anchored jump doesn't land the signal flush against the viewport edge.

Verified: `cd web && npx tsc --noEmit` — clean, no errors.

## Scope note

Did not touch `/signals/[slug]/page.tsx` (the longitudinal per-signal page) —
that page's own citability was out of scope; this run only closed the gap on
the dated-report page itself, per the assigned scope.
