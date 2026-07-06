# taxonomy-outlet-expansion

Scope: `src/taxonomy.py` only. Follows up on `structure-taxonomy-sync.md`, which found
doc §11 doesn't name exhaustive domains for most sectors but `DOMAIN_SECTOR_MAP` was still
thin for several. Added real, currently-active domains per sector:

- **designer_origin** (had zero entries): `chanel.com`, `dior.com`, `gucci.com`,
  `louisvuitton.com`, `prada.com` — brand-owned sites where collections/drops are announced
  first-party, the definition of "designer origin."
- **visual_archive** (had 2): `firstview.com` (runway image archive since 1995, 8M+ photos),
  `nowfashion.com` (self-described largest runway image database), `gettyimages.com`
  (licensed editorial/runway photo search), `fashionanthology.com` (runway photo archive/
  licensing site).
- **independent_criticism** (had 1, generic `substack.com`): `blackbirdspyplane.com`
  (subscriber-funded style/culture newsletter, no ads/affiliate links), `dieworkwear.com`
  (Derek Guy's menswear criticism blog), `throwingfits.com` (independent menswear
  newsletter/podcast) — all confirmed active via BoF's "New World of Indie Media" piece.
- **institutional** (had 3): `cfda.com` (Council of Fashion Designers of America),
  `kci.or.jp` (Kyoto Costume Institute), `britishfashioncouncil.co.uk` — established
  fashion governance/archival bodies.
- **retail** and **resale**: already well-populated (net-a-porter, ssense, farfetch,
  nordstrom, shopbop, revolve / therealreal, depop, vestiairecollective, grailed, poshmark)
  — left unchanged, no gaps found.

Pattern preserved exactly: flat `domain: sector` dict entries under existing comment
headers, no restructuring of `classify_source()`.

## Verify

`python -m py_compile src/*.py` — passes clean.

Spot-checked `classify_source()`:
`chanel.com` -> designer_origin, `blackbirdspyplane.com` -> independent_criticism,
`firstview.com` -> visual_archive, `cfda.com` -> institutional, `net-a-porter.com` -> retail,
`therealreal.com` -> resale. All correct.
