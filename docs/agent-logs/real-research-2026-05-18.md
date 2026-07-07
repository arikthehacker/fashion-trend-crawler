# Real report: 2026-05-18

## Task

Produce the first genuinely-researched report for a real past week,
`collection_window: {"start": "2026-05-12", "end": "2026-05-18"}`,
`report_date: "2026-05-18"` (matches `collection_window.end` per the run-92
convention in `report_schema.py`). This is one of several parallel agents
rebuilding the archive after the run-101/102 purge of 95 fictional-forward-dated
synthetic reports (see `data/examples/synthetic-reports/README.md`,
`data/reports/README.md`). No prior real report exists in `data/reports/` to
carry signal_ids or standing threads forward from — this report starts clean.

## WebSearch queries run and what each returned

1. `"Cannes Film Festival 2026 red carpet fashion May 2026"` — returned real,
   dated editorial coverage: CNN Style, W Magazine, Marie Claire all covering
   the 79th Cannes Film Festival's red carpet. Confirmed real looks: Tilda
   Swinton (Chanel SS26 couture), Ruth Negga (Ami tuxedo suit), Bella Hadid
   (Schiaparelli, dated May 20 — outside this window), Hoyeon (Louis Vuitton,
   May 17), Joan Collins (Stephane Rolland, opening night).
2. `"Cannes 2026 dates opening closing film festival"` — confirmed via
   Wikipedia/festival-cannes.com that the 79th Cannes Film Festival ran
   May 12–23, 2026 (opening May 12, hosted by Eye Haidara; closing May 23),
   meaning this collection window (May 12–18) covers the festival's entire
   first week. Not used as a fashion source, only for date confirmation.
3. `"vogue.com fashion trend May 2026"` — no results returned at all. Vogue
   was not used as a cited source for this report as a result (not for lack
   of trying — the query genuinely came back empty).
4. `"resort 2027 collection preview May 2026"` — surfaced Gucci, Dsquared2,
   Dior, and Stella McCartney Resort/Cruise 2027 previews, several dated
   within the window (Gucci May 18 post date, Dior May 18 post date). Follow-up
   queries below pinned down exact show dates.
5. `"Dior Resort 2027 Wilshire Boulevard show date Jonathan Anderson"` —
   confirmed Jonathan Anderson's first Dior Cruise 2027 show ("Wilshire
   Boulevard"), staged May 13, 2026 at LACMA's David Geffen Galleries.
6. `"Cannes 2026 red carpet May 14 15 16 dress"` — filled in day-by-day detail:
   May 14 (Diane Kruger, Givenchy floral mini dress, Fatherland premiere),
   May 15 (Riley Keough, Alaia drop-waist LBD).
7. `"Gucci Resort 2027 collection show date May 2026"` — confirmed Demna's
   first Gucci Cruise show, staged in Times Square, New York, on the evening
   of Saturday May 16, 2026 (one source's alternate May 17 date reconciled
   against WWD's "Saturday night" framing, which matches May 16).
8. `"Cannes 2026 opening ceremony dress Eye Haidara jury photocall fashion"` —
   surfaced several low-quality aggregator sites (iblingjewels.com,
   storynews.us, news.amomama.com, entertainmentnow.com) alongside a genuine
   WWD opening-ceremony piece; confirmed Demi Moore's jury-photocall
   polka-dot Jacquemus dress and custom Jacquemus opening-ceremony gown.
9. `"wwd.com Dior Cruise 2027 Jonathan Anderson LACMA review"` — confirmed
   direct WWD review + Modern Luxury + Wallpaper* coverage of the same show,
   with full detail (75-look lineup, Hitchcock/Dietrich referencing, reworked
   Bar jacket, David Geffen Galleries venue, Wednesday May 13 evening date).
10. `"Hunger magazine hungermag.com about fashion culture UK"` — run to
    evaluate hungermag.com (a Dior Cruise search result) as a possible citable
    domain. Confirmed it is a real, staffed quarterly UK fashion/culture
    magazine (founded 2011 by Rankin), but it was ultimately not cited in the
    final report — WWD/Modern Luxury/Wallpaper* already gave adequate
    corroboration for the Dior signal without adding a domain not yet in
    `taxonomy.py`'s map, and I preferred to minimize new unmapped-domain
    surface area this run rather than research and justify a second one.
11. `"wwd.com Gucci Cruise 2027 Demna New York Times Square review"` —
    confirmed direct WWD review plus RunwayLive, W Magazine, AnOther, and
    Whowhatwear coverage of the same May 16 Times Square show, with concrete
    detail (attendee list, "GucciCore" framing, ~90% wardrobe-staples
    composition, Times Square street closure).

## Signals included, and reasoning

**`cannes-2026-red-carpet-cluster`** (medium confidence, `recurring`
volatility, `editorial_amplified` origin) — four independent editorial
outlets (CNN, W Magazine, Marie Claire, WWD) each covered the same first
week of Cannes red-carpet appearances and each independently noted a mix of
large-scale couture drama and more playful/casual choices at the same event,
rather than one converging silhouette. All four corroborating sources are
`editorial`, so `derive_confidence()` returns `medium` (corroboration_count
>= 2, single sector) rather than `high` — recorded honestly rather than
inflated. Volatility is `recurring`, not `emerging` or `volatile`, since
Cannes red-carpet coverage is an annually-recurring calendar event, not a
newly-forming style movement.

**`dior-cruise-2027-anderson-lacma`** (medium confidence, `emerging`
volatility, `designer_originated` origin) — Jonathan Anderson's first Dior
Cruise show, staged May 13, 2026 at LACMA, independently reviewed by WWD,
Modern Luxury, and Wallpaper* with matching factual detail (venue, date,
75-look count, Hitchcock/Dietrich referencing). All three sources are
`editorial`, so confidence derives to `medium`, not `high`. Volatility
`emerging` rather than `stable`: this is a single creative-director debut
collection, and whether its specific motifs (florals/feathers/reworked Bar
jacket) recur beyond this one show isn't yet knowable from opening coverage.

**`gucci-cruise-2027-demna-times-square`** (high confidence, `emerging`
volatility, `designer_originated` origin) — Demna's first Gucci Cruise show,
staged May 16, 2026 in Times Square, corroborated by WWD, RunwayLive, W
Magazine, and AnOther (all `editorial`) plus Whowhatwear (`retail`). Two
distinct source sectors with corroboration_count >= 2 clears
`derive_confidence()`'s `high` bar — this is the one signal in this report
that does, and it's because a retail-sector outlet (Whowhatwear) happened to
independently cover the same show, not because the underlying claim is more
certain than the Dior signal. Volatility held at `emerging` for the same
reasoning as Dior: a single debut show is confirmed; whether "GucciCore"
becomes a durable framing beyond this one collection is not yet established.

## Signals considered and excluded

- **Bella Hadid's Schiaparelli look** (22,000-hour hand-embroidered dress,
  Jane Birkin homage) — genuinely real and well-covered, but dated May 20,
  2026, two days after this window's May 18 close. Excluded rather than
  pulled forward into this window; a future report covering the week of
  May 19–25 should pick it up if still relevant then.
