# Journalism standards check — run 48: headline capitalization consistency

**Topic:** AP style headline case vs. sentence case — checked for consistency between
`executive_summary` prose, `top_signals[].name` entries, and page `<title>` metadata
across the site. Not previously covered in agent-logs (checked list of ~15 prior
topics; this one is new).

## What AP style requires

AP style uses sentence case for standard prose/headlines in running text (only first
word + proper nouns capitalized), reserving Title Case for special display contexts
(nav labels, page titles). Mixing the two within the same content type — e.g., a
headline that title-cases every word inside body prose — reads as inconsistent/amateur
and is a common wire-service style violation.

## What was checked

1. Extracted `top_signals[].name` from all 40 reports in `data/reports/*.json`
   (deduped, ~90 unique strings). All are consistently sentence-case: only the first
   word and genuine proper nouns (NYFW, CFDA, Wales Bonner, Chanel, Charvet, etc.) are
   capitalized. No stray Title-Case-Every-Word entries.
2. Programmatically checked the first sentence of every report's `executive_summary`
   (40/40) for headline-case drift, flagging any sentence where >70% of words (len>4)
   were capitalized outside a small acronym allowlist. **Result: 0 flagged.**
3. Checked page `<title>` metadata across `web/app/**/*.tsx` (layout.tsx, archive,
   timeline, search, reports/[date], signals/[slug], methodology section headings).
   These consistently use Title Case (e.g., "Timeline — ARI3LLA INDEX",
   "Archive — ARI3LLA INDEX"), which is the correct, distinct convention for page
   chrome vs. body prose.

## Conclusion

No gap found — the site already meets the standard. Body prose (signal names,
executive summaries) is uniformly sentence-case; page titles/nav are uniformly Title
Case; the two conventions are applied consistently and don't bleed into each other.
No code changes made.

## Verification

Read-only checks only (Python script iterating `data/reports/*.json`, grep over
`web/app/**/*.tsx`). No files modified — `tsc`/`py_compile` re-verification not
applicable since nothing changed.
