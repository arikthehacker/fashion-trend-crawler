# Real report: 2026-06-08

## Task

First genuine real-world (not fictional-forward-dated) report for the archive rebuild
following the purge of 95 synthetic placeholder reports (see `data/reports/README.md`,
`data/examples/synthetic-reports/README.md`). Collection window
`{"start": "2026-06-02", "end": "2026-06-08"}`, `report_date: "2026-06-08"` (matches
`collection_window.end` per the run-92 convention in `report_schema.py`).

`data/reports/` was empty except its own `README.md` at task start -- no prior real
report exists yet to compare conventions against, so this report leans on
`docs/confidence-discipline-precedents.md` and `src/report_schema.py`/`src/taxonomy.py`
directly rather than a preceding real report.

## WebSearch queries run and what each returned

1. `"CFDA Fashion Awards 2026 winners June"` -- returned the 2026 CFDA/Vogue Fashion
   Fund finalist announcement (June 2, 2026: 10 finalists named, first designer
   judging June 10, winner announced October 20 with $300k/$100k prizes). No evidence
   of a separate main "CFDA Fashion Awards" ceremony in this window -- that ceremony is
   a later-year event (the 2025 edition was November 3, 2025), consistent with
   SKILL.md's note that the CFDA Fashion Awards question has a track record of staying
   unconfirmed/being a separate, later-year event. Not fabricated as occurring in this
   window.
2. `"fashion trends June 2026"` -- returned Who What Wear's summer 2026 trend
   coverage (lace-trimmed shorts, crochet skullcaps, asymmetric skirts, wedges,
   layered tops, big sunglasses, long pendant necklaces) and general trend-forecast
   sites (Trend Hunter, Heuritech). Real, but single-outlet/service-journalism in
   character -- see confidence discussion below.
3. `"resort 2027 collection preview June 2026"` -- returned multiple real Resort 2027
   collection preview/review pieces (Carolina Herrera, David Koma, Stella McCartney,
   Staud, Gabriela Hearst, Ferrari, MM6 Maison Margiela) via WWD and others. Followed
   up on each to confirm actual show/publication dates (see below) since "Resort 2027"
   previews run across the whole of May-July 2026, not just this window.
4. `"vogue.com trend report June 2026"` -- did not surface a dated June 2026 vogue.com
   trend piece; returned a Vogue Scandinavia SS26 trend report instead (a different,
   earlier season/outlet, not used).
5. `"Dior Resort 2027 Wilshire Boulevard Jonathan Anderson LACMA date"` -- confirmed
   the Dior Cruise 2027 show (Jonathan Anderson's first for the house) was staged
   **May 13, 2026** at LACMA -- before this window. Not logged as a signal for this
   report; recorded in `limitations` as confirmed-but-out-of-window.
6. `""CFDA Fashion Awards" 2026 ceremony date June"` -- no evidence of a main CFDA
   Fashion Awards ceremony in June 2026; confirmed the June events are the Fashion
   Fund program, a distinct CFDA property from the Fashion Awards ceremony itself.
7. `"Stella McCartney Resort 2027 25th anniversary sustainable materials June 2026"` --
   real collection (93% responsible materials, 25th-anniversary framing) but no
   specific in-window publication date was confirmed, so not logged as a top_signal
   (would need a follow-up search to pin the date; not chased further given three
   solid in-window signals were already secured).
8. `"thefashionfold.com Carolina Herrera Resort 2027 date published"` -- page metadata
   suggested "~3 weeks ago" relative to the July 7, 2026 session/search date, which
   points to roughly mid-June 2026 -- outside the June 2-8 window. Excluded from
   `source_domains` on that basis; only wwd.com's confirmed June 7, 2026 preview was
   cited.
9. `"fashion industry news week of June 2 2026"` -- surfaced Marine Serre x Under
   Armour (used, see below), plus SHEIN's acquisition of Everlane, Temu's EUR200m EU
   fine, and a Canopy wheat-straw Lyocell/viscose materials-innovation pilot. The
   first two are business/regulatory news, not style signals (excluded, see
   `limitations`); the Canopy item is real materials-innovation coverage but its only
   found source (goodonyou.eco) is not in `taxonomy.py`'s domain map and editing that
   file was out of scope for this report, so it's recorded in `limitations` as a
   flagged gap rather than logged or force-classified.
10. `"dieworkwear.com June 2026"` -- no specific June 2026 post surfaced in results;
    independent_criticism sector coverage for this window could not be confirmed, so
    none was logged.
11. `"Marine Serre Under Armour collaboration launch date June 2026"` -- confirmed the
    capsule launched **June 5, 2026** (inside window), corroborated by wwd.com,
    highsnobiety.com, fashionnetwork.com (three editorial outlets, already in
    `DOMAIN_SECTOR_MAP`) plus Under Armour's own announcement (underarmour.com, not
    yet mapped).
