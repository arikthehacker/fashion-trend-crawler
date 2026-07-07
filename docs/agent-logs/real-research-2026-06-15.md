# Real research: 2026-06-15

## Task

Produce one genuinely-researched report for `collection_window`
`{"start": "2026-06-09", "end": "2026-06-15"}`, `report_date: "2026-06-15"` (matches
`collection_window.end` per the run-92 convention in `report_schema.py`). This is one of
several agents replacing the purged synthetic archive with real reports for real past
weeks.

## Precedent reading

Read `src/report_schema.py` (Report/Signal dataclasses, `validate_report()`,
`derive_confidence()`), `src/taxonomy.py` (controlled vocab, `DOMAIN_SECTOR_MAP`,
`classify_source()`), and `docs/agent-logs/real-report-2028-04-24.md` for the honest-thin-
week discipline. Also read the two existing real reports on disk
(`data/reports/2026-05-04.json`, `data/reports/2026-05-11.json`) as the closest live
precedent for how a real, dated, WebSearch-sourced report should be built and worded --
`2026-05-11.json`'s Met Gala/Costume Institute framing (a calendar event one day outside
the window, included because its recap coverage was dated inside the window) turned out
to be directly reusable for this window's Tony Awards situation. Skimmed
`docs/confidence-discipline-precedents.md`'s precedent index and read precedent 9
("Signals driven by an external calendar event are held down until tracked past that
event") in full, since it applies directly to the Tony Awards signal below.

## WebSearch queries run and what each returned

1. `"men's fashion week June 2026 Paris Milan Spring Summer 2027"` -- confirmed Milan
   Men's SS27 runs June 19-23, 2026 and Paris Men's SS27 runs June 23-28, 2026 -- both
   **after** this window closes (June 15). Established the window sits before fashion
   month starts.
2. `"Milan menswear Spring Summer 2027 June 2026 review"` -- confirmed Milan coverage
   (Ralph Lauren, Thom Browne, Dolce & Gabbana, Brioni, Saul Nash) is all dated to the
   June 19-23 show week itself, outside this window.
3. `"Paris Fashion Week Men's June 2026 trends"` -- confirmed Paris SS27 runs June 23-28,
   also outside this window; Dior/Louis Vuitton/Sacai/Celine/Hermès coverage dated to
   that week.
4. `"Pitti Uomo June 2026 dates"` -- confirmed Pitti Uomo 110 (Florence) runs June 16-19,
   2026 -- starts the day *after* this window closes.
5. `"vogue.com trend June 2026"` -- no results returned.
6. `"fashion trends week of June 9 2026"` -- returned Trend Hunter and Who What Wear
   trend-listicle content (crochet skullcaps, wedge sandals, asymmetric hemlines). Traced
   further (queries 7-9 below) to confirm these are recirculated content from primary
   reporting dated well before this window, not new-this-window coverage.
7. `"whowhatwear "June 2026" trend"` -- confirmed Who What Wear's June trend round-ups are
   ongoing seasonal listicle content (retail sector), not new dated reporting specific to
   this window.
8. `"crochet skullcap trend 2026"` -- traced the trend to Copenhagen Fashion Week's
   January 2026 (Fall/Winter 2026) season; not a this-window development.
9. `"wedge heels sandals trend summer 2026"` and
   `"wwd.com "Wedge Sandal" summer 2026 shoe trend publish date June"` -- found the primary
   WWD piece on this trend is dated **May 17, 2026** -- a month before this window opens.
   Excluded both crochet-cap and wedge-sandal threads as signals; see limitations.
10. `""June 2026" fashion editorial garment trend runway street style"` -- returned only
    generic SS26/streetwear round-up content with no window-specific dated reporting.
11. `""June 10, 2026" OR "June 11, 2026" OR "June 12, 2026" fashion trend"` and
    `""June 9" OR "June 13" 2026 style street style report"` -- returned only the same
    recirculating June listicle content (Trend Hunter, Who What Wear, thedressoutlet.com),
    no new window-specific event.
12. `"Tony Awards 2026 red carpet fashion June"` -- found the 2026 Tony Awards were held
    June 7, 2026 at Radio City Music Hall -- two days before this window opens -- with
    recap/best-dressed coverage from Marie Claire, HelloBeautiful, RTE, E! Online.
13. `"Tony Awards 2026 fashion trend analysis capes sequins recap"` and
    `"Vogue.com Tony Awards 2026 red carpet best dressed"` -- surfaced further recap detail
    (Queen Latifah's feathered cape, Deborah Cox, Megan Thee Stallion, Rachel Zegler,
    Rose Byrne, Danielle Brooks, Cole Escola, Aubrey Plaza, Daniel Radcliffe) and additional
    outlets (madamenoire.com, bossip.com, buzzfeed.com, vogue.ph,
    redcarpet-fashionawards.com, a Substack).
14. `"CFDA Fashion Awards 2026 June date winner"` -- found the **CFDA/Vogue Fashion Fund**
    (distinct from the CFDA Fashion Awards, which remains unresolved per TODO.md/prior
    reports) held its 2026 finalist judged presentations on **June 10, 2026** -- inside
    this window -- with the winner not announced until October 20, 2026.
15. `"CFDA Vogue Fashion Fund finalists presentations June 10 2026 designs themes"` and
    `"wwd.com CFDA Vogue Fashion Fund 2026 finalists presentation collections"` -- found
    independent trade/editorial coverage (WWD x3, Business of Fashion, Fashionista,
    RUNWAY Magazine, nss magazine, The Impression, V Magazine, FashionUnited UK) of the
    June 10 presentations and the CFDA's own announcement, converging on describing the
    finalist cohort's maximalist embellishment (tutus with polka-dot lace, capes with pink
    lily appliques, a sequined lobster-motif garment).
