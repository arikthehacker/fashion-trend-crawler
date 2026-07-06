# archive_tags filter feasibility (run 85)

## Scope

Run 83's archive UX audit flagged `archive_tags` (real, populated field in
`report_schema.py`'s `Report` dataclass) as unsurfaced on `/archive`, explicitly
deferred as "future scope if the archive grows enough to need it." At 77 reports
now (up from 75 at run 83), this run pulled the actual tag data across every
report in `data/reports/*.json` to make a real (not hypothetical) call on
whether a tag-filter UI is worth building.

## Method

Ran a Python one-liner over all 77 `data/reports/*.json` files, collecting every
`archive_tags` entry with a `Counter`, then broke the results down by frequency
and by rough category (quarter tags, untracked/unresolved signal tags, closeout
tags, thin-week tags). No report/data files were modified.

## Raw findings

- 77 reports, 417 total tag occurrences, **130 distinct tags**, average 5.4
  tags/report, no report has zero tags.
- **88 of 130 distinct tags (68%) occur exactly once** across the whole archive.
  Another 14 occur exactly twice. Only **28 tags occur 3+ times**.
- The top of the frequency list is dominated by long-running-story tracking
  tags tied to one specific ongoing signal thread, not general browsing
  categories, e.g.:
  - `cfda-signals-untracked-pending-new-information` (30)
  - `wales-bonner-untracked-pending-new-information` (21)
  - `met-gala-2027-untracked` (15), `wales-bonner-hermes-debut-untracked` (15),
    `cfda-fashion-fund-winner-untracked` (15), `cfda-fashion-awards-2026-untracked` (15)
  - `margiela-raw-edge-editorial-close-out` (10)
- `thin-week` appears 28 times and is genuinely consistent (used exactly per
  `collection_status: "thin"` reports) — the one tag that behaves like a clean
  controlled-vocabulary facet.
- Quarter tags (`2026-q3`, `2026-q4`, `2027-q1`, `2027-q2`, etc.) appear 13x
  each and are internally well-formed, but only cover **57 of 77 reports
  (74%)** — the format wasn't used consistently from the start (`2026-q2` shows
  up only once, meaning most of that quarter's reports predate the convention
  or used something else).
- The remaining ~88 one-off tags are per-report descriptive/event labels
  (`sheer-layering`, `soft-tailoring`, `1990s-minimalism-revival`,
  `chanel-charvet-acquisition`, `purple-color-trend`,
  `handkerchief-hem-revival`, `dvf-zankov-succession`, etc.) — freeform prose
  fragments the report author coined fresh each week, not drawn from any
  shared vocabulary. Two different weeks describing similar trends do not
  reliably share a tag (e.g. no evidence of a stable `sheer-layering` tag
  recurring across multiple reports about sheer layering — it appears once in
  the sample and isn't in the 3+-occurrence set).

## Judgment

**Not genuinely worth building yet.** A tag-filter chip list is only useful if
most chips return more than one or two results — otherwise it's 100+ mostly-
single-result buttons cluttering the page, which is worse than no filter. The
actual data:

- 68% of tags are one-off — clicking most chips would show exactly 1 report,
  which is not a meaningful browsing affordance (a reader can already reach
  that one report from the flat/year-grouped list or search).
- The tags that DO recur (untracked-signal tracking tags, closeout tags) are
  narrative continuity markers for one specific ongoing story
  (Wales Bonner/Hermès debut, CFDA Fashion Fund, Margiela raw-edge), not
  general browsing categories a reader would reach for (contrast with the
  audit's own hypothetical examples like "paris-fashion-week" or
  "retail-adoption" — no tag like that exists as a stable, reusable category
  in the real data; the closest is `fashion-month-2026`/`nyfw-ss27-schedule`-
  style tags, which are themselves one-off per fashion-week edition, not a
  reusable "fashion-week" bucket).
- The one tag family that IS clean and would make a decent facet
  (`thin-week`, and quarter tags) largely duplicates information already
  addressed by run 83's year-grouping and by `collection_status` in the data
  layer — it doesn't unlock new browsing value the archive page doesn't
  already have a lower-cost fix for.

**Verdict: still premature, and for a concrete, data-backed reason** — not
"tags are freeform in theory" but "68% of the real tags are singletons and the
tags that do recur are per-story continuity markers, not shared browsing
categories."

## What would need to change first

Before a tag filter is worth building:

1. **Separate structured facets from narrative tags in the schema/writing
   convention.** Quarter (`YYYY-qN`) and `collection_status`-derived tags
   (`thin-week`) are already close to a clean controlled vocabulary — if
   `summarize.py`/the report-writing convention enforced them on every report
   (currently only 57/77 have a quarter tag), that alone would be a small,
   genuinely useful facet (filter by quarter, filter by thin-week).
2. **Stop coining one-off descriptive tags as `archive_tags` and use a
   real shared taxonomy for style descriptors,** or accept that those tags are
   inherently narrative prose per-report (which is fine) but exclude them
   from any future filter UI's candidate tag list.
3. Re-run this exact tag pull periodically (it's cheap — a ~15-line Python
   script) once quarter-tag coverage reaches ~100% and/or a genuinely reusable
   descriptive vocabulary (recurring 5+ times across independent stories, not
   just one story's own continuity thread) emerges. That's the concrete
   trigger for revisiting this, not just "archive gets bigger."

## Not done

No code changes. No UI built. `TODO.md`, `CHANGELOG.md`, and `data/reports/*.json`
untouched per instructions. Nothing committed.