12. `"Carolina Herrera Resort 2027 WWD June 7 2026 preview"` -- confirmed the WWD
    preview piece specifically to **June 7, 2026** (inside window), with full
    collection detail (Georgia O'Keeffe-inspired prints, palette, silk gazar/mesh
    knit/macrame/raffia, debut denim).
13. `"Paris men's fashion week June 2026 dates spring summer 2027"` -- confirmed Paris
    Men's Fashion Week SS27 runs **June 23-28, 2026**, entirely after this window's
    close. Used to correctly exclude Louis Vuitton/Dior Homme/Issey Miyake/Rick
    Owens/etc. from this report.
14. `"MM6 Maison Margiela Resort 2027 David Koma Resort 2027 date show June 2026"` --
    confirmed MM6's show was June 19, 2026, and David Koma's was June 25, 2026 --
    both after this window's close (June 8). Excluded on that basis, recorded in
    `limitations`.
15. `"whowhatwear summer fashion trends 2026 published June 2026 date"` -- confirmed
    one Who What Wear roundup specifically to June 2, 2026 (inside window). Used only
    to populate the structured `garments`/`silhouettes`/`colors` lists, not as a
    `top_signals` entry (see confidence reasoning below).

## Signals included, and why

1. **`cfda-vogue-fashion-fund-2026-finalists`** -- CFDA/Vogue Fashion Fund 2026
   finalists, announced June 2, 2026. Six independently-published outlets
   (cfda.com/institutional; wwd.com, businessoffashion.com, fashionista.com,
   theimpression.com, runwaylive.com/editorial), two genuinely distinct sectors --
   `derive_confidence()` correctly computes `high` (count 6, 2 sectors) with no
   manual override needed. `origin_classification` set to `"unclear"` rather than
   forced into a trend-adoption bucket, per precedent 11 (industry-recognition/
   institutional-cycle news is a distinct categorization from an observed garment/
   silhouette/aesthetic trend, even when well corroborated).
2. **`marine-serre-under-armour-capsule`** -- Marine Serre x Under Armour capsule,
   launched June 5, 2026. Four corroborating sources, but only three
   (wwd.com, highsnobiety.com, fashionnetwork.com) resolve to a mapped sector
   (`editorial`); Under Armour's own announcement (underarmour.com) is not yet in
   `taxonomy.py`'s `DOMAIN_SECTOR_MAP`. Editing `taxonomy.py` was out of scope for
   this report (scope was limited to the report JSON and this log), so per
   precedent 3 (an unmapped/"unclear" domain must not be counted as real sector
   diversity) `source_sectors` is set to `["editorial"]` only, leaving this correctly
   single-sector at `medium` via precedent 2's same-sector volume cap, rather than
   the `high` a naive 2-sector count would produce if `underarmour.com` were wrongly
   treated as a second sector. Flagged in `limitations`/`human_editor_note` as a
   `DOMAIN_SECTOR_MAP` gap for a future taxonomy-authorized run to close.
3. **`carolina-herrera-resort-2027-okeeffe`** -- Carolina Herrera Resort 2027 preview,
   WWD, June 7, 2026. Single confirmed in-window source; `editorial` is in
   `HIGH_RELIABILITY_SECTORS`, so `derive_confidence()` correctly computes `medium`
   at `count=1` rather than `low`. Other outlets covering the same collection
   (thefashionfold.com, theimpression.com, boujeez.com) were found but their
   publication dates could not be confirmed as falling inside June 2-8, so they were
   deliberately not cited, to avoid overstating in-window corroboration.

## Signals/items considered and excluded

- **Who What Wear's summer 2026 trend roundup** (June 2, 2026) -- real and in-window,
  but single-outlet, shopping/service-journalism framing ("44 standout fashion
  finds," "predict what it girls will be wearing and buying"). Excluded from
  `top_signals` per precedent 8's commercial-vertical discount rather than logged at
  an inflated tier; its garment/silhouette/color terms were still folded into the
  report's structured lists, since those fields carry no corroboration-bar
  requirement the way a `top_signals` entry does.
- **SHEIN's acquisition of Everlane, Temu's EUR200m EU fine, Patagonia's lawsuit** --
  real business/regulatory fashion-industry news this window, excluded as
  corporate/regulatory news rather than observation of a garment, silhouette, or
  aesthetic trend, per precedent 11's categorization discipline (attention-economics/
  industry discourse is not automatically a style signal).
