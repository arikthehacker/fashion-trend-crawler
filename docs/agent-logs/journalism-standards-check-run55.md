# Run 55 — 404 / not-found page quality

**Topic chosen:** whether the site has a real custom 404 page or falls back to
Next.js's generic default. Not previously covered in agent-logs.

## Research

Next.js App Router convention: a `not-found.tsx` file at the app root (or nested)
is rendered automatically for any unmatched route and for explicit `notFound()`
calls. Without one, Next.js falls back to its built-in generic 404 — unstyled,
no site branding, no navigation back into the app. This is a well-documented gap
that affects both UX (dead end for users who mistype a URL or follow a stale
link, e.g. `/reports/<bad-date>`) and brand consistency for a site whose whole
identity is a deliberate print/wire-service voice.

## Finding

Checked `web/app/` — confirmed no `not-found.tsx` existed anywhere in the tree
(only `page.tsx`, `layout.tsx`, `icon.tsx` at the root, plus route folders).
Confirmed via `web/out/` build artifacts that this meant genuinely falling back
to the framework default. This was a real, concrete gap.

## Fix

Added `web/app/not-found.tsx`:
- Matches the homepage's masthead visual language (Instrument Serif for the
  numeral, Libre Franklin uppercase for labels/copy, CSS custom properties for
  color).
- Copy follows the project's voice rules (doc section 2): plain statement of
  fact ("No record exists at this address..."), no apology, no first person, no
  hype.
- Includes a nav back to Home / Archive / Search / About so a dead link doesn't
  strand a reader.
- Sets a page-specific `<title>` ("Not Found: ARI3LLA INDEX") consistent with
  the `<Title>: ARI3LLA INDEX` pattern used in `layout.tsx` metadata.

## Verification

`cd web && npx tsc --noEmit` — passed with no errors.

Not wired into CI; this is a static file picked up automatically by Next's
build via the file-convention, no other config changes needed.
