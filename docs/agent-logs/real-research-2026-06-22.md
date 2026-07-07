# Real report: 2026-06-22

## Task

Produce a genuinely-researched report for `collection_window: {"start": "2026-06-16",
"end": "2026-06-22"}`, `report_date: "2026-06-22"` (matches `collection_window.end` per
the run-92 convention in `report_schema.py`). This continues the archive's rebuild from
real historical weeks after the 95-file synthetic-report purge (see
`data/examples/synthetic-reports/README.md`, `data/reports/README.md`). Only
`data/reports/2026-06-22.json` and this log were touched; no other file (including
`taxonomy.py`) was edited, per task scope, and no git action was taken.

## Precedent reading

Read `src/report_schema.py` (Report/Signal dataclasses, `validate_report()`,
`derive_confidence()`'s docstring/formula), `src/taxonomy.py` (controlled vocab +
`DOMAIN_SECTOR_MAP`/`classify_source()`), and `docs/agent-logs/real-report-2028-04-24.md`
for the honest-thin-week discipline. Also read the one real report currently on disk,
`data/reports/2026-05-04.json` (Met Gala / street-style-cluster / denim signals), as the
closest precedent for structure, confidence-override reasoning, and how to log
hand-classified new domains without editing `taxonomy.py`.

## WebSearch queries run and what each returned

1. `fashion trend June 2026 summer style` -- returned Who What Wear / Grazia USA /
   Marie Claire summer-2026 trend roundups (lace-trimmed shorts, crochet skullcaps,
   asymmetric skirts, updated wedges, layered tops). Season-long evergreen content, not
   tied to this specific seven-day window.
2. `vogue.com trend report June 2026` -- no dedicated June-2026 vogue.com trend report
   surfaced; only a Vogue Scandinavia SS26 piece and a YouTube video. Not used as a
   signal.
3. `whowhatwear trend June 2026` -- more Who What Wear seasonal roundups (color trends,
   Y2K revival, asymmetric hem, shopping picks). Same evergreen-content caveat as #1.
4. `resort 2027 collections June 2026` -- confirmed Miami Swim Week (May 29-30) kicked
   off Resort 2027 season, plus Dior's LACMA cruise show (dated separately, see #5) and a
   WWD contemporary-brands resort trend roundup. Not used directly as a top signal
   (dating too diffuse/pre-window), but corroborated the general fashion-calendar
   picture.
5. `Dior Resort 2027 Wilshire Boulevard LACMA show date June 2026` -- corrected my own
   assumption: the Dior Cruise 2027/LACMA show was May 13, 2026, before this window.
   Excluded from top_signals as out-of-window.
