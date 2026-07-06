# Static pages audit 2 — methodology / taxonomy / sources

Scope: `web/app/methodology/page.tsx`, `web/app/taxonomy/page.tsx`, `web/app/sources/page.tsx`
vs doc sections 22, 11/14/15/16, 11, and `src/taxonomy.py`'s `classify_source()`.

## Drift found and fixed

`src/taxonomy.py`'s `SOURCE_SECTORS` and doc section 11 both define 10 sectors, including
`street_ugc` (street/user-generated) and `resale` (resale/secondhand — implemented in
`DOMAIN_SECTOR_MAP` with real domains: therealreal.com, depop.com, vestiairecollective.com,
grailed.com, poshmark.com). Both frontend pages had silently dropped these two sectors:

- `taxonomy/page.tsx`: `sourceSectors` only listed 7 of 10 sectors. Added "Street/user-generated"
  and "Resale/secondhand" rows.
- `sources/page.tsx`: only listed 6 sectors, missing "Visual Archive/Search" (present in
  taxonomy.py's map via google.com/worn-on.com but absent here entirely) plus the same two.
  Added all three missing sector blocks with definitions and representative items.
- `methodology/page.tsx`: "Source Sectors" section text named only 7 sectors; updated to name
  all 9 currently in the taxonomy (visual archive/search was already implicit; street/UGC and
  resale/secondhand added).

## Not changed

- Volatility labels, confidence levels, and signal-type list on `taxonomy/page.tsx` matched
  `taxonomy.py`'s `VOLATILITY_LABELS`/`CONFIDENCE_LEVELS` and doc sections 14/15/16 exactly —
  no drift.
- No voice violations found (no first person, no hype language, no shopping-advice framing) —
  all three pages already used report/wire-service voice per doc §2.
- `street_ugc` has no domains in `DOMAIN_SECTOR_MAP` (declared vocab, unused by
  `classify_source` yet) — items listed are generic descriptions, not fabricated source names.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 13 routes built
including `/methodology`, `/taxonomy`, `/sources`.
