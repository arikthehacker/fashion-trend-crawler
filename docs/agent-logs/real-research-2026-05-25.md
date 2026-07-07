# Real report: 2026-05-25

## Task

Produce a genuinely-researched report for a real past week,
`collection_window: {"start": "2026-05-19", "end": "2026-05-25"}`,
`report_date: "2026-05-25"` (matches `collection_window.end` per the run-92
convention documented in `report_schema.py`). This is a real week (not a
fictional forward date past the training-cutoff scaffold), so genuine
WebSearch results were expected and found, unlike some of the sibling
fictional-2028-week reports being replaced elsewhere in this loop.

Two adjacent-week reports were already on disk when this run started
(`data/reports/2026-05-04.json`, `data/reports/2026-05-11.json`), produced by
other concurrent agents. Read `2026-05-11.json` in full before starting to
match established voice/structure and to check what it had already deferred
into this window (see below).

## WebSearch queries run and what each returned

1. `fashion trends May 2026 street style` -- generic evergreen 2026
   streetwear-trend listicles (Complex, Harper's Bazaar Singapore, printify,
   asphaltgold, etc.), no window-specific dated coverage. Not used.
2. `vogue.com trend report May 2026` -- Vogue Scandinavia SS26 trend piece
   and a Vogue Business Summit mention, neither dated/specific to this
   window. Not used.
3. `resort 2027 collection preview May 2026` -- surfaced the real anchor
   events of this general period: Gucci Resort 2027 (Tom + Lorenzo, posted
   May 18), Dsquared2 Resort 2027 (WWD, May 27 -- outside this window),
   Christian Dior Resort 2027 at LACMA (lesfacons.com, May 18), Stella
   McCartney Resort 2027. Used to identify Gucci as an in-window/edge-of-
   window candidate; Dior and Dsquared2 investigated further and excluded
   (see limitations below).
4. `whowhatwear trend report May 2026` -- mostly evergreen "summer 2026"
   trend content (swimwear, cool-girl, workwear), no window-specific dating.
   Not used directly, but whowhatwear.com later resurfaced with genuine
   Cannes-specific content (query 15).
5. `"May 2026" fashion week runway news` -- Denver Fashion Week, Runway 7
   Miami, FIT's Future of Fashion show -- none of these three are within
   this window's dates or a genuine trend signal (student/regional show
   listings). Not used.
6. `Jonathan Anderson Dior Resort 2027 LACMA show date May 2026` -- confirmed
   the Dior Cruise 2027 "Wilshire Boulevard" show was dated May 13, 2026 --
   six days before this window opens. Investigated in detail (see below) and
   excluded from top_signals as out-of-window.
7. `Cannes Film Festival 2026 red carpet fashion trend` -- CNN, W Magazine,
   CBC, Marie Claire, PORTER (Net-a-Porter) all returned genuine, dated
   Cannes-specific fashion coverage (bold color, sheer/transparent
   silhouettes, 90s minimalism, feathers). This became the basis of signal 1.
8. `Gucci Resort 2027 collection Demna review` -- WWD, AnOther, The
   Impression, Vogue Adria, and others returned genuine reviews of Demna's
   Times Square "GucciCore" show. Basis of signal 2.
9. `Gucci Resort 2027 Times Square show date May 19 2026` -- confirmed (with
   some cross-source date disagreement: May 16 vs. May 19, 2026) and
   surfaced Vogue Hong Kong (voguehk.com) as an additional reviewing outlet.
10. `Cannes Film Festival 2026 closing ceremony date May 23` -- confirmed via
    Wikipedia and festival-cannes.com that the 79th Festival de Cannes
    closing ceremony was May 23, 2026 -- inside this window, establishing
    that at least the festival's final days/closing coverage genuinely falls
    in the May 19-25 range.
11. `Chanel Dsquared2 Stella McCartney resort 2027 show date May 20 21 22
    2026` -- did not return precise dates for these three; Dsquared2 was
    separately confirmed (query 3) as May 27, outside this window. Not used
    further.