6. `"contrast-trim" swimwear Burberry Hunza G summer 2026` -- confirmed the Burberry x
   Hunza G capsule (Burberry check trim on Hunza G's Original Crinkle silhouettes)
   dropped April 27, 2026 -- seven weeks before this window. Referenced only as
   supporting evidence inside the broader aesthetic-cluster signal, explicitly flagged
   as predating the window in that signal's evidence/index_note, not claimed as
   week-specific news.
7. `Y2K revival fashion summer 2026 editorial` -- confirmed ongoing Y2K-revival/
   mermaidcore coverage (Who What Wear, Fashion Week Online, etc.) as season-long
   discourse, folded into the aesthetic-cluster signal rather than logged standalone
   (no single dated event to hang it on).
8. `asymmetric skirts hemlines trend 2026 fashion` -- confirmed asymmetric/godet
   hemlines as an active, multiply-corroborated summer 2026 trend (Who What Wear,
   Grazia USA). Same evergreen-content caveat.
9. `whowhatwear "June 16, 2026" OR "June 17, 2026" OR "June 18, 2026" trend` -- no
   exact-dated match found for those specific days; confirmed the aesthetic-cluster
   items are evergreen roundups rather than event-tied, reinforcing the manual
   confidence-cap decision for that signal.
10. `"week of June 16" 2026 fashion news` -- **the most useful query of this run.**
    Surfaced dated, checkable coverage squarely inside the window: Pitti Uomo 110
    (Florence menswear trade fair) opening June 16, Brunello Cucinelli's traditional
    opening dinner, Simone Rocha's guest-designer menswear debut June 18, and Thom
    Browne's first Milan runway show June 22. These three became the report's
    strongest signals.
11. `Pastels to Plumage: WWD contemporary resort 2027 trends published date` -- confirmed
    WWD's contemporary-brands resort 2027 trend piece is dated roughly two weeks before
    July 7, i.e. approximately the end of this window, but the underlying resort 2027
    season itself opened before this window (Miami Swim Week, late May). Not used as a
    standalone signal -- the resort season's start predates the window and the piece
    itself is a synthesized roundup, not a single dated event.
12. `Pitti Uomo June 2026 opening Brunello Cucinelli Men's Fashion Month` -- confirmed
    exact dates (Pitti Uomo 110, Fortezza da Basso, June 16-19, 2026), the 720+
    exhibiting-brand count, and the "THE POOL" curatorial theme (Chris Vidal Tenomaa /
    Tuomas Laitinen, SSAW Magazine, Hockney-adjacent visual register). Corroborated
    across wwd.com, wallpaper.com, imfirenzedigest.com, and Pitti Immagine's own event
    calendar (pittimmagine.com).
13. `Simone Rocha first menswear show Pitti Uomo Teatro della Pergola June 18 2026` --
    confirmed the show's exact date/venue and design detail (E.M. Forster's "A Room
    With a View" framing; ruffled rugby jerseys, elongated shirting, cut-out tailoring,
    wide Oxford trousers), corroborated across wallpaper.com, wonderlandmagazine.com,
    and rte.ie.
14. `Thom Browne Milan debut runway show June 22 2026` -- confirmed the exact date/venue
    (Palazzo Serbelloni, June 22) and design detail ("A Bug's Life"-referencing set,
    seersucker, Swiss dot tailoring, broadened color palette), corroborated across
    wwd.com, fashionnetwork.com, and theimpression.com.

## Signals included and reasoning

- **`pitti-uomo-110-menswear-month-open`** -- included: tightly dated (June 16-19,
  squarely inside the window), corroborated across 3 editorial outlets plus the event
  organizer's own site, and marks the conventional start of Men's Fashion Month.
  `origin_classification: "unclear"` (institutional trade-fair framework, not
  designer/editorial/retail/social), matching the precedent set for the 2026-05-04
  report's Met Gala signal. `confidence: "high"` matches `derive_confidence()`'s
  formula output (count 4, 2 sectors).
