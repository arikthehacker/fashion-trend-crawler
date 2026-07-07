# Real research: 2026-05-11

## Task

Produce the first genuine (non-fabricated) report for a real past week,
`collection_window: {"start": "2026-05-05", "end": "2026-05-11"}`,
`report_date: "2026-05-11"` (matches `collection_window.end` per the run-92
convention). This is one of several parallel agents rebuilding the archive
from real research after the purge of 95 synthetic/placeholder reports (see
`data/examples/synthetic-reports/README.md` and `data/reports/README.md`).

Scope followed exactly as instructed: only `data/reports/2026-05-11.json` and
this log file were touched. No other file edited, nothing committed, no git
commands run beyond none (none were run).

## WebSearch queries run, and what each returned

1. **`Met Gala 2026 theme`** — confirmed the 2026 Met Gala's dress code was
   "Fashion Is Art," tied to the Costume Institute's spring exhibition
   "Costume Art." Gala took place Monday, May 4, 2026 (one day before this
   window's May 5 start). Sources: metmuseum.org, rollingstone.com,
   itscritical.substack.com (not used — a prediction/speculation piece, not
   post-event coverage).
2. **`Met Gala 2026 red carpet fashion May 4`** — NPR and Washington Post
   recap pieces confirming co-hosts (Beyoncé, Nicole Kidman, Venus Williams)
   and specific looks (Madonna/Saint Laurent referencing a Leonora Carrington
   painting, Rihanna/Maison Margiela, Bad Bunny/Zara, Katy Perry/Stella
   McCartney).
3. **`vogue.com fashion trend May 2026`** — zero results. No Vogue-specific
   trend coverage for this window was retrievable via search. No signal
   logged from this query.
4. **`fashion news May 5 2026`** — returned mostly generic/listicle content
   (Who What Wear shopping picks, a law-firm luxury-news aggregator, a
   sustainable-fashion roundup) with only incidental, not window-specific,
   fashion-trend substance (Victoria's Secret x Agua Bendita capsule,
   Givenchy Voyou bucket bag, Christopher Kane joining Mulberry, Kering Q1
   results). None of these had enough independent, dated corroboration to
   justify a `top_signals` entry, so none was logged — noted in
   `limitations` instead as a category of searches that came back thin.
5. **`"Costume Art" exhibition Met opens May 10 2026 review`** — the
   strongest single result set. Confirmed via metmuseum.org's own press
   materials plus four independent editorial reviews (Wallpaper*, The Art
   Newspaper — dated May 11, 2026, inside the window — W Magazine, Time Out)
   that the Costume Institute's new ~12,000 sq ft above-ground gallery space
   and its inaugural exhibition "Costume Art" opened to the public May 10,
   2026, running through January 10, 2027.
6. **`Met Gala 2026 fashion trend analysis "art on the body" runway`** —
   Forbes' trend-report piece (dated May 5, 2026, inside the window) and
   several lower-quality blogs (trillmag.com, ourculturemag.com,
   kalkifashion.com's blog) converged on describing a "body as canvas" /
   sculptural theme: hand-painted garments (Emma Chamberlain via Mugler's
   Miguel Castro Freitas), beadwork mimicking paint (Jeremy Pope), sculpted
   bodices/breastplates, modular/magnetic jewelry. Only Forbes and Rolling
   Stone were used as corroborating sources for the logged signal; the
   lower-tier blogs (trillmag.com, ourculturemag.com, kalkifashion.com,
   suddenchic.com) were read for context but not cited as `source_domains`
   — none has an established editorial masthead comparable to the outlets
   already in `taxonomy.py`'s `DOMAIN_SECTOR_MAP`, and none was needed once
   NPR/Washington Post/Forbes/Rolling Stone already corroborated the same
   observation.
7. **`Met Gala 2026 best dressed fashion week aftermath`** — Today.com,
   Washington Post, and E! Online best-dressed roundups; used to
   cross-confirm the same "art on the body" framing (Today.com/E! not cited
   as `source_domains` in the final signal since Washington Post and Forbes
   already covered the same ground with more analytical framing).
8. **`resort 2027 collections preview May 2026`** — returned real coverage,
   but nothing dated inside the window itself: WWD's Resort 2027 runway
   pages, a Stella McCartney Resort 2027 anniversary collection, and
   confirmation that Dior's Cruise 2027 "Wilshire Boulevard" show (Jonathan
   Anderson's first for the house) was in the pipeline. No specific
   in-window date found from this query alone (see query 9).
9. **`Dior Resort 2027 Wilshire Boulevard LACMA Jonathan Anderson show date`**
   — confirmed via multiple outlets (hauteliving.com, ouispeakfashion.com,
   fashionnetwork.com, theimpression.com) that the show was dated **May 13,
   2026** — two days after this window closes (May 11). Excluded from
   `top_signals` on that basis; noted in `limitations` as expected to
   surface in the next window.
10. **`"May 2026" fashion week runway show designer new collection`** —
    returned only generic year-ahead "2026 runway trends" listicle content
    (fashiontimes.com) and a Miami/LA resort/swimwear trade-show expansion
    dated May 29-31, 2026 (outside this window). No in-window runway
    signal found; not logged.

## Signals included, and why

**`met-gala-2026-fashion-is-art-body-as-canvas`** (medium confidence, flash
volatility, editorial_amplified). Included because it is the one
well-corroborated, dated, checkable observation from this window: four
independent editorial outlets (npr.org, washingtonpost.com, forbes.com,
rollingstone.com) converged on describing the same body-as-canvas/sculptural
aesthetic at a single, confirmed real event. Held at `medium` because all
four sources resolve to the same sector (`editorial`) — per
`docs/confidence-discipline-precedents.md` precedent 2, raw outlet count
within one sector does not cross into `high`. `derive_confidence()` was run
against the assigned value and returned `medium` independently — no manual
override was needed (see `human_editor_note` on the signal itself for the
full reasoning, including why precedent 9's calendar-driven discount was
considered and not separately applied on top of precedent 2).

**`met-costume-institute-costume-art-gallery-opening`** (high confidence,
long_tail volatility, unclear origin). Included because it is genuinely
cross-sector corroborated: metmuseum.org's own press release (institutional,
first-party) plus four independent editorial reviews (wallpaper.com,
theartnewspaper.com, wmagazine.com, timeout.com) that critique the show
rather than reprint the museum's release. `derive_confidence()` independently
returned `high`, matching the assigned value. `origin_classification` was
set to `unclear` rather than forced into an ill-fitting existing value — see
the signal's own `human_editor_note` for why `archive_revival` was
considered and rejected (that value is calibrated for a design element
returning to fashion currency, not an institution restructuring its own
exhibition footprint).

## Signals/leads considered and excluded

- **General May 2026 fashion-trend/runway content** (query 4, 10): thin,
  generic, not window-specific enough to log; would have required
  manufacturing specificity that the search results didn't actually support.
- **Dior Cruise 2027 LACMA show**: real, well-corroborated, but dated May 13,
  2026 — two days outside this window. Excluded on a strict date basis
  rather than stretched to fit, consistent with how the Met Gala's May 4
  date was flagged (not silently included) even though its analytical
  coverage does fall inside the window.
- **Vogue.com specific coverage** (query 3): zero results retrievable via
  search; not logged, not assumed to exist.
- **Lower-tier blogs** (trillmag.com, ourculturemag.com, kalkifashion.com's
  blog, suddenchic.com): read for context on the body-as-canvas framing but
  not used as `source_domains` — no established editorial masthead
  comparable to existing `DOMAIN_SECTOR_MAP` entries, and not needed once
  four stronger outlets already corroborated the same observation.
- **Individual outfit color callouts** (gunmetal Margiela, black Saint
  Laurent, white Stella McCartney): real per-look details, but no
  cross-look color convergence was found strong enough to log as an
  aggregate `colors` trend entry, so `colors` was left empty rather than
  inflating a single-look detail into a claimed color trend.

## Source-sector classification reasoning (domains not yet in `taxonomy.py`)

`taxonomy.py`'s `DOMAIN_SECTOR_MAP` was not edited (out of scope for this
task — only `data/reports/2026-05-11.json` and this log were to be touched).
The following domains, cited in the report's `source_domains` fields, are
not yet in that map; each was classified for this report's own
`source_sectors` field by the same reasoning already applied to comparable
mapped domains, documented here for whoever next expands the map:

