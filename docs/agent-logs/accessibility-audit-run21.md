# Accessibility audit — run 21 (glossary + homepage "This Week's Index")

Scope: `web/app/glossary/page.tsx` and `web/app/page.tsx` only, checked against
the same WCAG standard as run 5's heading-hierarchy fix
(`docs/agent-logs/heading-hierarchy-fix.md`).

## Findings and fixes

**glossary/page.tsx** — heading hierarchy was already correct (single `<h1>`
"Glossary", no other headings needed). The actual issue was definition-list
semantics: the term/definition pairs were rendered as plain `<div>`/`<p>`
grid rows with no `<dl>`/`<dt>`/`<dd>` despite being a literal glossary.
Fixed: wrapped the entries in `<dl>`, changed the term `<p>` to `<dt>` and the
definition `<p>` to `<dd>`. Row-level `<div>` wrappers (grid layout) and all
styling preserved exactly.

**page.tsx (homepage)** — the new "This Week's Index" module used a styled
`<p>` as its section label ("This Week's Index — {date}") — the exact
run-5 bug pattern (styled `<p>` pretending to be a heading). Promoted to
`<h2>`. While checking the rest of the page for consistency, found two more
instances of the same pattern outside the new module: the "Latest Report —
{date}" label (promoted to `<h2>`) and each top-signal card's name (was `<p
font-instrument>`, promoted to `<h3>`, since it labels a signal subsection
under the Latest Report `<h2>` just like the module's dt/dd row headers).
Resulting outline: h1 (masthead) → h2 (This Week's Index) / h2 (Latest
Report) → h3 (per-signal name). No new sections, no visual/style changes
beyond tag swaps (kept existing `style` objects, added `margin: 0` /
`fontWeight: "400"` only where needed to neutralize default `<h2>`/`<h3>`
browser styling so appearance is unchanged).

The "This Week's Index" module's `<dl>` (metrics grid) was already using
correct `<dt>`/`<dd>` semantics — no non-text visual elements, so no
alt-text/aria-label gaps.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all
routes generated successfully (ran tsc and build separately since another
concurrent agent held a build lock momentarily; both commands were verified
against the final file state).
