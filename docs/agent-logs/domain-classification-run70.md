# Domain classification run 70

Followed up on the 2027-09-06 report's flag: `fhcm.paris` and `laforma.club`
both fell outside `taxonomy.py`'s `DOMAIN_SECTOR_MAP` and classified `unclear`.

## fhcm.paris

WebSearch confirmed `fhcm.paris` (fhcm.paris/en) is the real, official site of
the Fédération de la Haute Couture et de la Mode -- the governing body that
coordinates Paris Fashion Week and Haute Couture Week. Not a typo/wrong
domain. Classified as `institutional`, mirroring `cfda.com` and
`britishfashioncouncil.co.uk` -- it's an industry governing body's official
calendar, not editorial press or a brand.

## laforma.club

WebSearch showed LA FORMA / laforma.club is an independent fashion-media
outlet: fashion week calendar roundups, designer/bag guides, documentary
lists -- content with staff-style editorial framing, not a governing body and
not merely a raw data feed. Classified as `editorial`, matching the existing
pattern for content-plus-commerce editorial titles already in the map
(`okayafrica.com`, `stylerave.com`).

## Changes

`src/taxonomy.py`: added two entries to `DOMAIN_SECTOR_MAP`:
- `"fhcm.paris": "institutional"`
- `"laforma.club": "editorial"`

Both use existing `SOURCE_SECTORS` values; no vocabulary change.

## Verification

`python -m py_compile src/*.py` -- passed, no errors.

Not committed, per instructions. This does not retroactively change
`origin_classification`/confidence on the already-saved
`data/reports/2027-09-06.json` -- that would require re-running
`derive_confidence()`/editorial judgment on that specific report, out of
scope for this domain-map-only task. Flagging as a natural follow-up for
whoever next touches that report or runs `audit_confidence.py`.
