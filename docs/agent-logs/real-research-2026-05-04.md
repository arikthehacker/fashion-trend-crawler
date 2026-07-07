# Real research report: 2026-05-04

## Task

First genuinely-researched report for this archive following the purge of 95
synthetic/placeholder reports carrying fictional forward dates (2026-2028) --
see `data/examples/synthetic-reports/README.md` and TODO.md's "human
decision" entry. This report covers a real, WebSearch-verifiable past week:
`collection_window: {"start": "2026-04-27", "end": "2026-05-04"}`,
`report_date: "2026-05-04"` (matches `collection_window.end` per the run-92
dating convention documented in `report_schema.py`).

`data/reports/` is currently empty on disk (all 95 prior files renamed to
`data/examples/synthetic-reports/` per `git status`), so this is a first
file, not a continuation of any prior real report.

## WebSearch queries run and what each returned

1. `"fashion trend news April 27 2026"` -- returned WWD's spring 2026 denim
   runway roundup, explicitly dated **April 27, 2026** (the window's opening
   day) -- a genuinely, precisely dated hit. Also returned several
   season-long "Spring/Summer 2026 trends" evergreen roundups (Refinery29,
   ASOS, Who What Wear, Marie Claire) not specifically dated within the
   window.
2. `"street style trend early May 2026"` -- returned Harper's Bazaar
   Singapore's SS26 street style roundup, Who What Wear's Paris street-style
   shopping piece, and Trendalytics' SS26 street-style insights report.
   Content describes an ongoing spring 2026 street-style cluster (scarves,
   team jerseys, plaid, midi skirts) documented across the season rather
   than newly emerging in this specific week.
3. `"vogue.com trend report May 2026"` -- returned mostly Vogue Scandinavia
   (a different regional edition) and a Vogue Business Summit report, not
   vogue.com's own trend coverage. No usable dated signal from this query;
   not used.
