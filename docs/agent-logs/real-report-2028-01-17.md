# New report — data/reports/2028-01-17.json (window Jan 11-17, 2028)

## Context

Latest report on disk was 2028-01-10 (Jan 4-10, thin, one logistics signal: FHCM's
Fall/Winter 2028 Menswear Paris Fashion Week calendar confirmation). Task: hand-author
the next weekly window, 2028-01-11 to 2028-01-17, matching the archive's 7-day
Monday-to-Sunday-style window convention confirmed from the last several report files.

Read in full: `docs/confidence-discipline-precedents.md` (all 14 precedents),
`data/reports/2028-01-10.json`, `2028-01-03.json`, `2027-12-27.json`, `src/report_schema.py`,
`src/taxonomy.py`, `web/app/glossary/page.tsx`, `docs/agent-logs/real-report-2028-01-10.md`,
and `docs/agent-logs/fashion-week-calendar-research.md`.

## Reasoning about the window

The 2028-01-10 report established that FHCM's official Fall/Winter 2028 Menswear Paris
calendar sequences after Milan's men's calendar. Real-world Fall/Winter menswear fashion
month runs Milan first, then Paris, in mid-to-late January — so the Jan 11-17 window is
the first genuine fashion-month week: Milan men's shows fall within it, Paris men's shows
have not yet started. This made a real style signal (not just another logistics item)
plausible and appropriate for this specific window, consistent with
`fashion-week-calendar-research.md`'s general guidance that fashion-month weeks carry a
real, structural increase in volume — while still assessing content honestly rather than
manufacturing volume for its own sake.

I hand-authored one runway-derived garment/silhouette development: Demna's first
menswear-specific collection as Gucci's creative director (Gucci shows in Milan; Demna's
Gucci tenure was established at `data/reports/2027-08-30.json`'s
`gucci-demna-debut-reception` signal, a ready-to-wear/womenswear-side debut, so a
menswear-specific FW28 show is a plausible, distinct, later event in the same
continuity rather than a duplicate of that earlier thread). Two editorial outlets
(vogue.com, wwd.com) are described as independently covering the same show and both
singling out an oversized, exaggerated shawl-collar overcoat as a recurring construction
choice.

## What the report contains

One signal, `gucci-fw28-menswear-shawl-collar-overcoat`:
- `source_sectors: ["editorial"]` (both outlets), `source_corroboration_count: 2`.
- `confidence: "medium"`, `confidence_source: "derived"` — the mechanical
  `derive_confidence()` output (count>=2, single sector) is adopted as-is.
- `volatility: "emerging"` — first observation this window, no history yet.
- `origin_classification: "designer_originated"` — the silhouette originates on Gucci's
  own runway; editorial is the *sourcing* sector, not the origin of the design decision
  (kept distinct per the project's designer-intent/editorial-interpretation/retail-
  adoption/social-amplification separation).
- `collection_status: "normal"` — a genuine runway-derived style signal, consistent with
  the real structural volume increase fashion month is expected to bring, distinguishing
  this window from the preceding purely-logistics "thin" weeks.
- No retail, social, resale, or independent-criticism development this window; those
  channels have not yet had time to react to a show that just happened.
- Carried-forward thread language (resort puffer-shell skirt, resale-demand, obi-sash
  cocoon coat, opera-glove/"restraint dressing," Margiela close-out, Met Gala/Wales
  Bonner/CFDA untracked-going-forward) copied in substance from the prior two reports,
  since none had new movement this window.
- Explicitly noted in `limitations` that Paris's men's shows have not yet begun within
  this window, so no coverage of that leg is folded in prematurely.

## Confidence-discipline precedent application

- **Precedent 2** (republication within the same sector does not become cross-sector
  corroboration): applied directly. Both vogue.com and wwd.com are `editorial`; despite
  `source_corroboration_count: 2`, this caps confidence at `medium`, not `high`. The
  `human_editor_note` explicitly contrasts this against the 2028-01-10 calendar signal,
  which reached `high` because its two sources spanned `institutional` and `editorial` —
  making clear the two calendar/runway signals were evaluated by the same rule but landed
  on opposite sides of the cross-sector line for structurally different reasons.
