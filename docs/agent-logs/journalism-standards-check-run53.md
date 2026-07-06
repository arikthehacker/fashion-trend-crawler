# Journalism/professional-standards check — run 53: favicon / brand-identity completeness

**Topic:** Does the site have a real favicon, apple-touch-icon, or manifest — a
basic professional-site check never done in prior runs (confirmed against the
list of previously-covered topics in the ari3lla-index skill).

## Findings

Checked `web/app/` and `web/public/` for any icon/favicon/manifest file
(`favicon.ico`, `icon.*`, `apple-icon.*`, `manifest.json`/`manifest.ts`) —
**none existed**. `web/app/layout.tsx` sets full `metadata` (title, description,
OpenGraph, Twitter card, RSS alternate) but never touched icons, and there was
no file-based icon either. Confirmed via WebSearch that Next.js App Router
auto-detects file-based metadata icons (`favicon.ico`, `icon.png`/`icon.tsx`,
`apple-icon.png`) dropped directly in `app/`, and that omitting a favicon is a
real (if non-functional) polish gap: browsers show a blank/generic icon in
tabs and bookmarks, and some browsers/search engines surface the favicon in
bookmarks and search results — not purely cosmetic for a public research site
that positions itself as a professional index.

A `manifest.json` (PWA web-app-manifest) is confirmed optional for a
plain content site with no installability goal, so that was intentionally
**not** added — would be scope creep for a text-only editorial site.

## Fix applied

Added `web/app/icon.tsx` — a generated (no binary asset) 32x32 PNG favicon
using `next/og`'s `ImageResponse`: a black square with a white serif-weight
"A" (for ARI3LLA), matching the site's text-only-by-design aesthetic (same
constraint noted in the existing Twitter-card comment in `layout.tsx`). Next.js
auto-detects this file and injects the `<link rel="icon">` tag with no other
wiring needed.

## Verification

`cd web && npx tsc --noEmit` — passes clean, no errors.

Not verified: actual rendered favicon in a browser tab (would require
`next build`/`next dev`, out of scope for this quick check) — the file
follows the documented Next.js convention exactly, so runtime behavior should
match, but a follow-up run could do a `next dev` visual spot-check if
skepticism warranted.

## Scope note

Single, small, additive file. No other files touched. Not committed per
instructions.
