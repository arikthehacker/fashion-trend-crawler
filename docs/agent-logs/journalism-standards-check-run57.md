# Run 57 — Document-level heading hierarchy check

**Topic:** WCAG/WAI heading hierarchy at the document level (distinct from the recurring
styled-`<p>`-as-heading bug already caught by `check_heading_patterns.py`) — does each page
have exactly one real `<h1>` and does h2/h3/h4 nesting skip levels?

**Standard checked (WAI Headings tutorial, WCAG 2.4.6 Understanding doc, TPGi, A11Y Project):**
- Prefer exactly one `<h1>` per page describing the page's content (not a hard WCAG failure
  to have more, but best practice).
- Don't skip ranks going deeper (h2 directly to h4) — skipping while *closing* a subsection
  back up is fine, only skipping while descending is the problem.

**Method:** grepped every real `<h1>`-`<h6>` usage across all 16 route files in `web/app/`
(not a visual/styled-div read — actual JSX heading tags) and traced the sequence per page.

**Findings — every page already conforms:**
- `about`, `methodology` (h1→h2), `glossary` (h1 only — term list correctly uses semantic
  `<dl>/<dt>/<dd>`, not headings), `timeline` (h1→h2), `search` (h1 only), `not-found`
  (h1 only), `case-study` (h1→h2), `archive` (h1→h2), `taxonomy` (h1→h2 x4), `sources`
  (h1→h2), homepage `page.tsx` (h1→h2→h2→h3, h3 correctly nested under the second h2),
  `reports/[date]` (h1→h2 x9 sections, each with h3 children where needed, no skips),
  `signals/[slug]` (h1→h2→h3→h4, fully sequential, no skips).
- `layout.tsx` contributes no headings, so no page gets an accidental duplicate h1 from
  shared chrome.
- No file has an h1→h3 or h2→h4 descending skip anywhere in the app.

**Conclusion:** no code change made. This is a real check (grep of actual JSX heading
elements, not visual review) and the site already meets the standard — glossary's use of
`<dl>` instead of fake sub-headings for term entries is specifically correct semantic
markup, not a gap. Nothing to fix this run.
