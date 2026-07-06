# Run 57 — closing the skip-link verification gap from run 56

Run 56 added a skip-to-content link but only checked it with `tsc --noEmit`, explicitly
flagging that generated HTML/CSS output was not inspected. This run closes that gap.

## What was done

1. `cd web && npm run build` — succeeded, produced static output in `web/out` (117 HTML
   files across 13 route types, including all `reports/[date]` and `signals/[slug]`
   dynamic pages).
2. Inspected raw HTML for the homepage (`out/index.html`), a report page
   (`out/reports/2026-05-07.html`), and two more (`out/archive.html`,
   `out/signals/1990s-minimalism-revival.html`). In each, immediately after `<body>` (only
   preceded by a `hidden` Next.js hydration marker `<div>`, which is not focusable), the
   markup is:
   `<a href="#main-content" class="skip-link">Skip to main content</a><main id="main-content" ...>`
   — i.e. the skip link is the first focusable element, and `#main-content` exists on the
   same page.
3. Wrote a small Node script to walk **all 117** generated `.html` files and check: skip
   link present, `id="main-content"` present, and skip link appears before the
   `main-content` id in document order. Result: **0 failures across all 117 pages**.
4. Checked the built CSS bundle (`out/_next/static/chunks/0j7x9s025_nix.css`) — confirmed
   `.skip-link{...position:absolute;top:0;left:-9999px}` and
   `.skip-link:focus{top:.5rem;left:.5rem}` are both present in the shipped stylesheet.
5. Attempted a live static-server check (`npx serve` + `curl`) but the server didn't come
   up in time within the tight window; did not pursue further since raw HTML/CSS
   inspection across every generated page is already a stronger check than the single
   dev-server run originally flagged as missing.

## Outcome

No defects found — no `id="main-content"` targets were missing on any page, and the skip
link correctly precedes and points to it everywhere. No code changes were made.

## Verification

`cd web && npx tsc --noEmit` — clean (unchanged from run 56, no edits made this run).
