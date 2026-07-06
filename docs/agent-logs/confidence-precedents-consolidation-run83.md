# Confidence-discipline precedents consolidation + audit (run 83)

## Scope

Two tasks, both read-mostly:

1. Consolidate every manual confidence-override precedent scattered across
   `docs/agent-logs/real-report-*.md` and `data/reports/*.json` `human_editor_note`
   fields into a single permanent reference: `docs/confidence-discipline-precedents.md`.
2. Audit: spot-check whether reports written *after* each precedent was established are
   internally consistent with it.

No code, schema, `CHANGELOG.md`, or `TODO.md` changes. No `data/reports/*.json` files
were edited — see "On corrections" below for why the two findings below were left as
findings rather than corrected via `save_report()`.

## Methodology

1. Built a run-number → report-date mapping from `docs/CHANGELOG.md` and
   `docs/changelog-entries/run-*.md` (each changelog entry names the exact
   `real-report-*.md` / `data/reports/*.json` it added), since `agent-logs/real-report-*.md`
   files are named by date, not run number. Runs 1-82 mapped, spanning
   2026-07-13 through 2027-12-06.
2. Grepped `docs/agent-logs/*.md` for "confidence", "override", "corroboration",
   "sector", "reprint", "coincidental", "rehash", "independent", "derive_confidence",
   sampling broadly across the full run range rather than reading all ~75 real-report
   logs in full.
3. Grepped `data/reports/*.json` case-insensitively for "confidence" inside
   `human_editor_note` fields — this turned out to be the richer source: several
   precedents are documented only in report JSON, not in any agent-log.
4. For every distinct rule found, recorded: the one-line rule, the first report/run
   that established it, the stated reasoning (quoted), and later reports that applied
   (or should have applied) the same discipline.
5. For the audit pass, checked each precedent against every report dated after its
   establishment date, reading full signal blocks (not just grep hits) for anything
   that looked borderline, and verified the two flagged cases below by reading the
   full JSON myself rather than trusting the audit sub-pass's grep summary alone.

## Precedents documented: 12

Full detail, quotes, and worked examples are in `docs/confidence-discipline-precedents.md`.
One-line index, chronological:

1. A single source spanning multiple sector tags is not independent corroboration
   (pre-run-6, `resale-growth`, 2026-07-13).
2. Same-sector republication doesn't become cross-sector corroboration no matter the
   outlet count — stays capped at medium (run 38, `wales-bonner-hermes-debut`,
   2027-01-25; reinforced through at least run 61).
3. An "unclear" domain-map gap must not be counted as a real distinct sector (run 55,
   `cannes-2027-architectural-red-carpet`, 2027-05-24; reinforced across ~12 later
   signals through 2027-10-04; companion ruling that taxonomy fixes are not
   retroactive, `confidence-recompute-2027-09-06-run72.md`).
4. A downstream reprint/aggregator republishing a primary source is not independent
   second-sector confirmation (run 49, `glamoratti-revival`, 2027-04-12; most fully
   reasoned at run 72, `pfw-ss28-calendar-confirmed`, 2027-09-06).
5. The `independent_criticism` high-reliability exception covers genuine independent
   reporting, not a citation-free rehash (run 78,
   `bogota-waist-tailoring-independent-criticism-synthesis`, 2027-11-08; reapplied run
   81, 2027-11-29).
6. Same-week co-occurrence of two distinct signals is not cross-sector corroboration
   between them (run 80, `opera-gloves-awards-season-editorial`, 2027-11-22).
7. A nominal sector tag can mislabel what's actually the same underlying sector — check
   actual sourcing, not the tag (run 57, `sleepwear-as-outerwear-relaxed-tailoring`,
   2027-06-07).
8. Commercial/service-journalism verticals get an extra discount even within
   "editorial" (run 57, `beaded-jewelry-revival`, 2027-06-07).
9. Signals driven by an external calendar event are held down until tracked past that
   event (run 59, `blokecore-world-cup-jersey-styling`, 2027-06-21).
10. General-news/wire-syndicated pickup is not fashion-trade-press corroboration (run
    64, `lv-waterfall-heatwave-backlash`, 2027-07-26).
11. Attention-economics/casting discourse is a categorization call, not automatically a
    style signal (run 65, `ragebait-runway-casting`, 2027-08-09).
12. Structured/controlled-vocabulary fields are correctable retroactively; editorial
    prose fields are not (run 68, `godet-skirt-backfill-decision-run68.md`, re:
    2026-07-20).

Note on the task's original framing: runs 71/74/78/80 were named as the precedents'
origins, but only run 78 (precedent 5) and run 80 (precedent 6) turned out to be true
first-establishments. The "run 71" and "run 74" examples given in the task are real,
but they're later, minor reapplications of precedents 3 and 2, which were actually
established earlier (runs 55 and 38 respectively). The consolidated doc cites the true
first-establishment dates and lists the later reapplications separately, so this
doesn't affect the precedent count, only which report is cited as the origin.

## Audit findings