- **A standalone Diane Kruger/Givenchy floral-mini-dress signal** — considered
  as its own signal, but folded into the broader Cannes red-carpet cluster
  instead of standing alone, since a single dress at a single premiere with
  no second independent report treating it as a discrete trend (rather than
  one item in a round-up) doesn't clear the bar for its own signal_id versus
  being cited as supporting evidence for the broader cluster claim.
- **Stella McCartney Resort 2027 (25th-anniversary, sustainable-materials
  collection)** and **Dsquared2 Resort 2027** — both real and dated to May
  2026, but Dsquared2's show date (May 27, per one source) falls outside this
  window, and Stella McCartney's specific show date within the window could
  not be pinned down from search results with the same confidence as Dior/
  Gucci's confirmed dates. Excluded rather than guessed at.

## Source-sector classification reasoning

Domains already present in `taxonomy.py`'s `DOMAIN_SECTOR_MAP` were used
as-is: `wmagazine.com`, `marieclaire.com`, `wwd.com`, `modernluxury.com`,
`wallpaper.com`, `runwaylive.com`, `anothermag.com` (all `editorial`),
`whowhatwear.com` (`retail`).

**`cnn.com`** is not yet in `DOMAIN_SECTOR_MAP`. Verified via its coverage
(a dedicated CNN Style vertical with named bylines covering red-carpet
fashion) that it is a staffed general-news network with real fashion
editorial output, the same pattern already accepted for `nytimes.com`
(general newspaper, `editorial`). Treated as `editorial` in this report's
`source_sectors` for that reason, but this mapping was **not** added to
`taxonomy.py` — this task's scope is limited to `data/reports/2026-05-18.json`
and this log file. Flagged here as a candidate for a future
taxonomy-gap-fix run.

**`hungermag.com`** was researched (a real, staffed UK quarterly fashion/
culture magazine founded 2011) but not cited in the final report and not
added to `taxonomy.py` — see "signals included" above for why it wasn't
needed once WWD/Modern Luxury/Wallpaper* already corroborated the Dior
signal.

Several low-quality aggregator/listicle domains surfaced in search results
(`iblingjewels.com`, `storynews.us`, `news.amomama.com`, `entertainmentnow.com`,
`famedelivered.com`, `whatgoesaroundnyc.com`, `ouispeakfashion.com`,
`lesfacons.com`, `futurefestival.com`, `trendhunter.com`,
`fashionwiredaily.net`) were deliberately excluded from `source_domains` and
from the "credible" count feeding `source_sector_breakdown` — these republish
wire/agency photos under no named masthead or byline, the same pattern
`taxonomy.py`'s existing "skipped, not added" comments describe for other
rejected domains (e.g. `outfittrends.com`, `cafedelhomme.com`). They were
still counted toward `sources_scanned` (29 total distinct fashion-adjacent
domains surfaced across all 11 queries) since that field describes search
surface area, not citation-worthiness.

## Confidence discipline

All three signals had `confidence` computed via `derive_confidence()` and
adopted as-is (`confidence_source: "derived"` on all three) rather than
manually overridden — no borderline judgment call was needed to deviate from
the formula's output this run. The Gucci/Dior split (`high` vs. `medium`)
despite both being single-designer-show debuts illustrates the formula
working as intended: cross-sector corroboration, not the "bigness" of the
event, is what the archive's confidence tier actually measures.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-05-18')); print('VALID')"
-> VALID (no warnings; report_date matches collection_window.end, no schema errors)
```

Confidences produced by `derive_confidence()`: `["medium", "medium", "high"]`
for `cannes-2026-red-carpet-cluster`, `dior-cruise-2027-anderson-lacma`, and
`gucci-cruise-2027-demna-times-square` respectively.

## Files touched

- `data/reports/2026-05-18.json` (new)
- `docs/agent-logs/real-research-2026-05-18.md` (this file, new)

Per task scope, no other file was touched, nothing was committed, and no git
command was run.
