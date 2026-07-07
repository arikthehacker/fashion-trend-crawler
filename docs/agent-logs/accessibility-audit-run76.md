# Accessibility audit — run 76

Scope: first dedicated accessibility pass since the skip-link (run 57) and dark-mode
`prefers-color-scheme` support were added. Prior audits (runs 68, 71) covered journalism
standards (corrections visibility, sourcing conventions), not accessibility.

## Research: WCAG 2.1/2.2 AA criteria relevant to this site

Researched against a content-heavy archival/news site profile rather than a generic
checklist:

- **1.3.1 Info and Relationships (A)** — heading levels must reflect document structure;
  a visually heading-styled element that isn't a real heading tag breaks screen-reader
  "jump by heading" navigation, a documented recurring bug class for this project (see
  `check_heading_patterns.py`, SKILL.md workflow note #3).
- **2.4.6 Headings and Labels (AA)** — headings/labels must describe topic/purpose.
- **1.4.3 Contrast (Minimum) (AA)** — 4.5:1 for normal text, 3:1 for large text/UI
  components, in *both* light and dark palettes since this site auto-switches via
  `prefers-color-scheme`.
- **2.4.4 Link Purpose in Context (A)** — link text must be understandable from itself or
  its immediate context; relevant to this site's per-signal "#" permalink and "Full
  archive"/"Timeline" style nav links.
- **4.1.2 Name, Role, Value (A)** — custom interactive widgets (Pagefind mount, facet
  `<select>`s) need correct semantics/labels, not just visual affordance.
- **2.4.3 Focus Order / 2.1.1 Keyboard (A)** — all interactive elements reachable and
  operable via keyboard, not just the skip-link.

## Audit performed

**1. Heading hierarchy** — checked `app/reports/[date]/page.tsx`, `app/archive/page.tsx`,
`app/search/SearchClient.tsx`.

Archive and search pages: h1 → h2 pattern, consistent, no skips.

Report page: `<h1>` (date) → `<h2>` per major section (Executive Summary, Source Sectors,
Observed Signals, etc., all via shared `labelStyle`) → `<h3>` for signal names and for the
Garments/Silhouettes/Materials/Colors and Aesthetic/Cultural subheads. **Found a real
violation here**: in the "Observed Signals" loop, each signal name is rendered at
identical h3-scale styling in both branches of a conditional, but only actually wrapped in
an `<h3>` tag when `signal.signal_id` is absent. When `signal_id` is present (the common
case — most signals link to `/signals/[slug]`), the same-looking title was a bare
`<Link>` with no heading element at all. Net effect: for most reports, most signal titles
were invisible to screen-reader users navigating by heading, despite being visually
indistinguishable from the ones that *were* real headings — a heading-hierarchy
consistency bug (1.3.1 / 2.4.6), and notably the *inverse* of this project's previously
known bug pattern (styled-`<p>`-as-heading): here it's a styled-non-heading masquerading
as a heading.

**Fix applied** (`web/app/reports/[date]/page.tsx`): wrapped the linked-signal-name branch
in a real `<h3>`, keeping the `<Link>` inside it for the click target/styling, so both
branches now produce an actual heading element at the same level. Minimal diff, no visual
change (same font, size, color, spacing).

**2. Color contrast** (`app/globals.css`) — computed relative-luminance contrast ratios by
hand for the highest-risk pairing (`--gray` body text on `--white`/`--black` backgrounds,
since gray-on-background is used for all metadata/notes throughout report pages):

- Light mode: `--gray #6b6b6b` on `--white #f8f6f1` ≈ **4.94:1** — passes 4.5:1 AA for
  normal text.
- Dark mode: `--gray #b0aca4` on dark background `#0a0a0a` — the in-file comment
  (globals.css lines 14-21) already documents this at ≈7.9:1, comfortably passing; spot
  checked the arithmetic and it holds.
- `--black`/`--white` body text pairs are near-maximum contrast in both modes (well over
  AA/AAA).
- `--border` is intentionally a low-contrast hairline (decorative divider, not text) —
  correctly exempt from the text contrast requirement.

No violation found. The dark-mode palette was evidently already contrast-vetted when it
shipped (comment explicitly cites a recomputed, not just inverted, gray/border pair).

**3. Interactive elements / ARIA** — checked `app/search/SearchClient.tsx` (facet filters
+ Pagefind mount) and `layout.tsx` (skip link).

- Facet `<select>` elements each have a proper `<label htmlFor>` pointing at a matching
  `id` (`filter-sector`/`filter-confidence`/`filter-volatility`) — correct native
  labeling, no ARIA needed.
- Pagefind mount point (`#pagefind-search`) is a plain `<div>`; Pagefind's own UI bundle
  (external, not this repo's code) is responsible for the search input's accessible name
  and result semantics — outside this audit's scope to modify.
- Skip link (`layout.tsx` / `.skip-link` in globals.css) uses standard `position:
  absolute; left: -9999px` + `:focus` reveal pattern, targets `#main-content` which exists
  on every page's `<main>` — previously verified across all 117 pages (run 57 log). No
  toggle/dark-mode switch exists to check (dark mode is OS-preference-driven only, no
  manual control, confirmed in `layout.tsx`/`globals.css`).

No ARIA violations found in this repo's own markup.

**4. Link Purpose in Context (2.4.4)** — spot-checked repeated nav link text ("Full
archive", "Timeline", "Search", "Current report", "Corrections & AI use" — same footer
across archive/report pages) and the per-signal "#" permalink anchor. The bare "#" anchor
carries `aria-label="Permalink to signal: {signal.name}"` (`reports/[date]/page.tsx` line
386), so its accessible name is fully descriptive despite the terse visible glyph — this
matches the AA recommendation for icon-only links. Footer nav links are short but
unambiguous in isolation (standard site-chrome labels, not "click here"/"read more"
patterns) — no violation.

## Outcome

One real violation found and fixed: inconsistent heading semantics for signal titles on
report pages (fixed in `web/app/reports/[date]/page.tsx`). Contrast, ARIA/interactive
semantics, and link-purpose checks came back clean. Verified via `npx tsc --noEmit`,
`npx eslint .`, and `npm run build` (full static export + Pagefind postbuild) — all passed
with no new errors/warnings introduced.
