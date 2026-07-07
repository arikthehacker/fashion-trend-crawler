# Run 56 — keyboard-navigation / skip-link accessibility check

**Topic:** WCAG 2.4.1 (Bypass Blocks) — does the site let keyboard/screen-reader users
skip repeated navigation to reach main content? Distinct from the WCAG 2.2 target-size
work covered in an earlier run.

## Research

WCAG 2.4.1 (Level A) requires a mechanism to bypass blocks of content repeated across
pages (nav/header). The standard implementation is a visually-hidden "Skip to main
content" link, first in the DOM, that becomes visible on keyboard focus and jumps to
`#main-content`. This is one of the most common archival/publisher-site gaps because it's
invisible in normal mouse-driven QA — it only surfaces under actual keyboard testing.

## Findings against the current site

Checked `web/app/layout.tsx` (site-wide shell) and all 13 route pages. Every page already
has its own inline `<header>`/`<nav>` followed by a `<main>` — no shared nav component —
but there was no skip link anywhere, and no page's `<main>` had an `id` for a skip link to
target. This was a genuine, previously-unaddressed gap.

## Fix applied

- `web/app/layout.tsx` — added a `<a href="#main-content" className="skip-link">Skip to
  main content</a>` as the first element inside `<body>`, before `{children}`.
- `web/app/globals.css` — added `.skip-link` (positioned off-screen at `left: -9999px`)
  and `.skip-link:focus` (moves on-screen at `top/left: 0.5rem`) using existing
  `--black`/`--white`/`--font-franklin` tokens. Pure CSS, no client-side JS needed since
  `layout.tsx` is a server component (inline `onFocus`/`onBlur` handlers would have
  required `"use client"`, which was avoided).
- Added `id="main-content"` to the `<main>` tag on all 13 pages: `page.tsx`, `about`,
  `archive`, `case-study`, `glossary`, `methodology`, `not-found`, `reports/[date]`,
  `search`, `signals/[slug]`, `sources`, `taxonomy`, `timeline`.

## Verification

`cd web && npx tsc --noEmit` — clean, no errors.

Not verified: actual browser focus-visibility (no dev server run in this pass). CSS
positioning follows the standard skip-link pattern (`position: absolute`, huge negative
`left` when unfocused, `:focus` pulls it on-screen) so it should behave correctly, but a
manual Tab-key check in a running browser is recommended as a follow-up.
