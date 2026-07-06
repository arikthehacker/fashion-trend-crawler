# Signal history page — close-out correction display check

**Finding:** `web/app/signals/[slug]/page.tsx` rendered `signal.evidence` and
`signal.index_note` per occurrence, but did not render `signal.human_editor_note` at all.
This is a distinct gap from the report-level Correction History section added in run 23
(`web/app/reports/[date]/page.tsx`) — that surfaces `revision_history` on the report page,
but a reader landing directly on a signal's longitudinal history page (e.g.
`/signals/off-duty-varsity`) saw no trace of the editorial close-out reasoning
(`human_editor_note`) explaining why that signal's occurrence history ends where it does.
Confirmed by reading the actual component, not by inference — `human_editor_note` only
appeared in `web/lib/reports.ts` typing, never in a `.tsx` render.

**Fix applied:** added a conditional block after the existing `index_note` paragraph in the
occurrence list, rendering `signal.human_editor_note` under a real `<h4>` heading ("Editorial
Close-Out") rather than a styled `<p>` masquerading as a heading — per SKILL.md's recurring
styled-`<p>`-as-heading caution. Scoped to the single occurrence card; unaffected signals
without the field render nothing extra.

**Verification:** `cd web && npx tsc --noEmit && npx next build` — both passed clean, all 83
routes generated including the affected `/signals/[slug]` pages (off-duty-varsity,
layered-tops-styling, peplum-waist-revival, versace-mulier-debut-timing-unconfirmed,
armani-post-founder-transition-continues, poetcore-aesthetic among the 39+ signal slugs
built).

**Not done:** did not commit (per instructions). Did not touch
`reports/[date]/page.tsx` or any other file.
