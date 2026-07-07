# Real report: 2026-07-06

## Task

Produce the first genuine report for `collection_window: {"start": "2026-06-30", "end":
"2026-07-06"}`, `report_date: "2026-07-06"` — the most recent complete week as of the
real session date (2026-07-06), replacing the purged synthetic archive with real,
WebSearch/WebFetch-verified research. Scope: only `data/reports/2026-07-06.json` and this
log file. No commit, no other files touched.

## Precedent reading

Read `src/report_schema.py` (Report/Signal dataclasses, `validate_report()`,
`derive_confidence()`), `src/taxonomy.py` (`SOURCE_SECTORS`, `DOMAIN_SECTOR_MAP`,
`classify_source()`), `docs/agent-logs/real-report-2028-04-24.md` (thin-week discipline
example), `docs/confidence-discipline-precedents.md` (all 17 precedents), and the three
existing real reports on disk (`data/reports/2026-05-04.json`, `2026-05-11.json`,
`2026-05-18.json`) to match current archive conventions for a genuinely-researched
report (the 2026-05-18 report's structure — `executive_summary` prose style, `evidence`/
`index_note` split, `source_domains` restricted to `DOMAIN_SECTOR_MAP`-mapped bare
domains — was used as the direct template).

## WebSearch queries run and what each returned

1. `"fashion news July 2026 haute couture Paris"` — returned genuine, real coverage:
   Paris Haute Couture Week Fall/Winter 2026-27 runs July 6-9, 2026 (fhcm.paris,
   runwaylive.com, graziadaily.co.uk, fashionista.com, sortiraparis.com,
   fashionnetwork.com, wallpaper.com). Confirmed Pierpaolo Piccioli's Balenciaga debut,
   Duran Lantink's Jean Paul Gaultier debut, Manish Malhotra's couture-calendar debut,
   Fendi's off-calendar Rome show.
2. `"fashion trends this week July 2026"` — mostly retail/shopping-guide content
   (whowhatwear.com "what to buy" listicles) and a RUSSH "fashion moments" roundup;
   also surfaced "cool girl summer" trend framing (jerseys, babydoll dresses, fringe)
   which prompted the follow-up queries below.
3. `"vogue.com July 2026 trend report"` — thin results; no genuine dated Vogue piece
   specific to this window surfaced (a YouTube video and general summer-trend pieces
   only). Not used as a source.
4. `"Paris Haute Couture Fall/Winter 2026 schedule dates"` — confirmed July 6-9, 2026
   dates and house lineup via fhcm.paris and multiple editorial previews (ouispeakfashion.com,
   sortiraparis.com, thesqua.re, fashionprfirm.com — none of the last four are in
   `DOMAIN_SECTOR_MAP`, so none were cited as `source_domains`).
