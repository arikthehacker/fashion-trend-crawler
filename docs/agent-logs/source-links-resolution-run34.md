# source_links resolution (run 34)

## Decision: removed entirely (option a)

## Reasoning
`source_links` had no backend support: absent from `Report`/`Signal` dataclasses
and `REQUIRED_SIGNAL_KEYS` in `src/report_schema.py`, never populated by
`summarize.py`, never rendered by any `.tsx` file. It existed only as a stray
`source_links?: string[]` type in `web/lib/reports.ts` and an empty `[]` in one
legacy file (`data/reports/2026-05-07.json`).

Re-reading `docs/ARI3LLA INDEX.txt` (line 890, schema field list; line 1297,
report-module list) confirms `source_links` was part of the original raw-brainstorm
concept, not pure accidental drift — so it wasn't a baseless invention. But two
things outweigh reviving it:

1. The project's actual shipped design already resolved how sourcing is surfaced,
   and diverged from the brainstorm doc on purpose: `sources/page.tsx` lists
   outlets by name/category with no URLs, and every report's `evidence` field is
   aggregated sector-level prose, never a single-outlet link (confirmed by run 33's
   grep of all `data/reports/*.json` — no URLs in any `evidence` field). Adding
   per-article `source_links` now would be a net-new feature that cuts against
   established, deliberate practice, not a restoration of something the site
   already relies on.
2. Run 33 identified a genuine unresolved risk: per-article links to small/
   independent-criticism-sector outlets are a plausible "hug of death" /ǁpile-on
   vector, with a recommended mitigation (link to outlet homepage/section, not
   article permalink) that has not been designed or implemented. Shipping the
   field now, without that mitigation, would activate the exact risk run 33 flagged
   as dormant.

No current page, RSS feed, or JSON-LD block needs `source_links` to function.
Given no live consumer and an identified but unaddressed risk in implementing it
properly, removal is the safer and simpler call; it can be re-proposed later as a
scoped feature with the run-33 mitigation designed in from the start.

## Actions taken
- Removed `source_links?: string[]` from `Report` interface in `web/lib/reports.ts`.
- Cleaned the stray `source_links: []` key from `data/reports/2026-05-07.json` via
  `save_report()` with `revision_reason` (not hand-edited), which appended a
  `revision_history` entry recording the correction.

## Verification
- `python -m py_compile src/*.py` — passed.
- `python src/validate_all_reports.py` — `OK: all 26 report(s) ... passed schema validation.`
- `cd web && npx tsc --noEmit && npx next build` — passed, all 84 pages generated successfully.
