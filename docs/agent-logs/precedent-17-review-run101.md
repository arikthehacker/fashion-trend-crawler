# Precedent-17 review — run 101

Branch: `ari3lla-index-loop-improvements`. Task: independently re-verify
`periodic-audit-run100.md`'s flagged mismatch on `data/reports/2027-06-14.json`'s
`met-gala-2027-coverage-gap` signal, then decide whether `low` is a legitimate
undocumented call (formalize as precedent 17) or a mistake (correct to `medium` via
`save_report()`). No report file was edited as a result of this review — see
disposition below.

## 1. Independent re-derivation (did not trust run 100's write-up)

Read `data/reports/2027-06-14.json` directly. The `met-gala-2027-coverage-gap` signal:

```
"source_sectors": ["editorial"],
"confidence": "low",
"volatility": "declining",
"origin_classification": "editorial_amplified",
"source_corroboration_count": 1,
"confidence_source": "manual",
```

Read `derive_confidence()` in `src/report_schema.py` (lines 142-192):
- `existing_confidence != "archival"`, so not passed through unchanged.
- `distinct_sectors = {"editorial"}`, count = 1 → fails the `high` test
  (`count >= 2 and len(distinct_sectors) >= 2`).
- `medium` test: `count >= 2` from one sector (no, count is 1) **OR**
  `count == 1` from a sector in `HIGH_RELIABILITY_SECTORS`. `editorial` is in
  `HIGH_RELIABILITY_SECTORS` (confirmed in both `report_schema.py` and
  `docs/confidence-discipline-precedents.md`'s own restatement of the formula).
  This branch is true.
- Mechanical result: **`medium`**.
- Assigned result: **`low`**.

**Run 100's finding is accurate.** The mismatch is real, and it is a live,
non-placeholder report (unlike the separate `2026-05-07.json` placeholder finding in
the same audit, which is a different, already-dispositioned item).

Also independently confirmed the companion facts run 100 cited:
- Same signal_id's first occurrence, `data/reports/2027-05-31.json`, has the
  identical shape: `source_corroboration_count: 1`, `source_sectors: ["editorial"]`,
  `confidence: "low"`, `confidence_source: "manual"`. So the `low` call was made
  **twice, independently, across two different report windows/runs (56 and 58)**,
  not once.
- Neither report's `human_editor_note`/`evidence`/`index_note` states a reason for
  the confidence *value* specifically. Both notes are entirely about the
  signal_id-reuse/consolidation history (a prior draft minting a new archive_tag
  instead of reusing the signal_id) — a real and separate correction, but it says
  nothing about why the tier is `low` rather than the mechanically-implied `medium`.

## 2. Full evidence/note prose, read for context

`2027-06-14.json`:
> `evidence`: "Targeted search across seven consecutive weekly collection windows
> (2027-05-03 through 2027-06-14) found zero reachable coverage of a Met Gala 2027
> theme, co-chairs, or red-carpet under that name, despite the event historically
> generating same-day saturation coverage."
>
> `index_note`: "Reuses the signal_id introduced on 2027-05-31 so cross-report
> history actually accumulates for this index's dormancy tooling... The event's date
> is not in question... Seven consecutive windows of zero coverage for an event that
> normally generates same-day reporting remains a genuine, unresolved coverage
> absence, not a calendar mismatch."

`2027-05-31.json`'s `evidence`/`index_note` are the same pattern one window earlier
(five windows instead of seven), plus a note explaining the signal_id was
introduced then for the first time so `get_signal_status_history()`/
`is_prolonged_silence()` can track it going forward.

Nothing in either report's prose engages with confidence at all. The signal's
`type` field is `"factual_question"` (not a garment/aesthetic observation type),
and `source_sectors: ["editorial"]` on both occurrences records that the *searches*
run to look for coverage were of editorial-type sources, not that an editorial
source reported anything.

## 3. Cross-check against all 16 existing precedents in `docs/confidence-discipline-precedents.md`

Read the full document (confirmed 16 numbered precedents before this review, per
run 100's own count). None of the 16 states a rule for an absence-of-coverage /
"factual_question" signal specifically:

- Precedents 1, 2, 4, 6, 7 all concern whether apparent *corroboration* (multiple
  sectors/outlets) is real — not applicable, this signal has `count == 1` and one
  sector; there's no corroboration-count inflation to check.
- Precedent 3 (unclear domain-map gaps) — not applicable; `source_domains: []`
  here, no domain-resolution question.
- Precedent 5 (independent_criticism exception limited to genuine independent
  reporting) — a different sector and a different failure mode (citation-free
  rehash), not this signal's shape.
- Precedent 8 (commercial-vertical discount), 9 (calendar-driven durability), 10
  (wire-syndication discount), 11 (categorization vs. confidence) — each addresses
  a specific sourcing-quality discount on a *presence* claim; none addresses the
  case where the claim itself is an absence.
- Precedent 12 (structured fields correctable, prose fields never retroactively
  rewritten) — directly relevant to *how* to handle the missing documentation (see
  disposition below), but does not itself resolve whether `low` is correct.
- Precedent 13 (resale sourcing is supply-side, not demand-side) and 14
  (forecast/prediction is not evidence of a present signal) are the closest
  analogues in *shape*: both identify that a source category can satisfy the
  mechanical formula's letter while failing to supply the kind of evidence the
  formula was designed to score, and both were resolved by holding down rather than
  inventing an upward override. Neither, however, covers absence-of-coverage
  specifically — precedent 14 is about a forecast asserting something about the
  future; this signal asserts something about the present (a search's completeness),
  which is a different failure mode again.
- Precedent 15 (editorial-synthesis signals are a distinct category with a stricter
  gate) is the closest structural precedent: it establishes that a signal whose
  evidentiary content is not an observation but a claim *about the evidence itself*
  (a relationship between prior signals) is a genuinely different epistemic object
  and gets different treatment than an ordinary observation, run through the normal
  formula only after clearing an extra gate. A coverage-gap signal is the same kind
  of move one level further: its evidentiary content is not an observation of
  anything happening, but a claim about the *absence* of observations — an even
  more different epistemic object than a synthesis-of-existing-signals claim.
- Precedent 16 (single-outlet plural language) — a prose-discipline rule, orthogonal
  to the confidence-tier question here (also independently confirmed both reports
  correctly avoid plural sourcing language: "targeted search... found zero
  reachable coverage," never "sources report no coverage").

**Conclusion: no existing precedent covers this case.** This is a genuine gap, not
a case of failing to look hard enough for the applicable rule.

## 4. Is `low` the correct call, and why (the core judgment)

Concluded **yes, `low` is correct, for a reason not yet written down anywhere**,
and formalized it as precedent 17 in `docs/confidence-discipline-precedents.md`.

Reasoning:

1. **The `HIGH_RELIABILITY_SECTORS` single-source exception is calibrated for
   affirmative claims, not negative ones.** The exception exists because one
   `editorial`/`designer_origin`/`institutional`/`independent_criticism` source
   asserting a fact is more trustworthy than one social-media post asserting the
   same fact — it's a statement about the reliability of a sector's *editorial
   process* when it reports something. A coverage-gap signal has no such report to
   trust: nothing was found, so there is no assertion whose reliability the sector
   tag is vouching for. Running "which sector(s) did we search" through a formula
   designed to score "how many independent, reliable sources reported this" is a
   category error — the `source_sectors: ["editorial"]` field here is describing
   the search, not a source being corroborated.
2. **The real confidence driver for an absence claim is search
   thoroughness/completeness (how many windows, how broad the search, whether a
   crawler/reach failure has been ruled out), which the mechanical formula does not
   model at all.** `source_corroboration_count` and `source_sectors` are the wrong
   inputs for this signal type entirely — they happen to be populated because the
   schema requires them, but they don't carry the information that would actually
   justify raising or lowering confidence in an absence claim. Defaulting to `low`
   until some other explicit signal of search rigor is documented is the
   conservative, correct default.
3. **This is not resolved by any existing precedent's letter**, but is closely
   analogous in *spirit* to precedent 14 (a forecast is not evidence of a present
   signal — a different kind of claim than the formula's inputs assume) and
   precedent 15 (a claim about the evidence itself is a distinct epistemic category
   gated more strictly than an ordinary observation) — the same "this satisfies the
   formula's letter but not what the formula was built to measure" shape, applied
   to a third variant (absence rather than forecast or meta-claim).
4. **Consistency across two independent occurrences (run 56, run 58) is evidence
   this was a real, stable judgment**, not a one-off error — the same signal_id was
   held at `low` twice, a window apart, by (as far as the record shows) separate
   report-writing passes, without documented coordination between them beyond
   reusing the signal_id itself. This is the same "independently reached twice"
   pattern that justified formalizing precedent 14 from two reports a year apart.

## 5. Disposition: formalize precedent 17; do not edit either report

Added precedent 17 to `docs/confidence-discipline-precedents.md` (appended after
precedent 16, matching the document's actual append-order convention — confirmed by
inspection that existing precedents are NOT in strict first-established
chronological order, e.g. precedent 4's first-establishment run (49) predates
precedent 3's (55) despite precedent 3 being listed first; the document orders by
formalization/append order, not raw historical date, so precedent 17 is correctly
placed at the end regardless of its earlier 2027-05-31 first-establishment date).

**`data/reports/2027-05-31.json` and `data/reports/2027-06-14.json` were
deliberately left unedited** — no `human_editor_note` rewrite, no
`revision_history` entry, no `save_report()` call. Reasoning: per precedent 12
(structured/controlled-vocabulary fields are retroactively correctable;
`human_editor_note`/`evidence`/prose fields are never retroactively rewritten to
supply reasoning that was not contemporaneously recorded), inventing prose now to
explain a judgment that was actually made without written justification at the time
would misrepresent the historical record the same way precedent 12 declined to
"fix" the two verbatim-duplicate `human_editor_note`s in `2026-07-13.json`/
`2026-11-09.json`. The value itself (`low`) is correct and does not need
correcting; only the documentation was missing, and the correct fix for missing
documentation is capturing the durable rule going forward (this precedent), not
retrofitting the old files to look like the reasoning was written down originally.
`confidence_source: "manual"` on both signals remains accurate as-is (a deliberate
override did occur) and needed no change.

This is explicitly **not** the "leave undecided for a human" case — the review
reached a confident, well-supported conclusion (low is correct, for a reason now
written down) rather than punting. It differs from run 100's own disposition
(documented-but-uncorrected) only in that the reasoning has now been fully worked
through and captured as a citable precedent rather than left as an open flag.

## 6. Verification

```
$ python -m py_compile src/*.py
(no output — success)
$ python src/validate_all_reports.py
OK: all 94 report(s) in data/reports/ passed schema validation.
```

No report files were modified by this review, so the validator's clean pass
confirms no regression was introduced, not that a fix was applied — expected, since
the disposition was "correct value, document going forward" rather than "edit the
data."

## Summary

- Independently re-confirmed run 100's finding is accurate: `met-gala-2027-coverage-gap`
  in `2027-06-14.json` (and identically in `2027-05-31.json`, the signal's first
  occurrence) mechanically computes `medium` (`count == 1`, `editorial` is a
  `HIGH_RELIABILITY_SECTORS` member) but is assigned `low`, with no
  confidence-specific reasoning in either report's prose.
- Checked all 16 existing precedents in `docs/confidence-discipline-precedents.md`
  in full; none covers an absence-of-coverage / `factual_question` signal.
- Concluded `low` is the correct call for a genuine, previously-uncaptured reason:
  the `HIGH_RELIABILITY_SECTORS` single-source exception is calibrated for
  affirmative claims (trusting one reliable sector's assertion), not for the
  completeness of a negative search result, which the formula's inputs
  (`source_corroboration_count`, `source_sectors`) do not actually measure for this
  signal type.
- Formalized this as **precedent 17** in
  `docs/confidence-discipline-precedents.md`, following the same
  rule/first-establishment/reasoning/worked-example structure as precedents 1-16.
- Deliberately did **not** edit `2027-05-31.json` or `2027-06-14.json` — per
  precedent 12, missing contemporaneous prose reasoning is not retroactively
  invented; the correct fix is documenting the durable rule (done), not rewriting
  old files to look like the reasoning was recorded at authoring time.
- `python -m py_compile src/*.py` and `python src/validate_all_reports.py` both
  clean (94 reports, no regressions) after the precedents-doc-only change.