12. `Matthieu Blazy first Chanel resort collection Biarritz date May 2026` --
    confirmed via multiple outlets' publication dates (April 28-30, 2026)
    that this show was in late April 2026, well outside this window.
    Excluded (see limitations).
13. `sheer trend transparent dressing 2026 editorial` -- mostly undated
    evergreen "2026 sheer trend" listicle/blog content (burcinboz.com,
    bespokeaistylist.com, runwaylive.com generic pieces, Marie Claire spring
    piece dated around March). Confirms the sheer trend has broader
    evergreen coverage beyond Cannes specifically, but none of this was used
    as evidence for the logged signal -- only the Cannes-dated coverage
    (query 7/15) was used, to avoid treating undated listicle content as
    window-specific.
14. `"Gucci" "Times Square" Demna resort review site:wwd.com OR
    site:anothermag.com May 2026` -- pulled fuller detail from the WWD and
    AnOther reviews (celebrity attendance, "GucciCore" naming, collection
    contents) used in signal 2's evidence text.
15. `Cannes 2026 fashion trend roundup "May 2026" sheer 90s minimalism` --
    Style Rave's "Celebrities, Fashion and Beauty Trends That Defined Cannes
    2026" and Who What Wear's "over 50s French fashion trends" piece, both
    explicitly framed as Cannes-2026-specific trend roundups (not generic
    2026 listicles), and both naming the 90s-minimalism thread and citing
    the FX series "Love Story" (Carolyn Bessette-Kennedy) as its driver.
    These became the strongest, most directly dated evidence for signal 1.

## Signals included and why

**`cannes-2026-sheer-90s-minimalism-red-carpet`** -- included because the 79th
Festival de Cannes' closing days (through the May 23, 2026 closing ceremony)
fall squarely inside this window, and multiple outlets (marieclaire.com,
stylerave.com -- editorial; whowhatwear.com, net-a-porter.com -- retail)
independently published Cannes-2026-specific trend coverage naming the same
sheer/transparent-dressing and 90s-minimalism threads. `source_corroboration_
count: 5`, `source_sectors: ["editorial", "retail"]`.

**`gucci-guccicore-resort-2027-times-square`** -- included because Demna's
Times Square Resort 2027 show is a real, dated (May 16 or May 19, 2026,
sources disagree) designer-originated event reviewed independently by five
editorial/trade outlets (wwd.com, anothermag.com, theimpression.com,
runwaylive.com, voguehk.com) converging on the same "GucciCore" naming and
collection description. `source_corroboration_count: 5`, `source_sectors:
["editorial"]`.

## Signals/candidates considered and excluded

- **Dior Cruise 2027 "Wilshire Boulevard" (Jonathan Anderson's Dior debut,
  LACMA, May 13, 2026)** -- a major real story, extensively covered (Marie
  Claire, Hollywood Reporter, Hypebeast, WWD, Modern Luxury, etc.), but the
  show date is six days before this window opens. The prior report
  (`2026-05-11.json`) had explicitly flagged it as "expected to surface in
  the next window's search"; it actually falls in the May 12-18 gap week
  between that report and this one (not yet covered by any report on disk as
  of this run), not in this May 19-25 window. Excluded and noted in
  `limitations` rather than silently absorbed into this window on the
  strength of its size as a story.