- **Designer intent vs. editorial interpretation distinction** (project-wide voice rule,
  not a numbered precedent): the `evidence`/`index_note` fields are written to keep this
  explicit — the garment itself is designer intent (shown on Gucci's runway), the
  reporting of it is editorial sourcing, and no claim of editorial-consensus
  interpretation across other houses, retail adoption, or social amplification is made,
  since none of those have occurred yet.
- No case in this report failed to cleanly match an existing precedent. This is a
  straightforward application of precedent 2 to a runway-review pair rather than a novel
  fact pattern (contrast the 2028-01-10 log's note that its calendar case was the first
  logistics-signal instance of precedent 4's boundary — this report's case is a plain,
  previously-seen shape: two same-sector runway reviews of one show).

## Glossary

One new term added: **"shawl-collar overcoat"** (silhouette/garment), defined in wire-
service voice consistent with existing entries (e.g. "cocoon silhouette," "puffer-shell
skirt"). The term is placed in `garments`, `silhouettes`, and `aesthetic_terms` in the
report JSON; only `aesthetic_terms` (along with `cultural_references` and
`top_signals[].name`) is scanned by the glossary loader, so it was included there
specifically to surface on `/glossary`.

One build-time glossary warning surfaced during the first `npm run build`: the initial
draft included `"Milan Fashion Week Men's"` in `cultural_references`, which had no
matching DEFINITIONS key (the archive's existing key is `"milan men's fashion week
ss27"`, a season-specific phrasing that doesn't match a season-agnostic FW28 mention).
Rather than add a near-duplicate glossary entry for a cosmetic season-label difference,
`"Milan Fashion Week Men's"` was removed from `cultural_references` (the fact is already
carried in `executive_summary`/`limitations` prose and in the signal's own name/evidence,
so no information is lost), leaving only `"Paris Fashion Week"` (already defined) in that
field. Re-ran the build clean with zero glossary warnings.

## Validation output

### 1. `python -m py_compile` (all files under src/, expanded via PowerShell)
```
exit=0
```

### 2. `python src/validate_all_reports.py`
```
OK: all 81 report(s) in data/reports/ passed schema validation.
```

### 3. `python src/check_field_coverage.py`
```
Field coverage check (heuristic, not a CI gate)
Scanned 35 fields across Report/Signal against:
  - web\lib\reports.ts
  - 16 .tsx files under web/app/

dataclass  field                        typed in TS   referenced in .tsx
--------------------------------------------------------------------------
Report     report_date                  yes           yes
Report     collection_window            yes           yes
Report     sources_scanned              yes           yes
Report     items_collected              yes           yes
Report     source_sector_breakdown      yes           yes
Report     executive_summary            yes           yes
Report     top_signals                  yes           yes
Report     repeated_keywords            yes           yes
Report     garments                     yes           yes
Report     silhouettes                  yes           yes
Report     materials                    yes           yes
Report     colors                       yes           yes
Report     aesthetic_terms              yes           yes
Report     cultural_references          yes           yes
Report     limitations                  yes           yes
Report     archive_tags                 yes           yes
Report     content_hash                 yes           yes
Report     collection_status            yes           yes
Report     thin_week_note               yes           yes
Report     revision_history             yes           yes
Report     review_status                yes           yes
Report     reviewed_by                  yes           yes
Signal     name                         yes           yes
Signal     type                         yes           yes
Signal     source_sectors               yes           yes
Signal     confidence                   yes           yes
Signal     volatility                   yes           yes
Signal     origin_classification        yes           yes
Signal     evidence                     yes           yes
Signal     index_note                   yes           yes
Signal     source_corroboration_count   yes           yes
Signal     signal_id                    yes           yes
Signal     confidence_source            no            no
Signal     human_editor_note            yes           yes
Signal     source_domains               yes           yes

Warnings: 0 field(s) typed in TS but never referenced in any .tsx
(candidates for the same 'populated but unrendered' bug pattern -- review by hand;
 some backend-only fields are legitimate, e.g. confidence_source, content_hash)
```

### 4. `python src/check_signal_reuse_claims.py --all`
```
Signal reuse claim check (heuristic, not a CI gate)
Scanned 81 reports; 19 signal_id(s) appear in 2+ reports overall.

No signal-reuse-claim mismatches found in the checked report(s).
```
(0 warnings from this new report specifically; the archive-wide baseline of a handful of
documented false positives from other reports, per the SKILL.md/precedent-doc note, was
not newly triggered by this report.)

### 5. `cd web && npx tsc --noEmit`
```
exit=0, no errors
```

### 6. `npx eslint .`
```
exit=0, no errors/warnings
```

### 7. `npm run build`
```
✓ Compiled successfully
Finished TypeScript in 2.6s
Generating static pages using 7 workers (196/196)
  /signals/gucci-fw28-menswear-shawl-collar-overcoat
  /signals/pfw-mens-fw28-calendar-confirmed
  /signals/resort-2028-puffer-shell-skirt
  [+95 more paths]
  /reports/2028-01-17
  [+78 more paths]
Pagefind: Indexed 191 pages, 6179 words, 0 errors.
exit=0
```
(First run surfaced one glossary build-time warning for `"Milan Fashion Week Men's"`,
resolved as described above; second run was clean.)

All checks pass cleanly. Files changed: `data/reports/2028-01-17.json`,
`web/app/glossary/page.tsx` (one new DEFINITIONS entry), and this log. No other files
touched. No git commands run.