- **Canopy wheat-straw Lyocell/viscose pilot** -- real materials-innovation coverage,
  but its only found source (goodonyou.eco) isn't in `taxonomy.py`'s domain map;
  classifying a new domain or editing that file was out of scope for this report, so
  it was left unlogged and flagged as a gap in `limitations` rather than force-fit or
  fabricated a sector for it.
- **Dior Cruise 2027 "Wilshire Boulevard" (LACMA)** -- confirmed real and widely
  covered, but staged May 13, 2026, before this window opens (June 2). Not logged.
- **Paris Men's Fashion Week SS27 (Louis Vuitton, Dior Homme, MM6 Maison Margiela,
  David Koma, etc.)** -- confirmed real, runs June 23-28, 2026, after this window
  closes (June 8). Not logged.
- **Stella McCartney, Staud, Gabriela Hearst, Ferrari Resort 2027 collections** --
  real collections, but no in-window publication date could be pinned down in the
  time available (Gabriela Hearst's show ties to Paris menswear week, June 23-28,
  outside window regardless). Not chased further once three solid in-window signals
  were secured; not logged.
- **dieworkwear.com (independent_criticism)** -- searched specifically for June 2026
  coverage; no dated post for this window surfaced. No independent_criticism-sector
  signal logged this window.

## Source-sector classification reasoning (new/unmapped domains encountered)

- **underarmour.com** -- Under Armour's own official press/announcement page
  (`about.underarmour.com`), first-party brand content announcing its own capsule
  collaboration. Not yet in `taxonomy.py`'s `DOMAIN_SECTOR_MAP`. Reasoned it would
  match the existing `designer_origin` pattern (brand-owned site, first-party
  collection/collaboration drop -- the same pattern as `chanel.com`, `loewe.com`,
  `proenzaschouler.com`) if a future run is authorized to add it, but did **not** add
  it to `taxonomy.py` myself, since this report's scope was explicitly limited to
  `data/reports/2026-06-08.json` and this log file only. Treated as an unmapped/
  "unclear" domain for this report's confidence math (see precedent 3), cited in
  `source_domains` for attribution but excluded from `source_sectors`.
- **goodonyou.eco** -- a sustainable-fashion-focused editorial/advocacy outlet,
  encountered via the Canopy materials-innovation search. Also not in
  `DOMAIN_SECTOR_MAP`. Not classified or added (same out-of-scope reasoning as
  above); the item it sourced was left unlogged rather than force-classified.
- All other domains cited (`cfda.com`, `wwd.com`, `businessoffashion.com`,
  `fashionista.com`, `theimpression.com`, `runwaylive.com`, `highsnobiety.com`,
  `fashionnetwork.com`, `whowhatwear.com`) were already present in
  `taxonomy.py`'s `DOMAIN_SECTOR_MAP` and were used as-is via `classify_source()`
  logic (no new classification work needed).

## Confidence discipline

- `cfda-vogue-fashion-fund-2026-finalists`: `high`, `confidence_source: "derived"` --
  mechanical formula output adopted as-is (6 sources, 2 real distinct sectors).
- `marine-serre-under-armour-capsule`: `medium`, `confidence_source: "derived"` --
  mechanical formula output adopted as-is, after correctly excluding the unmapped
  `underarmour.com` domain from `source_sectors` per precedent 3 (this exclusion is
  the substantive judgment call here; once made, the formula runs straightforwardly).
- `carolina-herrera-resort-2027-okeeffe`: `medium`, `confidence_source: "derived"` --
  mechanical formula output adopted as-is (single editorial source, `editorial` in
  `HIGH_RELIABILITY_SECTORS`).
- No signal in this report required a precedent-12-style manual override away from
  the mechanical result; the judgment work here was in *what to exclude from
  `source_sectors`/`top_signals` in the first place* (precedents 2, 3, 8, 11), not in
  overriding a computed tier.
- `collection_status: "normal"` (not `"thin"`) -- three genuinely distinct, dated,
  cross-checkable signals were found for this window, which clears the bar for a
  normal (non-thin) report.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-06-08'))"
```
-> no output, no exception raised (`validate_report()` passes silently on success).
`content_hash` computed and written by `save_report()`. Report was built entirely via
`Report`/`Signal`/`CollectionWindow` dataclasses and `save_report()` -- no hand-written
JSON.

## Files touched

- `data/reports/2026-06-08.json` (new)
- `docs/agent-logs/real-research-2026-06-08.md` (this file, new)

No other file was touched, per task scope. `taxonomy.py`'s two flagged domain-map gaps
(`underarmour.com`, `goodonyou.eco`) are left for a future run explicitly scoped to
edit that file. No commit was made; git was not touched.
