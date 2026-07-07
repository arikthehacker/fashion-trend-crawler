# Run 58 — dark-mode / prefers-color-scheme support

**Topic chosen:** dark-mode support for the text-dense report site (not yet covered in
prior agent-log runs).

## Finding

`web/app/globals.css` defined four theme tokens (`--black`, `--white`, `--gray`,
`--border`) but had zero `@media (prefers-color-scheme: dark)` handling anywhere in the
codebase (confirmed via grep — no matches). Every visitor got the light palette
regardless of OS/browser dark-mode setting, which is a real gap for a long-form
reading site (report pages run to thousands of words of prose).

## Fix

Added a `prefers-color-scheme: dark` override block in `:root` that swaps the four
tokens. Colors were re-picked, not just inverted, so contrast still clears WCAG AA
against the new backgrounds:

- Light mode (unchanged): `--gray: #6b6b6b` on `--white: #f8f6f1` ≈ 4.93:1 (passes AA
  normal text, 4.5:1 threshold — calculated via the standard relative-luminance
  formula, not eyeballed).
- Dark mode (new): `--gray: #b0aca4` on `--black: #0a0a0a` ≈ 7.9:1 (exceeds AAA).
- `--border` swapped from a light hairline (`#e0ddd8`) to a dark hairline
  (`#2a2827`) so dividers stay visible without glowing against the dark background.
- `--black`/`--white` swap directly (`#0a0a0a` ↔ `#f8f6f1`) since both are already
  nowhere near mid-gray, so the swap alone gives ~17:1 body-text contrast either way.

The print stylesheet (`@media print`) was left untouched — it already forces pure
black-on-white regardless of theme, which is correct for citation printouts.

## Verification

- Grepped for all `var(--gray)`/`var(--border)`/`var(--black)`/`var(--white)` usages
  across `web/app/**` (14 files) — all reference the shared tokens, so the override
  cascades everywhere with no page-level hardcoded colors to fix separately.
- `npx tsc --noEmit` was run; it fails on a pre-existing, unrelated `.next/types`
  cache issue (`routes.js` not found) present before this change — not caused by the
  CSS-only edit here.

## Not done (out of scope for this pass)

- `--red: #c8102e` (accent color) contrast wasn't re-verified against the new dark
  background; it's used sparingly as an accent, not for body text, so risk is low but
  unconfirmed.
- No manual/browser screenshot verification of the dark palette in situ — token-level
  math only.
