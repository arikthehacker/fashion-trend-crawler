# Glossary DEFINITIONS coverage audit — run 74

## Mechanism

`web/app/glossary/page.tsx` builds the glossary at build time from three per-report
fields (`aesthetic_terms`, `cultural_references`, `top_signals[].name`) across all of
`data/reports/*.json`, matched against a curated `DEFINITIONS` map. `isPlausibleGlossaryTerm()`
filters out sentence-like candidates before checking `DEFINITIONS`; anything that passes
that filter but has no `DEFINITIONS` entry triggers `console.warn("[glossary] no
DEFINITIONS entry ...")` at build time (non-blocking) and is silently omitted from the
rendered page.

## Findings

Ran `npm run build` and captured stderr. Initial run surfaced 47 distinct terms with no
`DEFINITIONS` entry, spanning reports from 2027-06-14 through 2027-10-04 (aesthetic
vocabulary, designer/brand/venue proper nouns, event names, and outlet names — all
legitimate archive content, none were malformed/garbage strings). A second build run
mid-audit picked up a newly-added report (2027-10-11, added concurrently by another
process) with 3 more missing terms.

All 50 terms were determined to be legitimate archive content worth documenting, either
as real style/construction vocabulary (e.g. "deconstructed tailoring," "raw-edge
finishing," "shock-casting," "tenniscore," "blokecore") or as designer/brand/venue/event/
outlet references consistent with existing precedent already in the map (e.g. "marlene
dietrich," "conner ives nyfw debut," "pinterest predicts annual trend report" were already
present as standalone proper-noun/event entries before this run). No true false positives
were found — no garbage strings, no scanning-logic changes were made, `isPlausibleGlossaryTerm()`
is untouched.

## Changes

Added 50 new entries to `DEFINITIONS` in `web/app/glossary/page.tsx`, wire-service voice,
no first person, no hype — covering: deconstructed tailoring / raw-edge finishing /
unfinished seam(s) / deconstructivist (Margiela/Martens design vocabulary), retro
sexiness, shock-casting / attention-economy runway / spectacle staging / climate-optics
backlash, preppy tailoring / nature motif embroidery, archival reverence / archive
revival, tenniscore / spectator style / royal courtside style / blokecore / expressive
dressing, and designer/brand/venue/outlet/event references (Glenn Martens, Maison
Margiela, Demna, Gucci, Balenciaga, Martin Margiela, John Galliano, Charvet, Matthieu
Blazy, Place Vendôme, Palazzo Serbelloni, Antwerp Six, Clavicular/Braden Peters, 424, Net-
a-Porter, Ssense, TikTok, Who What Wear, FHCM, CFDA, Paris/New York/Milan fashion week
variants, Paris Haute Couture Week, Wimbledon 2027, Royal Ascot, 2026 European heatwave,
Cristóbal Balenciaga archive, and compound event-signal names like "Demna's Gucci debut
reception").

## Validation

- `npx tsc --noEmit`: clean, exit 0.
- `npx eslint .`: clean, exit 0.
- `npm run build`: exit 0 on a clean `.next` (two earlier build attempts in this session
  hit unrelated Turbopack/export filesystem errors — `ENOENT` on a `.next` build-manifest
  temp file and a transient `out/glossary.html` read-after-retry warning during Pagefind
  indexing — both consistent with concurrent file writes from another process/agent
  active in this repo during the audit, not related to the glossary change; a clean
  `rm -rf .next && npm run build` succeeded with no glossary warnings).
- Confirmed via `grep -i glossary` on full build output: zero `[glossary] no DEFINITIONS
  entry` warnings remain after the changes.

## Remaining warnings

None outstanding as of this run. Since the glossary is derived from the live archive,
any future report with genuinely new aesthetic terms, designers, or events will produce
the same class of warning again — expected and by design, not a regression.