Checked every precedent against every report dated after its establishment date.
Precedents 4, 5, and 6 show **no violations** — every later report that hits the
pattern applies the discipline correctly (in the case of precedent 5, run 81
explicitly cites the run 78 precedent by date when reapplying it).

Precedents 2 and 3 turned up two genuine post-precedent inconsistencies:

### Finding 1 — precedent 2 (same-sector cap), `data/reports/2027-05-17.json`

Signal `dior-cruise-2027-lacma-debut`: `confidence: "high"`,
`source_corroboration_count: 6`, `source_sectors: ["editorial"]` (single sector),
`confidence_source: "manual"`.

This is dated 2027-05-17, four months after precedent 2 was established
(2027-01-25) and after it had already been applied identically across 8+ consecutive
windows on the `wales-bonner-hermes-debut` signal. The report's own
`human_editor_note` is explicit that this is a deliberate departure, not an oversight:

> "derive_confidence() would land this at 'medium' — six sources, but all editorial (a
> single source_sector). Overriding to 'high' as an editorial judgment call: this is a
> discrete, photographed, celebrity-attended runway event with matching factual detail
> ... across outlets with no institutional/retail sector expected to weigh in on a
> runway show this quickly. Treating single-sector convergence as a ceiling here would
> penalize a genuinely well-documented event for a sourcing-mix gap that doesn't
> reflect uncertainty about whether it happened."

This is a reasoned argument, not a careless mistake — but it directly contradicts
precedent 2's stated rule ("stays capped at medium ... no matter how many outlets
repeat it") without citing or reconciling with that precedent, even though the
precedent was live and well-established by this date. It effectively invents a new,
undocumented sub-exception ("discrete verifiable-fact event vs. an aesthetic/trend
claim") on the fly. Flagging as a genuine same-era inconsistency for a human to decide
whether (a) this narrower exception is worth formally adding to the precedent doc as
precedent 2a, or (b) the report's confidence should be corrected to `medium`.

### Finding 2 — precedent 3 (unclear-domain gap), `data/reports/2027-07-12.json`

Signal `couture-fw27-debuts-reception`: `confidence: "high"`,
`source_sectors: ["editorial", "unclear"]`, `confidence_source: "manual"`.

The `human_editor_note` names the exact taxonomy gap precedent 3 addresses, but never
offers reasoning for why `high` is still justified despite it:

> "wallpaper.com, nssmag.com, and theimpression.com are established fashion trade
> press by any reasonable read but remain outside DOMAIN_SECTOR_MAP, so a chunk of this
> signal's real corroboration still classifies as 'unclear' sector — the same
> taxonomy-coverage gap noted last window, not yet closed."

The immediate predecessor signal, `couture-fw27-designer-debuts`
(`data/reports/2027-07-05.json`), was held at `medium` one week earlier with the same
`["editorial", "unclear"]` sector mix and the same taxonomy gap explicitly cited as the
reason. The 2027-07-12 report's own `index_note` frames the upgrade as justified by the
claim shifting from "forward-looking anticipation" to "backward-looking, directly
verifiable" reception — but that's a different, unstated rationale from precedent 3's
domain-gap logic, and the note never reconciles the two or explains why the unclear
sector no longer caps the tier the way it did the week before. Flagging as a genuine
inconsistency: either the "verifiable-fact vs. forward-looking claim" distinction is a
legitimate new sub-exception worth formalizing, or the confidence here should have
stayed at `medium` (or the unclear-domain caveat should have been addressed directly,
the way run 72's `confidence-recompute` log did for a similar case).

## On corrections

Both findings involve genuine, non-frivolous editorial reasoning already recorded in
the report's own `human_editor_note` — they are not silent errors, they are reasoned
departures from precedent that were never reconciled against it. Per the task's
constraint to only correct data with very high confidence and to prefer documenting
over correcting when in doubt, I made **no changes to either report file**. Both are
left as audit findings for a human (or a future run explicitly tasked with reconciling
them) to decide: formalize a narrower sub-exception in
`docs/confidence-discipline-precedents.md`, or use `save_report()` to correct the
`confidence` field with a proper `revision_reason`/`corrected_at`.

## Other precedents checked, no violations found

- Precedent 1: no later signal exhibits a single source mapped across multiple sector
  tags being treated as real corroboration.
- Precedent 7 (mislabeled sector), precedent 8 (commercial-vertical discount),
  precedent 9 (calendar-driven event), precedent 10 (wire/general-news pickup),
  precedent 11 (attention-economics categorization), precedent 12 (structured vs.
  prose field correctability): each was established once and I found no later report
  reproducing the same structural pattern without applying the discipline (in most
  cases, because the specific triggering pattern — e.g. a World Cup-driven signal, a
  jewelry-service-vertical cluster — simply didn't recur in a later report to check
  against; noted in the precedent doc as candidates for future audits if/when they
  recur).

## Files touched this run

- Created `docs/confidence-discipline-precedents.md`
- Created `docs/agent-logs/confidence-precedents-consolidation-run83.md` (this file)

No other files were read for writing purposes; no `.env`/secret contents were
accessed or printed; no `data/reports/*.json`, `CHANGELOG.md`, or `TODO.md` files were
modified.
