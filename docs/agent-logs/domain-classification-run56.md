# Domain classification follow-up: run 56

Closed the `DOMAIN_SECTOR_MAP` gap flagged in `docs/agent-logs/real-report-2027-05-24.md`
for `runwaylive.com` and `stylerave.com` (both cited in `data/reports/2027-05-24.json`'s
`source_domains`, both correctly falling back to `unclear` before this run).

## Research

- **runwaylive.com** (WebSearch, WebFetch 429'd on this domain): RUNWAY Magazine, a US
  fashion/beauty/lifestyle publication established 1989, operated by Runway TV LLC,
  CFDA-accredited Fashion Week coverage. Genuine editorial outlet, not an aggregator or
  PR wire.
- **stylerave.com** (WebFetch succeeded): Style Rave NG LLC, a Nigeria-based fashion/
  beauty/culture editorial publication with named staff writers (Justina Willie, Lydia
  Oladejo, Collins Badewa), original critical/analysis pieces, plus an affiliate-linked
  "Shopping Guide" section and a premium subscription tier. Same editorial-plus-commerce-
  layer pattern already accepted for `okayafrica.com`/`nataal.com` in the map -- not a
  content farm, not disqualifying.

Neither domain warrants a "don't cite this" flag; both are legitimate editorial outlets.

## Change

Added to `src/taxonomy.py`'s `DOMAIN_SECTOR_MAP` (with an inline comment recording the
verification basis):

```python
"runwaylive.com": "editorial",
"stylerave.com": "editorial",
```

No changes made to `data/reports/2027-05-24.json` or any other report content, per scope.

## Verification

`python -m py_compile src/*.py` -- passed.

Not committed, per instructions.
