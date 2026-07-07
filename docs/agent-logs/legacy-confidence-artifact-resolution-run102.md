# Legacy confidence artifact resolution — run 102

## The open item

`data/reports/2026-05-07.json`, the archive's very first report
(`reviewed_by: "hand-authored-placeholder-run0"`), has a `sheer-layering` signal with
`source_corroboration_count: 2` across two distinct `source_sectors`
(`["editorial", "retail"]`). `src/report_schema.py::derive_confidence()` would
mechanically compute `high` for that shape. The report assigns `confidence: "medium"`,
with no `confidence_source` field at all (the field did not exist yet when this report
was authored — it predates the entire confidence-discipline apparatus documented in
`docs/confidence-discipline-precedents.md`).

Runs 99 and 100 both flagged this mismatch and declined to act, correctly refusing to
invent retroactive override reasoning that was never contemporaneously recorded (per
precedent 12). Neither run closed the item — both left it as "flagged, unresolved."
This run's job was to actually decide, not defer a fourth time.

## Reading the report in full

Full content read from `data/reports/2026-05-07.json`:

- `executive_summary`: "This report identifies recurring style signals across 25
  collected items from 12 public web sources... Coverage is primarily editorial, so the
  report reflects style media discourse rather than retail sales or broad consumer
  adoption."
- Three signals total: `sheer-layering` (medium, count 2, sectors
  editorial+retail), `soft-tailoring` (medium, count 3, sectors
  editorial+retail+designer_origin — also mechanically `high` and also left at
  `medium`), `archival-romanticism` (medium, count 2, sectors
  editorial+independent_criticism — also mechanically `high`, also left at `medium`).
- `limitations`: "Coverage is skewed toward editorial sources and may not reflect
  retail sales data," "Social platform signals are limited... classified as
  high-noise," "Sample size is small relative to the full scope of public style
  discourse."
- `human_editor_note`: **"Placeholder example report used to scaffold the archive and
  report page templates."** This is the load-bearing fact for the whole decision.
- `reviewed_by`: `"hand-authored-placeholder-run0"`.
- `revision_history`: one prior entry, run-of-record backfilling `reviewed_by`
  provenance metadata only — no confidence-related edit has ever been made to this
  file.

Notably, all three signals in this report — not just `sheer-layering` — hit the same
mechanical-vs-assigned mismatch (2+ sectors, count >= 2, assigned `medium` instead of
mechanical `high`). That's a strong signal this wasn't an evidence-specific editorial
judgment call made signal-by-signal (the way precedents 1-17 all are, each turning on
some specific fact about *that* signal's sourcing) — it's a uniform placeholder
authoring convention applied identically across the whole file.

## Working through the three options

**Option 1 — is `medium` defensible via a nameable reason, correctable via a new
`confidence_source` field?** No. Every real precedent in
`confidence-discipline-precedents.md` that manually holds a signal below its mechanical
tier does so by pointing at something *specific and checkable* about the actual
sourcing: republication within one sector (precedent 2), an unmapped-domain gap
(precedent 3), a downstream reprint (precedent 4), a commercial vertical's incentive
(precedent 8), calendar-driven durability risk (precedent 9), wire-syndication versus
trade press (precedent 10). None of that is available here. `evidence`,
`index_note`, and `source_sectors` for `sheer-layering` are generic hand-authored
placeholder text ("Repeated references to transparent fabrics, mesh, organza, and
layered styling across editorial sources") describing no real, individually
identifiable outlets — there is nothing to check "editorial" and "retail" against,
because there is no underlying source list at all. Precedent 12 draws the line at
whether reasoning was *contemporaneously recorded*, not whether the field existed yet;
inventing a specific override rationale now, about sources that were never real, would
manufacture a false record of editorial judgment that never happened. This option is
foreclosed.

**Option 2 — mechanically correct: use `save_report()` to raise `sheer-layering` (and,
for consistency, `soft-tailoring` and `archival-romanticism`, which have the identical
shape) to `high`?** Also rejected. `derive_confidence()` is a formula for scoring real
corroboration across real, taxonomy-mapped sources. Applying it here would produce a
technically-mechanical-but-substantively-meaningless result: there were never 12 real
scanned sources or 25 real collected items behind this report, so "high confidence"
would assert a false thing — that two independently verifiable source sectors actually
corroborated this signal — about content that was invented to test the archive's own
templates. Correcting it upward doesn't fix an under-confident real judgment; it would
dress up placeholder content in the language of a rigorous one, which is worse than
leaving the mismatch alone.

**Option 3 — grandfather clause: leave as-is, document explicitly, close the item.**
This is the correct call. The report is not a case of "confidence discipline applied
inconsistently to real evidence" (which is what every other precedent in the document
addresses) — it's synthetic scaffolding content that predates confidence discipline
existing at all, explicitly self-labeled as such by its own author. Precedent 3's
"taxonomy fixes are not retroactive" companion ruling and precedent 12's prose/
structured-field distinction both point the same direction: later apparatus does not
reach back and re-derive judgment calls that were never made under it, and structured
fields are only correctable when there's a real, checkable fact underneath them to
correct *to*. Here there isn't one.

## Decision

**Leave `data/reports/2026-05-07.json` unmodified.** No `save_report()` call was made —
there is nothing to change that would represent a legitimate correction rather than a
fabrication. Documented the decision at
`docs/confidence-discipline-precedents.md`'s "Related, non-override background"
section (new bullet, dated run 102) so this is a permanent, explicit historical
grandfather clause, not a silently-accepted inconsistency that a future audit
re-discovers and re-flags as unresolved for a fifth time. The precedents-doc entry
covers `sheer-layering` specifically (the signal named in this task) and notes the same
reasoning applies identically to `soft-tailoring` and `archival-romanticism` in the
same file, since all three share the exact same placeholder-authorship shape.

## Verification

- `python -m py_compile src/*.py` — passed, no output (no code changed).
- `python src/validate_all_reports.py` — `OK: all 95 report(s) in data/reports/ passed
  schema validation.` Unchanged from before this run, since no report data was edited.

No `.env` or API key content was read, printed, or logged during this task.
