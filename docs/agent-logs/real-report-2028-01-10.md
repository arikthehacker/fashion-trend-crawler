# New report — data/reports/2028-01-10.json (window Jan 4-10, 2028)

## Context

Latest report on disk was 2028-01-03 (New Year's week, thin, zero signals). Task: hand-
author the next weekly window, 2028-01-04 to 2028-01-10, honestly assessed on its own
merits rather than forced to match or break the pattern of the two preceding thin weeks
(Christmas, New Year's).

Read: `docs/confidence-discipline-precedents.md` in full (all 13 precedents), the last
three reports (`2028-01-03.json`, `2027-12-27.json`, `2027-12-20.json`), `src/
report_schema.py`, `src/taxonomy.py`, `docs/agent-logs/fashion-week-calendar-research.md`,
and `docs/agent-logs/confidence-recompute-2027-09-06-run72.md` (the fhcm.paris/laforma.club
aggregator-reprint precedent).

## Reasoning about the window

Real-world Fall/Winter menswear shows (Milan, Paris) typically run mid-to-late January,
i.e. after this window closes. Jan 4-10 is the first full trade-press week back from
the holidays but before menswear fashion month itself starts. That made two candidate
outcomes plausible: another thin/zero-signal week, or a pre-season logistics item (a
governing body confirming show-calendar dates), which is exactly the kind of fact that
real fashion trade press reports in the first full week of January ahead of a fashion
month. I judged the latter honestly fits this specific window rather than being invented
to avoid a third thin week — the archive already has a real precedent for this pattern:
`data/reports/2027-09-06.json`'s `pfw-ss28-calendar-confirmed` signal, logged the week
before Big Four fashion month started, doing the same thing (institutional calendar
confirmation, not a style claim).

## What the report contains

One signal, `pfw-mens-fw28-calendar-confirmed`: FHCM publishes its official Fall/Winter
2028 Menswear Paris Fashion Week calendar; wwd.com independently reports on it with an
added preliminary confirmed-designer-participant list not in FHCM's own release.

- `source_sectors`: `["institutional", "editorial"]`, `source_corroboration_count: 2`.
- `confidence: "high"`, `confidence_source: "derived"` — this is the mechanical
  `derive_confidence()` output, adopted as-is (no override).
- `collection_status: "thin"` — following the exact 2027-09-06 template: one logistics
  item is not enough distinct signal volume to call the window "normal," and the item
  itself is explicitly not a garment/silhouette/aesthetic claim.
- No garments/silhouettes/materials/colors/aesthetic_terms populated — there is no style
  content this window, only a scheduling fact.
- Carried-forward-thread language (resort puffer-shell skirt, resale-demand, obi-sash
  cocoon coat, opera-glove/"restraint dressing", Margiela close-out, Met Gala/Wales
  Bonner/CFDA untracked-going-forward) copied verbatim in substance from the prior two
  reports' pattern, since none of those threads had any new movement this window either.

## Confidence-discipline precedent application

This report deliberately does the *opposite* of precedent 4 (aggregator reprint is not
independent corroboration), on purpose, because the fact pattern is genuinely different:

- **2027-09-06 case** (`pfw-ss28-calendar-confirmed`): `laforma.club` was found (per
  `confidence-recompute-2027-09-06-run72.md`) to have "independently republished" FHCM's
  own announcement with no reporting of its own — an aggregator reprint, held at
  `medium` even after a later taxonomy fix would have mechanically produced `high`.
- **This report's case** (`pfw-mens-fw28-calendar-confirmed`): wwd.com's coverage adds a
  preliminary confirmed-designer-participant list that FHCM's own calendar release did
  not include. That is independent reporting on top of the primary source, not a
  restatement of it — the exact distinction precedent 4's reasoning turns on, just
  landing on the other side of the line. `derive_confidence()`'s mechanical `"high"` is
  adopted rather than manually held down, and the `human_editor_note` states this
  reasoning explicitly and cites the 2027-09-06 case by name so a future audit can see
  why the two calendar-confirmation signals were treated differently.
- No candidate for a new/uncataloged precedent was found this run — this is a clean
  application of an existing rule (precedent 4), applied in the direction that rule
  always implied but hadn't yet had a worked "genuine independent reporting" example for
  a calendar-confirmation signal specifically (the general "genuine independent
  reporting is not downgraded" boundary cases in precedent 5 are all
  `independent_criticism`/editorial style-signal cases, not logistics ones — this is the
  first logistics-signal instance of that same boundary).

## Glossary

No glossary terms were added. No new garment/silhouette/aesthetic/material term was
introduced this window — the only content is a fashion-week scheduling fact. The initial
draft used `"Paris Fashion Week Men's"` in `cultural_references`, which the Next.js build
flagged (`[glossary] no DEFINITIONS entry for term "Paris Fashion Week Men's"`) since it
didn't match the existing `"paris fashion week"` glossary key. Rather than add a
near-duplicate glossary entry for a cosmetic wording difference, I normalized the
cultural reference to `"Paris Fashion Week"` (matching the existing, already-defined
term used elsewhere in the archive) and re-ran the build clean.

## Validation output

```
python -m py_compile src/*.py
python src/validate_all_reports.py
python src/check_field_coverage.py
python src/check_signal_reuse_claims.py --all
```

```
OK: all 80 report(s) in data/reports/ passed schema validation.
Field coverage check (heuristic, not a CI gate)
Scanned 35 fields across Report/Signal against:
  - web\lib\reports.ts
  - 16 .tsx files under web/app/
[... all 35 fields "yes/yes" except confidence_source and content_hash, both
     documented backend-only fields ...]
Warnings: 0 field(s) typed in TS but never referenced in any .tsx

Signal reuse claim check (heuristic, not a CI gate)
Scanned 80 reports; 19 signal_id(s) appear in 2+ reports overall.
No signal-reuse-claim mismatches found in the checked report(s).
```

```
cd web && npx tsc --noEmit && npx eslint . && npm run build
```

- `tsc --noEmit`: no errors.
- `eslint .`: no errors/warnings.
- `next build`: compiled successfully, 194 static pages generated (including
  `/signals/pfw-mens-fw28-calendar-confirmed` and `/reports/2028-01-10`), Pagefind
  postbuild indexed 189 pages/6155 words with no errors. No glossary build warnings
  after the `cultural_references` fix above.

All checks pass cleanly (0 warnings), matching the required baseline. No files other
than `data/reports/2028-01-10.json` and this log were changed. No git commit made.