16. `"fashion news June 9 2026"` and `"fashion news June 12 2026"` -- returned brand-
    capsule/retail-opening news (Marine Serre x Under Armour capsule, H.Lorenzo flagship,
    Shopbop pop-up) dated inside/near the window but with no describable garment/
    silhouette/aesthetic content suitable for a style signal -- not logged.
17. `"businessoffashion.com June 2026 report"` -- found BoF's State of Fashion 2026 series
    (published earlier in 2026) and a luxury-industry data report dated June 29, 2026 --
    both outside this window; not logged.
18. `""June 9" OR "June 13" 2026 style street style report"` overlap check and
    `"Tony Awards 2026 fashion recap best dressed "June 9" OR "June 8" 2026"` -- confirmed
    redcarpet-fashionawards.com published a Tony Awards recap dated 2026/06/09 (inside the
    window) and Marie Claire's best-dressed piece is also dated June 9.

## Signal reasoning

**Included -- `cfda-vogue-fashion-fund-2026-finalists`:** the CFDA/Vogue Fashion Fund's ten
2026 finalists presented to judges on June 10, 2026, inside this window. Corroborated by
the program's own institutional announcement (cfda.com) plus four independent trade/
editorial outlets (WWD, Business of Fashion, Fashionista, RUNWAY Magazine) describing the
same presentations rather than reprinting the CFDA release -- two genuinely distinct
sectors, `derive_confidence()` computes `high` on its own terms (corroboration count 5,
2 distinct sectors), no manual override applied. `origin_classification` set to
`designer_originated` since this is garments shown directly by their makers to a judging
panel, not a runway show or retail assortment. Volatility set to `emerging` rather than
`flash` because the process (Material Innovation Challenge and other brand challenges)
continues through the October 20 winner announcement, unlike a same-day calendar event.

