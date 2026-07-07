# Agent log: taxonomy gap fix, run 94

## Task
Run 93 surveyed every `source_domains` value across all 85 reports against
`src/taxonomy.py`'s `DOMAIN_SECTOR_MAP` and found 58 missing domains, all
editorial/media/retail/institute sites, prioritized by citation frequency in its
log (`docs/agent-logs/taxonomy-gap-fix-run93.md`):
`voguescandinavia.com` (6), `wallpaper.com` (6), `marieclaire.com` (5),
`nssmag.com` (5), `coveteur.com` (5), `istitutomarangoni.com` (4),
`wmagazine.com` (3), `anothermag.com` (3), plus ~50 more at count 1-2. This run
closes the top 8 of that backlog with real verification rather than trusting
run 93's own loose "editorial/media/retail/institute" grouping as the final
classification.

## Verification (WebSearch each domain individually)

- **voguescandinavia.com** -- Vogue Scandinavia, Conde Nast's Nordic-region
  local Vogue edition (launched Aug 2021, 26th local Vogue edition, edited by
  Martina Bonnier). Staffed editorial title, same publisher family as
  vogue.com/voguearabia.com already in the map. -> `editorial`.
- **wallpaper.com** -- Wallpaper*, British monthly design/architecture/
  fashion/art/travel magazine (est. 1996 London, now Future plc). Staffed
  editorial title with named editors. -> `editorial`.
- **marieclaire.com** -- US edition of Marie Claire, women's magazine
  founded 1937 in France, now published by Future US (acquired from Hearst
  2021). Long-running staffed editorial title. -> `editorial`.
- **nssmag.com** -- nss magazine, Milan-based streetwear/culture title,
  originally a blog (naplestreetstyle.it, 2012), now an officially registered
  newspaper publication (2022) with investigative journalism and feature
  content, plus a "shopping" vertical. Editorial-plus-commerce-layer pattern,
  same bar already accepted for okayafrica.com/stylerave.com. -> `editorial`.
- **coveteur.com** -- Coveteur, multimedia fashion/beauty/lifestyle brand
  (est. 2011, relaunched 2025 under Gallery Media Group/VaynerX), has a
  named Editor-in-Chief (Faith Xue) and a published editorial policy that
  explicitly bars pay-for-play coverage. Has a "shopping" section but is
  editorial-led, not a transactional retailer like net-a-porter.com/
  ssense.com. -> `editorial`.
- **istitutomarangoni.com** -- Istituto Marangoni, a genuine higher-education
  institution founded 1935 in Milan, campuses in Milan/Paris/London/
  Florence/Shanghai, QS-ranked fashion/design/luxury school. This is the
  domain the task flagged as a likely miscategorization risk (run 93's list
  called it "editorial/media/retail/institute" without picking one) -- on
  inspection it is unambiguously an educational body, matching fitnyc.edu's
  existing `institutional` entry, not `editorial` or `designer_origin`.
  -> `institutional`.
- **wmagazine.com** -- W Magazine, fashion/film/art/culture title (est.
  1993 as a Fairchild Fashion Media spinoff of WWD, now Bustle Digital
  Group). Staffed editorial title with a public masthead. -> `editorial`.
- **anothermag.com** -- AnOther Magazine, British biannual fashion magazine
  (est. 2001, founded by Jefferson Hack), published online by Dazed Media --
  the same independent publisher as dazeddigital.com, already `editorial`
  in this map. -> `editorial`.

No domain in this batch turned out to be a PR/marketing site or already
effectively covered by an existing entry -- all 8 are genuine, independently
verifiable outlets or (in istitutomarangoni.com's case) a genuine institution.
None were skipped.

## Changes made
Added 8 entries to `DOMAIN_SECTOR_MAP` in `src/taxonomy.py`, each with a
citation comment in the established style referencing this log:
- `voguescandinavia.com` -> `editorial`
- `wallpaper.com` -> `editorial`
- `marieclaire.com` -> `editorial`
- `wmagazine.com` -> `editorial`
- `anothermag.com` -> `editorial`
- `nssmag.com` -> `editorial`
- `coveteur.com` -> `editorial`
- `istitutomarangoni.com` -> `institutional`

## Validation
```
python -m py_compile src/*.py            -> no output (success)
python src/validate_all_reports.py       -> OK: all 86 report(s) in data/reports/ passed schema validation.
```
(This run doesn't touch report data; 86/86 clean as expected.)

## Backlog remaining for a future run
Per run 93's survey, the following ~50 domains (each cited 1-2 times) are
still missing from `DOMAIN_SECTOR_MAP` and were deliberately left undone this
run -- not silently dropped, just lower priority by citation count. A future
run should re-run run 93's extraction script (or an equivalent domain diff
against all `data/reports/*.json`) to get the exact current list, since new
reports may have added or changed counts since run 93. Nothing beyond the 8
domains listed above was added in this run.

## Files touched
- `src/taxonomy.py` (8 new `DOMAIN_SECTOR_MAP` entries, see above)
- `docs/agent-logs/taxonomy-gap-fix-run94.md` (this log)

No other files modified. No git operations performed. TODO.md, CHANGELOG.md,
and `data/reports/*.json` were not touched.
