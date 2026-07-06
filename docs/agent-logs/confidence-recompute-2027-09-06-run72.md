# Confidence recompute review — data/reports/2027-09-06.json (run 72)

## Trigger

Run 70/71's TODO.md flagged: `data/reports/2027-09-06.json`'s `human_editor_note` cites
`fhcm.paris` and `laforma.club` as falling outside `DOMAIN_SECTOR_MAP` (classifying as
`unclear`) as the specific reason the `pfw-ss28-calendar-confirmed` signal was held at
`medium` rather than upgraded. Run 70 subsequently added both domains to
`DOMAIN_SECTOR_MAP`:

- `fhcm.paris` -> `institutional`
- `laforma.club` -> `editorial`

Task: decide whether this taxonomy addition retroactively changes what confidence *should*
have been computed for this signal, per the run 68 precedent that structured/derived-field
corrections (unlike editorial prose) are appropriate when a genuine data-quality issue
exists, while narrative/editorial framing is not retroactively rewritten.

## What the report currently says

Signal `pfw-ss28-calendar-confirmed`:
- `confidence`: `"medium"`, `confidence_source`: `"manual"`
- `source_corroboration_count`: 2
- `source_sectors`: `["unclear", "unclear"]` (stored at write time, before run 70's taxonomy update)
- `source_domains`: `["fhcm.paris", "laforma.club"]`
- `human_editor_note` explicitly reasons: both domains classify `unclear` under the
  then-current `DOMAIN_SECTOR_MAP`, so a literal two-matching-sector read would be
  mistaking a domain-map *gap* for real cross-sector corroboration; medium (not low) was
  chosen because `fhcm.paris` is functionally a first-party institutional source even
  though it wasn't tagged as such yet. The note recommends the exact taxonomy addition
  run 70 later made.

## Mechanical recompute with current taxonomy.py

With today's `DOMAIN_SECTOR_MAP`, `classify_source()` on the two domains now returns
`institutional` and `editorial` respectively — two distinct, named sectors instead of two
`unclear` entries.

Feeding that into `derive_confidence()`'s logic (src/report_schema.py:142-192):
- `corroboration_count` = 2 (unchanged)
- `distinct_sectors` would now be `{"institutional", "editorial"}` — size 2 (was `{"unclear"}`, size 1)
- Rule order: `corroboration_count >= 2 and len(distinct_sectors) >= 2` -> **"high"**

So a mechanical, literal recompute using the corrected domain classifications would now
output `high`, not the report's current `medium`. This is the case for outcome (a).

## Why I did not apply that mechanical result

The mechanical formula treats two *distinct sector labels* as evidence of independent
cross-sector corroboration. That assumption doesn't hold for this specific signal, and the
report's own `evidence` field says why: `laforma.club` is not an independent second
reporter confirming the calendar fact from its own vantage point — it is described in the
report's own evidence text as having "independently republished" FHCM's own calendar
announcement. That is a primary source (the federation publishing its own official
calendar) plus a downstream aggregator/republisher of that same primary announcement, not
two separate sectors each independently corroborating a claim. The `confidence-scoring-
research.md` rationale for the whole formula (cross-sector corroboration as the real
confidence signal, not raw mention count) is specifically trying to reward independent
confirmation — one fact republished by an aggregator with no independent reporting of its
own is closer to a single corroboration than a genuine second one, even though it now
carries a different sector label than the primary source.

This is the same substantive judgment the report's `human_editor_note` already applied to
the "unclear-heavy Demna/Gucci signal in the prior (2027-08-30) report," and it survives
the taxonomy fix: closing the domain-map gap changes the *labels* attached to these two
domains, but it does not change the underlying fact pattern (one primary institutional
announcement, one aggregator reprint of it) that made `medium` the substantively correct
call in the first place. Mechanically deriving `high` here would reward a domain-map
artifact of "two different sector names" over the real question the formula exists to
answer (is there truly independent confirmation?), which the evidence text shows there
isn't.

There is also no other stated reason in the report to hold confidence down (no
contradicting sources, no volatility concern beyond routine logistics) — so if the
aggregator-reprint reasoning were wrong, `high` would indeed be earned. But on reflection
the aggregator-reprint distinction is real and material, and it is exactly the kind of
editorial/substantive judgment call (doc section 18/19: humans decide what clustered
signals mean, not a mechanical rule) that `derive_confidence()` is documented as a
cross-check for, not an auto-authority ("this is a standalone helper... a human editor can
call it to cross-check or override the LLM's confidence assignment" — report_schema.py
docstring, lines 163-167).

## Decision: no retroactive correction applied

`data/reports/2027-09-06.json` is left untouched. `confidence` remains `medium`,
`confidence_source` remains `manual`, `revision_history` remains `[]`.

Reasoning, for the record: the taxonomy fix (fhcm.paris -> institutional, laforma.club ->
editorial) resolves the domain-map *gap* the original human_editor_note flagged, but it
does not resolve — and was never claimed to resolve — the separate substantive question of
whether `laforma.club`'s republication of FHCM's own announcement counts as independent
second-sector corroboration. It does not: it is an aggregator reprint of the same primary
fact, not an independently sourced confirmation. `medium` remains the correct call for the
same reason it was originally chosen (fhcm.paris being functionally first-party
institutional keeps this above `low`, but the single-source-plus-reprint structure keeps it
below `high`). This is a "reviewed, no change needed" outcome per the run 72 task's valid
outcome (b): the taxonomy addition changes what `derive_confidence()` would mechanically
output, but does not change what the substantively correct confidence tier is, so no
correction is warranted.

## Validation run

```
python -m py_compile src/*.py
python src/validate_all_reports.py
python src/check_field_coverage.py
```

All three run clean against the repo with `data/reports/2027-09-06.json` unmodified (see
shell output from this run). No files other than this log were changed.
