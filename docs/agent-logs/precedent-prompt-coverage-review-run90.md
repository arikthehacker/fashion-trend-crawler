# Precedent prompt-coverage review — run 90

## Task

Run 89 condensed 5 of the 14 confidence-discipline precedents
(`docs/confidence-discipline-precedents.md`) into `src/summarize.py`'s
`build_prompt()`, leaving out precedents 1, 4, 7, 8, 9, 10, 11, 12, 13. This
review checks whether the actual report archive (`data/reports/*.json`)
shows real recurrence for any of those 9 that would justify promoting them
into the condensed in-prompt summary.

## Method

Grepped `data/reports/*.json` for each precedent's distinguishing
terminology (both loose keyword matches and tight `human_editor_note`
phrase matches), beyond the founding/reinforcement examples already cited
in the precedents doc itself.

## Findings per excluded precedent

- **1 (single-source-multi-sector):** only the pre-run-6 founding case
  (`2026-07-13.json`, `resale-growth`) is documented, resolved by finding a
  real second source rather than by repeated future application. No further
  applications found in later reports.
- **4 (reprint/aggregator):** founding case (`2027-04-12.json`,
  `glamoratti-revival`) plus one reinforcement
  (`pfw-ss28-calendar-confirmed`, `2027-09-06.json`, discussed via
  `confidence-recompute-2027-09-06-run72.md`). Two real instances total.
- **7 (nominal-sector mislabeling):** founding case
  (`sleepwear-as-outerwear-relaxed-tailoring`, `2027-06-07.json`) plus one
  reinforcement (`royal-purple-color-trend`, `2027-06-14.json`, not captured
  by a grep match on this pass but already documented in the precedents
  file). Two instances.
- **8 (commercial-vertical discount):** one instance only
  (`beaded-jewelry-revival`, `2027-06-07.json`). No recurrence since.
- **9 (calendar-driven event hold):** one instance only
  (`blokecore-world-cup-jersey-styling`, `2027-06-21.json`). Confirmed by
  direct grep for "calendar-driven"/"external sporting event" phrasing
  across the full archive — no other report applies this rule.
- **10 (wire/broadcast vs. trade press):** one instance only
  (`lv-waterfall-heatwave-backlash`, `2027-07-26.json`). No recurrence.
- **11 (attention-economics categorization):** one instance only
  (`ragebait-runway-casting`, `2027-08-09.json`). No recurrence.
- **12 (structured vs. prose correctability):** one instance
  (`godet-skirt-backfill-decision-run68.md`, referencing `2026-07-20.json`
  and the `human-editor-note-quality-audit-run49.md` duplicate finding).
  This is also a narrower editorial-process rule (about *when fields may be
  rewritten*), not a `derive_confidence()` override at all — it isn't the
  same kind of rule as the other 13 and wouldn't fit naturally into the
  confidence-discipline section of the prompt even if it recurred.
- **13 (resale-platform reliability):** direct grep for the five resale
  domains (`therealreal.com`, `vestiairecollective.com`, `depop.com`,
  `grailed.com`, `poshmark.com`) across all of `data/reports/*.json` returns
  exactly **one file**: `2027-12-20.json`. The `resale` sector has never
  reappeared in any other report to date. This is a single founding
  instance, not a recurring pattern — despite being the most recently
  formalized and most elaborately reasoned precedent in the doc, it has had
  zero opportunities to recur since run 84/85.

## Judgment

None of the 9 excluded precedents show real recurrence beyond their
documented founding case (or a single reinforcement, for 4 and 7). By
contrast, the 5 precedents run 89 promoted (same-sector cap, unclear-domain
gap, citation-free rehash, same-week coincidence, forecast exclusion) each
have 5-12+ independently logged applications across the archive — an order
of magnitude more real recurrence than any of the 9 candidates here.

Precedent 13 (resale) was the most plausible promotion candidate going in,
given how much reasoning went into formalizing it — but "well-reasoned"
and "frequently recurring" are different properties, and the grep is
unambiguous: resale sourcing has appeared exactly once, ever. The same is
true of precedent 9 (calendar-driven events), which will presumably recur
again as fashion seasons/majors sporting events continue, but has not yet
done so a second time.

**Decision: no change to `src/summarize.py`.** The current 5-precedent
condensed summary remains the right cut based on actual recurrence
evidence. If `resale` or calendar-driven-event sourcing shows up again in
future reports, revisit at that point — this is exactly the kind of
"worth revisiting if any of them turn out to recur often" check run 89
flagged for, and the honest answer right now is that none of them have.

## Validation

No code changes made to `src/summarize.py`; `py_compile` not needed since
the file was not touched.
