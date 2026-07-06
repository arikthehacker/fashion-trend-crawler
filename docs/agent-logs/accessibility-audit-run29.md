# Accessibility audit — run 29 (full sweep, all pages)

Scope: every file under `web/app/**/*.tsx` (14 files), first full pass since
run 21 (which only covered glossary + homepage).

## Checks performed

1. **Styled-`<p>`-as-heading bug.** Grepped every `<p>` in the app and cross-
   checked each against the file's real `<h1>`-`<h3>` outline. Found one
   genuine instance: `web/app/case-study/page.tsx` — each numbered case-study
   section ("01 Concept & Scope", "02 Architecture", ...) was a styled `<p>`
   acting as that section's title, directly analogous to the fixed run-21 bug
   and to how `timeline/page.tsx` correctly uses `<h2>` for its date-group
   headers. Fixed: promoted to `<h2>` (kept all styling, added `fontWeight:
   "400"` and `margin: 0` to neutralize default heading browser styles, so
   appearance is unchanged). All other `<p>` instances checked (taxonomy row
   labels, archive/timeline list-row cells, kicker labels, body copy) are
   genuine data-row content or prose, not section titles — left as `<p>`.

2. **Image alt text.** No `<img>` or `next/image` usage anywhere under
   `web/app` — confirmed via grep. Site is text-only; nothing to fix.

3. **Color contrast.** `--gray: #6b6b6b` on `--white: #f8f6f1` (not pure
   white) computed to a WCAG contrast ratio of ~4.93:1 — passes AA (4.5:1)
   for normal text. `--black`/`--red` on `--white` both far exceed AA.
   No contrast issues found.

4. **aria-labels on interactive elements.** Every `<nav>` (site-sections nav,
   present on 8 of 9 top-level pages) has `aria-label="Site sections"`. Every
   facet `<select>` in `search/SearchClient.tsx` has an associated `<label
   htmlFor>`. Every landmark `<section>` across report/signal/search/timeline/
   archive/case-study pages has a descriptive `aria-label`. No gaps found.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 77
static/SSG routes generated successfully.