4. `"Met Gala 2026 fashion May 4"` -- returned an NPR piece dated exactly
   **May 4, 2026** (the window's closing day) previewing the Met Gala's
   "Costume Art" exhibition and "Fashion Is Art" dress code. Strong, tightly
   dated hit.
5. `""April 2026" fashion week resort 2027 preview"` -- returned mostly
   fashion-week-calendar/directory sites (Fashion Week Online, T-Fashion,
   CFDA calendar, hotel blog) and WWD's Resort 2027 runway section landing
   page, but no article specifically dated within the window with
   substantive resort-2027 content -- Resort 2027 previews appear to run
   later (June 2026 per a Veronica Beard review found). Not used as a
   signal.
6. `"Met Gala 2026 theme "Costume Art" dress code coverage"` -- corroborated
   query 4: Metropolitan Museum of Art press release, E! Online (two
   articles: theme/dress-code explainer and a celebrities roundup), CBS News
   New York. All describe the same May 4 event; used to build the Met Gala
   signal's evidence and source_domains.
7. `"whowhatwear paris street style shopping April 2026"` -- returned several
   Who What Wear street-style pieces (Paris shopping, tassel-scarf trend,
   Milan/Paris street-style shopping, spring outfit ideas) corroborating the
   scarf/accessories cluster from query 2.
8. `"dieworkwear substack fashion April 2026"` -- returned only general
   newsletter/subscriber/traffic description of Derek Guy's Die, Workwear
   Substack (SimilarWeb analytics, cross-references from other newsletters),
   no specific dated claim about this window. **Excluded** -- checked in
   good faith per this project's practice of considering independent
   criticism, but nothing substantive enough to log as a standalone signal.
9. `""May 2026" street style scarf jersey trend fashion week"` and
   `"harpersbazaar.sg spring summer 2026 street style trends scarves jerseys
   plaid"` -- follow-up queries to pin down the accessories cluster in more
   detail (silk-scarf-as-garment framing, jersey styling, plaid/"school
   chic" framing); both corroborated and added detail to the same cluster
   already found in queries 2 and 7, not a new signal.

## Signals included and reasoning

**1. `met-gala-2026-costume-art`** (confidence: high, derived) -- the
most tightly and verifiably dated item found: an institutional press
release (metmuseum.org) plus same-day/preview broadcast and entertainment
press (npr.org, cbsnews.com, eonline.com x2) all describing the same named
event (Met Gala, Monday May 4, "Fashion Is Art" dress code / "Costume Art"
exhibition, named co-chairs Beyonce/Nicole Kidman/Venus Williams/Anna
Wintour, honorary chairs Jeff Bezos/Lauren Sanchez Bezos, Vogue as official
livestream host). `source_corroboration_count: 5`, `source_sectors:
["institutional", "editorial"]` -> `derive_confidence()` returns `"high"`
(count >= 2 and >= 2 distinct sectors), matching the assigned value (cross-
checked programmatically in the build script, not just by eye).
`origin_classification` set to `"unclear"` rather than forced into an
existing bucket -- none of `designer_originated` / `editorial_amplified` /
`retail_adopted` / `social_amplified` / `platform_native` / `archive_revival`
accurately describes "an institution setting an annual gala theme,"
explained in the signal's own `index_note` so a future reader isn't left
guessing why. `volatility: "flash"` -- a single dated annual event, not an
ongoing trend.

**2. `ss26-street-style-accessories-cluster`** (confidence: high, derived) --
oversized silk scarves worn as garments (not just accessories), team
jerseys styled outside sport context, plaid/check prints, and midi skirts,
independently corroborated across Harper's Bazaar Singapore (editorial),
Who What Wear (retail, already mapped in `taxonomy.DOMAIN_SECTOR_MAP`), and
Trendalytics (trade_intelligence). `source_corroboration_count: 6`,
3 distinct sectors -> `derive_confidence()` returns `"high"`. Explicitly
flagged in the signal's own `index_note` and in `limitations` as season-long
documentation (spring/summer 2026 runway-to-street coverage spanning
March-May), not a claim that this specific cluster is new to this
particular seven-day window -- included because the underlying discourse is
real and multiply corroborated, but framed honestly about its actual time
horizon rather than implied as week-specific. `origin_classification`
`"retail_adopted"` (the cited evidence centers on documented street-style/
consumer wear; runway origination at Hermes/Celine/Miu Miu/Lanvin is noted
in `evidence` for traceability but is not itself what's being scored).

**3. `spring-2026-denim-wwd`** (confidence: medium, derived) -- WWD's spring
2026 denim runway roundup, the one item precisely dated to April 27 (the
window's opening day). Single source only (`source_corroboration_count:
1`), one high-reliability sector (`editorial` is in
`report_schema.HIGH_RELIABILITY_SECTORS`) -> `derive_confidence()` returns
`"medium"`, matching the assigned value. Not upgraded on the strength of
WWD's reputation alone -- held at the formula's output per this archive's
established confidence discipline.

**Excluded / considered and rejected:**
- Resort 2027 previews (query 5) -- no article found dated within the
  window with substantive content; the real preview activity appears to
  run later (June 2026). Not fabricated to fill a quota.
- Independent criticism / dieworkwear (query 8) -- checked, no dated
  substantive claim found. Noted in `limitations` rather than silently
  dropped.
- vogue.com's own trend coverage (query 3) -- searches surfaced Vogue
  Scandinavia and a Vogue Business Summit report instead of vogue.com's own
  monthly trend content; not used as a standalone signal since it wasn't
  actually found, though vogue.com is cited as one of the Met Gala signal's
  `source_domains` for its confirmed livestream-hosting role (that specific
  fact was corroborated).

## Source-sector classification reasoning for newly-encountered domains

None of these four domains exist yet in `taxonomy.DOMAIN_SECTOR_MAP`.
Per task instructions, `taxonomy.py` itself was **not edited** (out of
scope for this task -- only `data/reports/2026-05-04.json` and this log were
to be touched), so classification here is documented reasoning applied by
hand for this report's `source_sectors` fields, not a codebase change:

- **harpersbazaar.com.sg** -- Harper's Bazaar Singapore, the Singapore-market
  regional edition of Harper's Bazaar. `harpersbazaar.com` (the US edition)
  is already mapped `editorial`; this is the same staffed-editorial,
  regional-edition pattern already accepted for `vogue.mx`, `voguearabia.com`,
  `voguescandinavia.com`, and `vogueadria.com` (all `editorial`). Classified
  **editorial**.
- **eonline.com** -- E! Online, the digital arm of E! (NBCUniversal-owned),
  a staffed entertainment/celebrity news operation running since the late
  1980s with named editorial bylines, covering red-carpet and fashion
  extensively. Same pattern as already-mapped `hellomagazine.com` (staffed
  celebrity/entertainment weekly) and `hollywoodreporter.com` (staffed
  entertainment trade press covering fashion). Classified **editorial**.
- **cbsnews.com** -- CBS News, a major staffed broadcast news network's
  digital news arm. Same "general staffed press covering fashion/culture"
  pattern already accepted for `euronews.com` and `scmp.com`. Classified
  **editorial**.
- **npr.org** -- National Public Radio, a major staffed nonprofit public
  radio/news organization; the specific article used here is culture/arts
  journalism about a museum exhibition and gala. Same general-staffed-press
  pattern as `euronews.com`/`cbsnews.com`. Classified **editorial**.

All four are noted in the report's own `limitations` field so a future
taxonomy-gap-fix run (in the style of runs 93/94/96/98/99/100) can decide
whether to formally add them to `DOMAIN_SECTOR_MAP`.

## Confidence discipline

All three signals' assigned `confidence` values were cross-checked against
`report_schema.derive_confidence()` programmatically inside the build
script (an `assert derived == sig["confidence"]` per signal before calling
`save_report()`), not just eyeballed -- all three matched
(`confidence_source: "derived"` on all three). No override of the formula's
output was needed or used.

`collection_status` is `"normal"` (not `"thin"`) -- three genuinely
corroborated, distinctly dated real-world signals were found this window,
which clears the bar for a normal report rather than an honest empty one.
This is a different outcome from the `2028-04-24` reference report (which
found nothing and correctly went thin) -- the difference is real: this
window is a real past week (session date 2026-07-06, well after the
2026-04-27/05-04 window), so genuine search results exist, whereas the
2028 fictional-calendar report was searching for a date that hasn't
happened and correctly found nothing.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-05-04'))"
-> no output, no exception raised (valid)
```

`save_report()` also ran its own internal `validate_report()` call during
the save (`validate=True` default), and computed `content_hash` from the
final `top_signals` content. No `revision_history` entry was created (first
save for this date, no prior file existed).

## Files touched

- `data/reports/2026-05-04.json` (new -- built via `src/report_schema.py`'s
  `save_report()`, not hand-written JSON)
- `docs/agent-logs/real-research-2026-05-04.md` (this file, new)

No other file was touched. No commit was made. Git was not otherwise
invoked beyond the read-only `git status` check used to confirm
`data/reports/` was empty before starting.