- **Chanel Cruise 2026/27 (Matthieu Blazy's Chanel debut, Biarritz)** --
  confirmed via multiple outlets' publication dates (April 28-30, 2026) to
  be late April 2026, well outside this window. Excluded.
- **Dsquared2 Resort 2027** -- confirmed dated May 27, 2026, two days after
  this window closes. Excluded.
- Generic "2026 fashion trends" / "summer 2026 trends" listicle content
  (queries 1, 2, 4, 13) -- undated or dated well outside this window
  (evergreen SEO content, some visibly published months earlier). Not used
  as evidence for either signal, consistent with this archive's precedent 14
  (forecast/undated-listicle content is not evidence of a present, dated
  signal).

## Confidence discipline

Read `docs/confidence-discipline-precedents.md` in full before assigning
confidence.

- **Cannes signal**: `derive_confidence()` computes `high` mechanically
  (count 5, two distinct sectors: editorial + retail). Manually overridden
  down to `medium` under **precedent 9** (calendar-driven external-event
  signals held down until tracked past the event) -- the entire signal is
  driven by one film festival's closing days, with genuinely unknown
  durability past the event. `volatility: "flash"` carries the same
  single-event caveat, following the exact technique the 2026-05-11 report's
  Met Gala signal used (considered precedent 9 there too, and used `flash`
  volatility rather than double-penalizing an already-capped signal).
  `confidence_source: "manual"`.
- **Gucci signal**: `derive_confidence()` computes `medium` mechanically
  under **precedent 2** (raw corroboration count doesn't create cross-sector
  diversity; all five outlets resolve to `editorial`). Precedent 9 was
  considered and explicitly *not* applied as a further downgrade: a house's
  own runway show is not an event external to the fashion calendar the way a
  film festival or a sporting tournament is -- it is the archive's normal
  occasion for a designer-originated signal to first appear -- and the
  signal is already at `medium` via precedent 2 with no room to
  double-penalize. `confidence_source: "derived"`.
- Both signals' `confidence_source`/mechanical-vs-assigned values were
  cross-checked programmatically against `derive_confidence()` before saving
  (see the build script's printed output below) rather than asserted by
  hand.

## Source-sector classification reasoning

All domains cited in `source_domains` for both signals
(marieclaire.com, stylerave.com, whowhatwear.com, net-a-porter.com, wwd.com,
anothermag.com, theimpression.com, runwaylive.com) are already present in
`taxonomy.py`'s `DOMAIN_SECTOR_MAP`, classified `editorial` or `retail`
respectively -- no new classification judgment was needed for those.

**`voguehk.com` (Vogue Hong Kong)** is a domain not yet in `DOMAIN_SECTOR_MAP`.
Classified as `editorial` in this report's `source_sectors` by the same
established pattern already used for Vogue's other Conde Nast regional
editions already mapped in `taxonomy.py` (`voguearabia.com`,
`voguescandinavia.com`, `vogueadria.com`) -- Vogue Hong Kong is the
Hong Kong/Greater China regional edition of the same publisher family,
carrying the same staffed-masthead, first-party-review pattern as those
entries. This reasoning is recorded here rather than added to
`taxonomy.py` itself, per this task's file scope (only `data/reports/
2026-05-25.json` and this log were to be touched); a future run closing
taxonomy gaps can add `voguehk.com` to `DOMAIN_SECTOR_MAP` formally, citing
this reasoning.

## Report authored

Built with `src/report_schema.py`'s `Report`/`CollectionWindow`/`Signal`
dataclasses via a script (not hand-written JSON) and saved with
`save_report()`, which computed `content_hash` and ran `validate_report()`
automatically. `collection_status: "normal"` (two real, independently
corroborated signals were found -- not a thin week). `review_status:
"reviewed"`, `reviewed_by: "real-research-pilot-2026-05-25"`.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-05-25'))"
-> VALID (no output/errors)
```

The build script also printed a mechanical-vs-assigned confidence
cross-check for both signals before saving:

```
cannes-2026-sheer-90s-minimalism-red-carpet: assigned='medium' mechanical='high' source='manual'
gucci-guccicore-resort-2027-times-square: assigned='medium' mechanical='medium' source='derived'
```

Both match the reasoning documented above and in each signal's
`human_editor_note`.

## Files touched

- `data/reports/2026-05-25.json` (new)
- `docs/agent-logs/real-research-2026-05-25.md` (this file, new)

No other file was touched. No commit was made. `.env` contents were never
read, printed, or referenced.
