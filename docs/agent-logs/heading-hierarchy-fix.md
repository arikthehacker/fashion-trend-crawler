# Heading hierarchy fix

Fixed the WCAG heading-hierarchy issue flagged in
`docs/agent-logs/accessibility-seo-research.md`: section labels were styled
`<p>` tags instead of real headings, breaking screen-reader outline navigation.

Scope: only `web/app/reports/[date]/page.tsx`, `web/app/signals/[slug]/page.tsx`,
`web/app/timeline/page.tsx` — no other files touched.

## Changes

- **reports/[date]/page.tsx**: existing `<h1>` (report date) kept. Promoted all
  `labelStyle` section labels ("Executive Summary," "Source Sectors,"
  "Observed Signals," "Repeated Keywords," "Garments, Silhouettes, Materials,
  Colors," "Aesthetic & Cultural References," "Notes," "Limitations,"
  "Archive Tags") from `<p>` to `<h2>`. Promoted subsection labels
  ("Garments"/"Silhouettes"/"Materials"/"Colors," "Aesthetic Terms,"
  "Cultural References") from `<p>` to `<h3>`. Also promoted the non-linked
  signal-name fallback (`{i+1}. {signal.name}`) from `<p>` to `<h3>` since it
  labels each signal subsection just like its linked sibling does.
- **signals/[slug]/page.tsx**: promoted "Recorded Occurrences" label to `<h2>`
  and each per-occurrence report-date label (inside the `Link`) to `<h3>`.
- **timeline/page.tsx**: promoted each per-date group label (inside the
  `Link`) from `<p>` to `<h2>`.

All changes preserve exact existing `style={...}` objects/classNames — tag
only, no visual or text-content change. No new sections added.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 29
routes generated successfully.

Note: while working, another agent's concurrent SEO edits (JSON-LD /
`generateMetadata` additions) appeared in `reports/[date]/page.tsx` — those
are unrelated to this task and were left untouched.