5. `"Fashionista Paris Haute Couture Week July 2026 provisional calendar Balenciaga
   Piccioli debut"` — confirmed WWD's and Fashionista's preview pieces (both dated
   late June 2026, before the window's July 6 close) naming the same debuts.
6. `""babydoll dress" trend summer 2026"` — found the babydoll-dress revival narrative
   across marieclaire.com, whowhatwear.com, grazia.my (unmapped), fashionisers.com
   (unmapped), tying it to Olivia Rodrigo's styling and to Spring 2026 runway origins
   (Ulla Johnson, Chloe, Miu Miu).
7. `"fringe trend 2026 handbags fashion"` — found marieclaire.com and wwd.com pieces,
   but on WebFetch inspection these were Spring-2026-season forecast content (fringe)
   or a December 2025 forward-looking handbag-trends piece — excluded per precedent 14
   (forecast pieces are not evidence of a present-window signal).
8. `"World Cup 2026 jerseys fashion trend soccer style"` and `"World Cup jersey style
   street style late June 2026"` — found genuine, well-corroborated "blokecore"/jersey
   street-style coverage (dazeddigital.com, soccerbible.com, whowhatwear.com,
   complex.com) but every dated instance found (mid-June 2026) predates the window's
   June 30 start — excluded per precedent 9 (external-calendar-event-driven signals
   held down/excluded until tracked past the event or a fresh in-window source
   appears).
9. `"Chanel Balenciaga couture July 6 2026 review show"` — confirmed the Chanel
   (Matthieu Blazy, July 7) and Balenciaga (Pierpaolo Piccioli, July 8) show dates,
   both after this window's July 6 close, so their content itself is not logged here;
   used only to firm up the calendar-signal's corroboration.
10. `"Olivia Rodrigo babydoll dress July 2026"` — corroborated the babydoll-controversy
    narrative (refinery29.com, variety.com, stanforddaily.com, realitytea.com — none
    mapped in `DOMAIN_SECTOR_MAP`, so not cited) and specifically the cream Modomorpho
    micro-minidress detail used in the signal's `evidence` field.

## WebFetch verification (publish dates)

- `fashionista.com` couture-schedule article: 403 (paywall/blocked), not directly
  fetchable, but corroborated by other search results and the WWD/Grazia fetches below;
  retained as a `source_domains` citation on the strength of the search-result snippet
  plus independent corroboration from wwd.com and graziadaily.co.uk.
- `marieclaire.com` babydoll-dress article: confirmed publish date **July 6, 2026** —
  inside the window, in fact on its closing day.
- `whowhatwear.com` soccer-jersey-styling article: confirmed publish date **June 15,
  2026** — outside the window (this, plus the Dazed June 18 date below, is why the
  jersey signal was excluded rather than logged).
- `wwd.com` couture-schedule article (via `tollbit.wwd.com` redirect): 402 Payment
  Required, not directly fetchable; retained as a citation on the strength of the
  search-result content plus independent corroboration.
- `dazeddigital.com` World Cup kits article: confirmed publish date **June 18, 2026** —
  outside the window.
- `graziadaily.co.uk` couture-week article: confirmed as "Updated July 6th, 2026 at
  9:37pm" — same-day coverage of the actual July 6 opening shows (Schiaparelli, Dior),
  the strongest single piece of evidence that the couture signal is genuinely dated
  inside this window and not just a forward-looking preview.
- `marieclaire.com` handbag-trends-2026 article: confirmed publish date **December 18,
  2025** — well outside any reasonable "near this window" reading; excluded per
  precedent 14.

## Signals included and reasoning

**1. `couture-fw26-paris-opening-shows`** (medium confidence, manual override) — Paris
Haute Couture Week Fall/Winter 2026-27's calendar (institutional: fhcm.paris) plus
editorial preview/same-day coverage (fashionista.com, wwd.com, runwaylive.com,
wallpaper.com, graziadaily.co.uk) of the July 6 opening shows (Schiaparelli's oceanic
surrealism, Dior's Lynda-Benglis-referencing second Jonathan Anderson collection).
Origin: `designer_originated` (first-party couture shows). Confidence mechanically
computes `high` (count 6, 2 sectors: editorial + institutional), but manually held at
`medium` per **precedent 2** (this archive's own past `couture-fwXX-designer-debuts`
signals have repeatedly been held at medium when corroboration is really one sector,
editorial, describing the same event) and **precedent 7** (the institutional citation
here confirms only the calendar/schedule fact, not independent corroboration of the
shows' actual aesthetic content, so the nominal two-sector count overstates real
diversity). `confidence_source: "manual"`.

**2. `babydoll-dress-revival-rodrigo-controversy`** (medium confidence, manual
override) — babydoll-dress silhouette revival, driven this window by Olivia Rodrigo's
styling controversy, covered by marieclaire.com (July 6, 2026 — inside the window) and
whowhatwear.com. Origin: `editorial_amplified` (the coverage driver is celebrity
styling/controversy commentary, not a fresh runway presentation — the cited runway
origin is Spring 2026, months prior). Confidence mechanically computes `high` (count 2,
2 sectors: editorial + retail), manually held at `medium` per **precedent 8**
(commercial/service-journalism discount — Who What Wear's celebrity-style vertical and
Marie Claire's own shopping-pick-closing piece both carry this risk even at a
multi-sector, seemingly well-corroborated tier). `confidence_source: "manual"`.

## Signals considered and excluded

- **World Cup 2026 jersey/"blokecore" street-style trend** — genuine, real,
  well-corroborated (dazeddigital.com, soccerbible.com, whowhatwear.com, complex.com)
  and directly analogous to this archive's own precedent 9 worked example
  (`blokecore-world-cup-jersey-styling`, `2027-06-21.json`). Excluded here rather than
  logged because every dated instance found (mid-June 2026) predates this window's
  June 30 start, so there is no in-window-dated source to attach a fresh signal_id to;
  noted in `limitations` and `archive_tags` so a later window can pick this up with
  fresh dated coverage if it recurs.
- **Fringe trend (handbags/ready-to-wear)** — real, but every dated source found was
  Spring-2026-season forecast content or (for the handbag-trends piece specifically)
  published December 18, 2025. Excluded per precedent 14 (forecast/older-season
  content is not evidence of a present-window signal).
- **Chanel (Matthieu Blazy, July 7) and Balenciaga (Pierpaolo Piccioli debut, July 8)
  couture shows** — real and confirmed on the calendar, but both fall after this
  window's July 6 close; their content is not logged here (only referenced as
  context/anticipation inside the couture-calendar signal's `evidence`). A later window
  (covering July 7-13 or similar) is the correct place to log their actual show
  content once it happens and is reported.

## Source-sector classification reasoning

All `source_domains` cited (`fashionista.com`, `wwd.com`, `graziadaily.co.uk`,
`runwaylive.com`, `wallpaper.com`, `fhcm.paris`, `marieclaire.com`, `whowhatwear.com`)
were already present in `taxonomy.py`'s `DOMAIN_SECTOR_MAP` (editorial: fashionista.com,
wwd.com, graziadaily.co.uk, runwaylive.com, wallpaper.com, marieclaire.com;
institutional: fhcm.paris; retail: whowhatwear.com) — no new domain classification was
needed, and none was added, consistent with this task's scope restriction (only
`data/reports/2026-07-06.json` and this log). Several unmapped domains were encountered
during research (refinery29.com, variety.com, stanforddaily.com, realitytea.com,
grazia.my, fashionisers.com, babble-up.com, sortiraparis.com, modemonline.com,
ouispeakfashion.com, thesqua.re, fashionprfirm.com, soccerbible.com — wait, soccerbible.com
is actually already mapped editorial per taxonomy.py, but its World Cup content was
excluded on date grounds regardless) — these were used only as background corroboration
in research, never cited in `source_domains`, and `taxonomy.py` was not touched.

## Confidence discipline

Both signals had their mechanically-derived confidence (`high` in both cases) manually
overridden down to `medium`, citing precedents 2/7 (couture signal) and 8 (babydoll
signal) explicitly in each signal's `index_note`/`human_editor_note`, per this archive's
established discipline of not letting raw corroboration-count/sector-count formulas
override known structural caveats.

## Report authored

Built with `src/report_schema.py`'s `Report`/`CollectionWindow`/`Signal` dataclasses and
saved via `save_report()` (no hand-written JSON) — see
`build_report_2026-07-06.py` in the session scratchpad (not committed to the repo).
`collection_status: "normal"` (two genuine, well-corroborated signals — not a thin
week). `review_status: "reviewed"`, `reviewed_by: "real-research-pilot-2026-07-06"`.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-07-06'))"
-> no output / no exception raised (OK)
```

No other verification commands (`tsc`, `next build`, `validate_all_reports.py`) were run
per this task's scope restriction (only the report JSON and this log were to be touched;
no other files, no commit).

## Files touched

- `data/reports/2026-07-06.json` (new)
- `docs/agent-logs/real-research-2026-07-06.md` (this file, new)

No other file was read-then-modified, no commit was made, `.env` was never read.