- **npr.org** — National Public Radio, a staffed nonprofit news
  organization; its "Picture Show" desk ran a dedicated red-carpet
  photo/recap piece. Same general-editorial-press pattern as `nytimes.com`
  (already `editorial`). Classified `editorial`.
- **washingtonpost.com** — staffed daily newspaper with a dedicated Style
  section; ran both a live-updates recap and a separate best-dressed piece.
  Same pattern as `nytimes.com`. Classified `editorial`.
- **forbes.com** — staffed contributor-network business/culture
  publication; the cited piece is a named contributor's fashion-report
  analysis. Same pattern as `hollywoodreporter.com`/`robbreport.com`
  (already `editorial`, both Penske/contributor-adjacent models).
  Classified `editorial`.
- **rollingstone.com** — staffed culture/entertainment magazine (Penske
  Media, same publisher family as `hollywoodreporter.com`/`robbreport.com`)
  with a "best and most outrageous looks" fashion feature. Classified
  `editorial`.
- **theartnewspaper.com** — The Art Newspaper, a staffed international
  visual-arts trade/editorial publication (comparable in kind to
  `artnews.com`, already `editorial`); its May 11, 2026 piece is a
  named-author critical review of the Costume Institute's new galleries.
  Classified `editorial`.
- **timeout.com** — Time Out, a staffed city-guide/culture magazine
  (comparable to `wallpaper.com`, already `editorial`) with named-author
  arts/culture reviews. Classified `editorial`.

No domain in this list was ambiguous enough to warrant `unclear` — all are
recognizable, long-running staffed publications with named authors/editorial
processes, the same bar already applied to dozens of comparable domains in
`DOMAIN_SECTOR_MAP`.

## Confidence discipline

Both signals' `confidence` values were checked against `derive_confidence()`
and matched exactly — no manual override was required for either. Precedent
2 (single-sector volume cap) and precedent 7 (verify sector tags reflect
actual sourcing, not just the label) were both explicitly considered and
cited in the signals' own `human_editor_note` fields. Precedent 17
(absence-of-coverage signals) was considered for the thin general-search
results (queries 3, 4, 10) but does not apply here in the way it did for
`docs/agent-logs/real-report-2028-04-24.md` — this report is not a fully
thin week (`collection_status: "normal"`, two real signals were found), so
there is no dedicated `factual_question`/coverage-gap signal_id for an
absence claim to attach to; the thin general-search results are instead
documented plainly in `limitations` as searches that came back generic
rather than logged as their own signal.

## Verification run

```
cd src && python -c "from report_schema import load_report, validate_report; validate_report(load_report('2026-05-11'))"
```

Passed silently (no output, no exception) — report validates. Confidence
tiers were also cross-checked against `derive_confidence()` directly inside
the build script before saving (see build script output: both signals'
assigned confidence matched the derived value exactly).

## Files touched

- `data/reports/2026-05-11.json` (new, via `save_report()` — not
  hand-written)
- `docs/agent-logs/real-research-2026-05-11.md` (this file, new)

No other file was touched. No commit was made. No git command was run.