- **`simone-rocha-pitti-uomo-menswear-debut`** -- included: single dated event (June 18),
  3 independent editorial sources with consistent detail. Held at `confidence: "medium"`
  (single sector -- editorial only; no designer-origin or institutional corroboration
  found in this run's searches, so not inflated past what was actually observed).
- **`thom-browne-milan-debut-ss27`** -- included: single dated event (June 22, the
  window's closing day), 3 independent editorial sources with consistent detail. Same
  single-sector `medium` reasoning as the Rocha signal.
- **`summer-2026-aesthetic-cluster-asymmetric-y2k`** -- included, but with an explicit
  manual confidence override: `derive_confidence()` would return `"high"` (3 sources, 2
  sectors -- whowhatwear.com retail, marieclaire.com/graziadaily.co.uk editorial), but
  the underlying content is season-long evergreen trend coverage, not tied to this
  specific week, and the concrete example most repeatedly cited (Burberry x Hunza G)
  dropped seven weeks before the window. Confidence manually capped at `"medium"`
  (`confidence_source: "manual"`) to avoid implying week-specific novelty that the
  evidence doesn't support -- the same override pattern the 2026-05-04 report applied to
  its own street-style-cluster signal.

### Considered and excluded

- Dior's Cruise/Resort 2027 LACMA show -- real and well-covered, but dated May 13, 2026,
  three-plus weeks before the window opens. Excluded as out-of-window, not folded into
  a signal.
- Burberry x Hunza G swimwear capsule as its own standalone signal -- real, but the
  capsule itself dropped April 27, 2026, seven weeks before the window; referenced only
  as supporting evidence inside the broader aesthetic-cluster signal with that dating
  caveat stated explicitly, not presented as a dated event of this window.
- Miami Swim Week / broader Resort 2027 season opening -- real, but started in late May
  (before the window); the specific WWD "Pastels to Plumage" roundup is dated near the
  window's end but is itself a synthesized trend piece about an already-opened season,
  not a single dated event inside the window. Excluded rather than stretched into a
  signal.
- A specific vogue.com June-2026 trend report -- searched for directly, did not surface;
  not fabricated to satisfy an outlet-diversity wish.
- Independent-criticism and designer-origin direct sources (e.g. a Substack critic
  commenting on Pitti Uomo/Rocha/Browne, or simonerocha.com/thombrowne.com posting about
  their own shows) -- searched for but did not surface in this run's queries; their
  absence from `source_sectors` is stated honestly in each signal's index_note/evidence
  rather than assumed or invented.

## Source-sector classification reasoning for newly-encountered domains

None of these three domains are yet in `taxonomy.py`'s `DOMAIN_SECTOR_MAP`.
`taxonomy.py` was **not edited** (out of scope for this task); classifications below are
recorded here for a future run to add to the map if it chooses to.

- **`pittimmagine.com`** -- classified `institutional`. This is Pitti Immagine's own
  domain (the event-calendar page for Pitti Uomo, confirmed via search-result title/URL
  matching the official fair). Pitti Immagine is the organizing body for the Pitti Uomo
  trade fair, playing the identical structural role `cameramoda.it` (Milan Fashion
  Week's organizing body) and `fhcm.paris` (Paris's) already play in the existing map --
  an official governing/organizing body, not a designer house, editorial outlet, or
  retailer.
- **`wonderlandmagazine.com`** -- classified `editorial`. Wonderland is a UK-based,
  staffed fashion/music/culture magazine (confirmed via its coverage of the Rocha show
  carrying a dated byline/article format consistent with a staffed masthead, the same
  bar already applied to comparable UK titles like `stylist.co.uk`/`bricksmagazine.co.uk`
  in the existing map).
- **`rte.ie`** -- classified `editorial`. RTE (Raidio Teilifis Eireann) is Ireland's
  national public-service broadcaster; this piece is general/lifestyle news coverage of
  a fashion event, matching the same geographic-diversity general-press pattern already
  applied to `euronews.com`/`wionews.com`/`asiae.co.kr` (staffed national/international
  news organizations covering fashion as part of broader beat coverage, not a dedicated
  fashion trade outlet, but a legitimate staffed newsroom nonetheless).

## Confidence discipline

Each signal's `confidence` was cross-checked against `derive_confidence()` by running
the actual function against the built dict before saving (see build script output, all
four rows matched or explicitly documented why they diverge). Three of four signals
match the derived value exactly (`confidence_source: "derived"`). The fourth
(`summer-2026-aesthetic-cluster-asymmetric-y2k`) was manually held one tier below its
derived value (`confidence_source: "manual"`), with the override reasoning recorded
directly in that signal's `index_note` -- the corroboration-count/sector-diversity
formula rewards cross-sector agreement, but does not by itself detect that the
underlying content is season-long evergreen material rather than week-specific news,
which is a judgment call this report makes explicitly rather than silently.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-06-22'))"
```
-> no output, no exception raised (valid).

Also ran the build script directly and printed a per-signal `derive_confidence()`
cross-check before saving (see reasoning above); all four rows were as expected.

`web/` build/lint/tsc were **not** re-run as part of this task (out of scope --
task instructions scoped this run to the two named files only).

## Files touched

- `data/reports/2026-06-22.json` (new)
- `docs/agent-logs/real-research-2026-06-22.md` (this file, new)

No other file was touched. `taxonomy.py` was deliberately left unedited despite three
newly-encountered domains being classified in reasoning above -- out of scope for this
task. No git action (commit, stage, etc.) was taken.
