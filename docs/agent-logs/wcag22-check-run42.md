# WCAG 2.2 delta check — run 42

Checked the new WCAG 2.2 (Oct 2023) success criteria against the current site,
beyond the WCAG 2.1 AA work already done in runs 5, 20-22, 29.

**Not applicable** (static, read-only archive, no forms/auth/drag): 2.5.7
Dragging Movements, 3.2.6 Consistent Help, 3.3.7 Redundant Entry, 3.3.8
Accessible Authentication.

**2.4.11 Focus Not Obscured** — checked for any `position: sticky`/`fixed`
element across `web/app/**`. None exist anywhere in the codebase (grep for
`position:\s*(sticky|fixed)` returned zero matches), so no element can ever
obscure a focused control during keyboard nav. Passes trivially.

**2.5.8 Target Size Minimum (AA)** — found a genuine violation and fixed it.
The site-section `<nav>` (Report/Methodology/Taxonomy/Sources/Glossary/
Timeline/Archive/Search/About/Case Study) is duplicated identically across
`web/app/page.tsx`, `about/page.tsx`, `sources/page.tsx`, `taxonomy/page.tsx`,
and `glossary/page.tsx`. Each `<Link>` used `fontSize: "0.7rem"` with no
padding, giving a clickable target roughly 13-16px tall — under the 24 CSS-px
minimum, with no exception applicable (not inline sentence text, no
equivalent larger control offered, presentation not essential). The 1.5rem
gap between items doesn't rescue it since the spacing exception requires an
uncovered 24px circle centered on the target, which vertical padding alone
doesn't provide either — so this needed a real fix, not just a spacing
argument.

Fix: added `display: "inline-block", padding: "0.65rem 0"` to each nav
`<Link>`'s style object in all 5 files, bringing the clickable box to
~34px tall (well over 24px) without changing the visible text size or
layout. Left the single inline "Read the full report" link on the homepage
(`page.tsx` line ~300) untouched — it sits inside a sentence-style paragraph
and qualifies for the Inline exception.

**Verification:** `cd web && npx tsc --noEmit && npx eslint .` — both clean,
no errors.

**Files touched:** `web/app/page.tsx`, `web/app/about/page.tsx`,
`web/app/sources/page.tsx`, `web/app/taxonomy/page.tsx`,
`web/app/glossary/page.tsx`.
