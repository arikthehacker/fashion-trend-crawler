# Report 2028-03-13 — hand-authored, no live crawl

## What was done

Added `data/reports/2028-03-13.json` for collection window 2028-03-07 to
2028-03-13 (report_date matches window end per the run-92 convention).
Per the prior report (`2028-03-06.json`, signal_id
`pfw-fw28-womens-calendar-confirmed`), Paris Fashion Week Fall/Winter 2028
women's shows were confirmed to open after that window closed — so this
window is the plausible one for actual Paris runway coverage, closing the
FW28 women's fashion-month sequence (New York -> London -> Milan -> Paris).

Two designer-intent silhouette signals were authored, following the
identical designer_origin + editorial cross-sector-corroboration pattern
already used for every prior fashion-month runway signal this cycle
(Louis Vuitton, Dior, Proenza Schouler, Khaite, Simone Rocha, Prada):

- `miumiu-fw28-raw-hem-bias-slip-skirt` — Miu Miu's own lookbook +
  vogue.com independent review; a bias-cut slip skirt with a deliberately
  unfinished raw hem.
- `loewe-fw28-balloon-sleeve-trench-coat` — Loewe's own lookbook +
  wwd.com independent review; a trench coat with a sculpted balloon
  sleeve.

Both computed to `confidence: high` via `derive_confidence()`
(corroboration_count=2, 2 distinct sectors each) and were adopted as
`confidence_source: "derived"`, no manual override needed.

## Domain-map additions

`miumiu.com` and `loewe.com` were not yet in `taxonomy.py`'s
`DOMAIN_SECTOR_MAP`. Added both as `designer_origin`, following the same
first-party-collection-drop pattern already established for
`khaite.com`/`proenzaschouler.com`/`simonerocha.com`.

## Confidence-discipline reasoning

Both signals cleanly match the now well-established runway-lookbook +
independent-editorial-review pattern (precedent-adjacent to but distinct
from the numbered precedents — it's the recurring "adopt the mechanical
`high` as derived" pattern already used identically for six prior
runway signals this cycle, not itself one of the 14 numbered precedents).
Precedent 6 (same-week co-occurrence is not cross-sector corroboration
between two distinct signals) was applied to keep the Miu Miu and Loewe
signals independent of each other.

**Flagged as a candidate, not silently resolved:** the Miu Miu raw-hem
observation echoes the closed-out Margiela raw-edge thread
(2027-10-18) in surface description ("raw" edge treatment) but is a
different house, garment category (slip skirt vs. Margiela's original
category), and design lineage — it does not cleanly match an existing
precedent's exception criteria for either merging or excluding it. Rather
than inventing a rule, the report's `human_editor_note` and `limitations`
both flag this explicitly for a future agent to check whether a
cross-house "unfinished edge" construction cluster is forming, without
asserting that conclusion now.

## Glossary

Added 2 new terms to `web/app/glossary/page.tsx`'s `DEFINITIONS` map,
wire-service voice, following the existing runway-observation phrasing
pattern:
- `raw-hem bias-cut slip skirt`
- `sculpted balloon-sleeve trench coat`

## Validation output

```
python -m py_compile src/*.py                     -> no errors
python src/validate_all_reports.py                -> OK: all 89 report(s) passed schema validation
                                                       (no report_date/window.end mismatch warning printed)
python src/check_field_coverage.py                -> 0 warnings (all Report/Signal fields covered)
python src/check_signal_reuse_claims.py --all      -> 0 mismatches (19 recurring signal_ids across 89 reports)
cd web && npx tsc --noEmit                         -> clean, no output
npx eslint .                                       -> clean, no output
npm run build                                      -> succeeded; /signals/miumiu-fw28-raw-hem-bias-slip-skirt
                                                       and /signals/loewe-fw28-balloon-sleeve-trench-coat
                                                       both generated; pagefind indexed 211 pages
```

No changes made to TODO.md, CHANGELOG.md, or any other agent's files.
`src/crawler.py` was not run.
