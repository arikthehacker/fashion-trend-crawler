# Run 77 — glossary "Vogue" scan-warning cleanup

## Context

Run 76 left one carried-forward item: `web/app/glossary/page.tsx`'s build-time scanner
(`loadGlossaryTerms()`) was warning that "Vogue" had no `DEFINITIONS` entry, sourced from
`data/reports/2027-10-18.json`.

## Investigation

1. **How the scanner decides what's a "term"**: `loadGlossaryTerms()` in
   `web/app/glossary/page.tsx` scans three fields per report — `aesthetic_terms`,
   `cultural_references`, and `top_signals[].name` — normalizes each candidate, filters
   out sentence-like strings via `isPlausibleGlossaryTerm()`, then checks the survivors
   against the `DEFINITIONS` dictionary. Anything present in the archive but missing from
   `DEFINITIONS` triggers a non-blocking `console.warn` at build time and is silently
   omitted from the rendered page.

2. **Where "Vogue" actually appears**: `data/reports/2027-10-18.json`, line 63, inside
   `cultural_references: ["Inexmoda", "Bogota fashion week", "Vogue"]`. That field
   already legitimately holds source/publication names elsewhere in the same report
   (`Inexmoda`, `Bogota fashion week`) — both of which have real `DEFINITIONS` entries
   describing them as institutional-sector sources. The report's `limitations` field
   confirms the intent: "No U.S. or European editorial outlet beyond vogue.com has
   independently corroborated the Bogota showcase..." — i.e., Vogue is cited here as the
   editorial outlet that broke/corroborated the Bogota fashion-week coverage, the same
   role "who what wear," "ssense," "net-a-porter," and "fhcm" already play as
   editorial/retail/institutional source-name glossary entries.

## Decision

This is **not** a data bug and **not** an over-broad scan. `cultural_references` is
explicitly used elsewhere in the schema/glossary to hold source/publication names
alongside aesthetic terms (see existing entries for "who what wear," "ssense," "cfda,"
"fhcm," "net-a-porter" — all publication/retailer/institution names with real
`DEFINITIONS` entries, following the same precedent set in run 74's glossary audit for
designer/brand names). "Vogue" fits this exact established pattern: a publication cited
as an editorial-sector source. It deserves a minimal, accurate, wire-service-voice
definition — not a data correction.

## Fix applied

Added to `DEFINITIONS` in `web/app/glossary/page.tsx` (alphabetically after
"who what wear," matching existing style):

```
"vogue": "A Conde Nast fashion and lifestyle publication, cited as an editorial-sector
source when its coverage is tracked; distinct from the CFDA/Vogue Fashion Fund, a
separate jointly run award program."
```

The parenthetical distinguishing it from "cfda/vogue fashion fund 2026" (an existing,
separate glossary entry) avoids ambiguity since both terms now co-exist in the
dictionary.

No scanner logic changed. No report data changed — `cultural_references` in
`2027-10-18.json` is correct as-is.

## Validation

- `npx tsc --noEmit` — clean, no errors.
- `npx eslint .` — clean, no warnings/errors.
- `npm run build` — succeeded (169 pages, Pagefind index built); no
  `[glossary] no DEFINITIONS entry for term "Vogue"` warning in the build log, and no
  other new glossary warnings appeared.

No other files touched. Nothing committed.
