# Voice audit — web/app/**/*.tsx

Reviewed all page.tsx/layout.tsx files against doc section 2 (no first person,
no hype/"must-have"/"obsessed", no shopping recs, no TikTok-to-editorial
authority upgrade).

## Violation found and fixed

- `web/app/case-study/page.tsx`: "My Role" section header plus "Designed and
  built the crawler..." used first-person possessive framing, which violates
  the no-first-person rule. Changed heading to "Scope" and rewrote the body
  to "Covers the crawler, MCP workflow, report structure, style taxonomy,
  frontend interface, and editorial/product direction." — same information,
  third-person/report voice, matches surrounding section tone.

## Clean (no changes needed)

- `web/app/page.tsx` — homepage copy is report-voice throughout, disclaimer
  present ("No purchasing recommendation is implied").
- `web/app/layout.tsx` — metadata title/description confirmed current
  ("ARI3LLA INDEX: Weekly Style Signal Report"), no stale "RUNWAY" branding.
- `web/app/archive/page.tsx`, `methodology/page.tsx`, `taxonomy/page.tsx`,
  `sources/page.tsx`, `about/page.tsx`, `reports/[date]/page.tsx` — all in
  wire-service tone, no hype language, no shopping recommendations.
  Methodology and About pages explicitly state TikTok/social signals are
  high-noise by default and editorial coverage does not upgrade their
  confidence — correctly preserves the source-sector distinction rather than
  flattening into "trending."

## Verification

`cd web && npx tsc --noEmit && npx next build` — passed clean, no errors
introduced. All 9 static routes plus 2 dated report pages generated
successfully.