**Included -- `tony-awards-2026-red-carpet`:** the 2026 Tony Awards ceremony itself was
June 7, two days before this window opens, but recap/best-dressed coverage (Marie Claire,
published June 9; HelloBeautiful) was published inside the window. Applied the same
resolution the `2026-05-11.json` report used for a Met Gala one day outside that window:
included, with the outside-window event date noted explicitly in `limitations` rather than
silently treated as in-window. Precedent 9 (calendar-driven signals held down until
tracked past the event) applies directly -- volatility marked `flash`, and confidence is
not pushed above what `derive_confidence()` computes on raw corroboration alone (`medium`:
count 2, single sector, editorial). Two additional outlets with real, dated coverage of
this event -- vogue.ph and redcarpet-fashionawards.com -- were found but are not yet in
`taxonomy.py`'s `DOMAIN_SECTOR_MAP`; left out of `source_domains` rather than cited
unclassified, since editing `taxonomy.py` is out of scope for this report (flagged in
`limitations` as a taxonomy gap for a future run).

**Excluded -- wedge sandal / crochet skullcap / asymmetric hemline seasonal listicles:**
surfaced repeatedly across multiple search angles, but every attempt to trace primary
reporting found dates well outside this window (WWD's wedge-sandal piece: May 17, 2026;
crochet-cap coverage tied to Copenhagen Fashion Week's January 2026 season). These are
ongoing seasonal trends being recirculated in June round-up/listicle content, not new
this-window developments. Not logged as signals, consistent with this archive's discipline
against manufacturing in-window coverage from recirculated, off-window primary reporting
(see `real-report-2028-04-24.md`'s precedent for the same call).

**Excluded -- brand-capsule/retail-opening news (Marine Serre x Under Armour capsule,
H.Lorenzo flagship opening, Shopbop pop-up):** genuinely dated inside/near the window, but
none carries describable garment/silhouette/aesthetic content beyond "a capsule/store
launched" -- not a style signal in this project's sense, and not logged.

**Considered and rejected -- Milan/Paris Men's SS27, Pitti Uomo 110:** all three
confirmed via search to fall after this window closes (Pitti Uomo June 16-19; Milan
June 19-23; Paris June 23-28). No designer_origin/runway coverage of men's fashion month
exists yet for this window; expected to surface starting the next window's report.

## Source-sector classification reasoning

All source domains cited in this report's `top_signals[].source_domains`
(`cfda.com`, `wwd.com`, `businessoffashion.com`, `fashionista.com`, `runwaylive.com`,
`marieclaire.com`, `hellobeautiful.com`) are already present in `taxonomy.py`'s
`DOMAIN_SECTOR_MAP` from prior runs -- no new domain was added to the map, since editing
`taxonomy.py` is out of scope for this task. Two domains with real, dated coverage of the
Tony Awards were found but are *not* yet mapped -- `vogue.ph` (Vogue Philippines, a
Conde Nast regional Vogue edition, the same pattern as the already-mapped
`voguearabia.com`/`voguescandinavia.com`/`vogueadria.com`) and `redcarpet-fashionawards.com`
(a dedicated red-carpet-fashion recap site, not yet researched in depth). Both were
deliberately excluded from this report's `source_domains` rather than cited unclassified,
and flagged in `limitations` as a taxonomy gap for a future run to research and classify
properly (per the project's established WebSearch-before-classifying convention).

## Report authored

Built with `src/report_schema.py`'s `Report`/`Signal`/`CollectionWindow` dataclasses and
saved via `save_report()` (no hand-written JSON) --
`C:\Users\User\AppData\Local\Temp\claude\...\scratchpad\build_report_2026_06_15.py`.
`collection_status: "normal"` (two well-corroborated signals, not a thin week).
`review_status: "reviewed"`, `reviewed_by: "real-research-pilot-2026-06-15"`.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-06-15'))"
-> VALID, no errors, no warnings
```

No fabricated signal, quote, or source domain was introduced. `.env` contents were never
read, printed, or referenced.

## Files touched

- `data/reports/2026-06-15.json` (new)
- `docs/agent-logs/real-research-2026-06-15.md` (this file, new)

No other file was touched. No commit was made, per task scope.
