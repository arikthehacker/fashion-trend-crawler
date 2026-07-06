# Confidence-precedent resolution (run 84)

Follow-up to `docs/agent-logs/confidence-precedents-consolidation-run83.md`, which
found two genuine, unreconciled precedent departures and deliberately left them
uncorrected for a human decision. This run makes that decision for each case.

## Case 1 — `data/reports/2027-05-17.json`, `dior-cruise-2027-lacma-debut`

**Decision: correct to `medium` (option b). No new precedent formalized.**

The report's `human_editor_note` argued a discrete, photographed, celebrity-attended
runway event with matching factual detail across outlets deserves an exception from
precedent 2's same-sector cap, distinct from an aesthetic/trend claim. This is a
real, non-frivolous distinction in the abstract — a verifiable single event genuinely
carries different evidentiary weight than convergent trend-naming, which is more
vulnerable to outlets copying each other's framing.

But precedent 2's own worked-example list already contains a directly on-point case:
`chanel-cruise-2027-biarritz-debut` (2027-05-03, "nine outlets, same sector") is the
same fact pattern — a discrete, single-day, photographed Cruise runway debut,
multiple editorial outlets, single sector — and was held at `medium` under precedent
2 without exception, only two weeks before this report. If "discrete verifiable
event" were a real, generalizable exception, it should have applied there too, and
it wasn't invoked. That means the exception isn't a new principle this report
discovered; it's an inconsistency with a precedent that had already been tested
against materially the same scenario and decided the other way. Formalizing it now
as precedent 13 would effectively let any well-documented single event carve itself
out of precedent 2 retroactively-by-analogy, which is exactly the loophole risk the
task asked me to guard against.

Corrected `confidence` from `high` to `medium` via `save_report(revision_reason=...,
corrected_at="2026-07-06")`, appended a correction note to the existing
`human_editor_note` (per precedent 12, the original prose is preserved, not
rewritten — the correction is appended, not substituted) citing the
`chanel-cruise-2027-biarritz-debut` precedent by name.

## Case 2 — `data/reports/2027-07-12.json`, `couture-fw27-debuts-reception`

**Decision: correct to `medium` (option b). No new precedent formalized.**

The report's `index_note` argued confidence should rise from `medium` to `high`
because the claim shifted from "forward-looking anticipation" (2027-07-05) to
"backward-looking, directly verifiable" reception (2027-07-12). Unlike case 1, this
rationale doesn't even address the mechanism precedent 3 governs. Precedent 3's rule
concerns whether `unclear`-taxonomy sources should count as real sector diversity —
and the report's own `human_editor_note` explicitly names the same unmapped domains
(wallpaper.com, nssmag.com, theimpression.com) as still `unclear` in this window. A
show having *already happened* doesn't change which taxonomy bucket a domain falls
into; the sourcing-mix gap precedent 3 cares about is structurally identical to the
prior week's. The forward/backward-looking framing answers a question ("is the
underlying fact well-established?") that precedent 3 was never about, and never
engages with the actual gap the note itself flags.

This is also directly inconsistent with the immediately preceding report
(`2027-07-05.json`, signal `couture-fw27-designer-debuts`), which held the identical
`["editorial", "unclear"]` sector mix at `medium` one week earlier, citing the same
taxonomy gap with no forward/backward distinction invoked. Two structurally
identical weekly windows on the same signal thread landing at different tiers, with
no precedent-level reasoning connecting the change, is the kind of drift precedent 3
exists to prevent.

Corrected `confidence` from `high` to `medium` via `save_report(revision_reason=...,
corrected_at="2026-07-06")`, appended a correction note to the existing
`human_editor_note` explaining why the backward/forward distinction doesn't reconcile
with precedent 3, and citing the 2027-07-05 report's identical treatment.

## Why neither became a new precedent

Both notes were genuine, reasoned editorial judgment, not carelessness — consistent
with run 83's framing. But formalizing either into precedent 13/14 would create
exactly the loophole the task warned against: "discrete verifiable event" and
"backward-looking confirmed fact" are both broad enough categories that a huge share
of future signals could plausibly claim to fit them, hollowing out precedents 2 and
3 in practice. Critically, in both cases the archive already contains an on-point
prior decision (`chanel-cruise-2027-biarritz-debut` for case 1; the 2027-07-05
report itself for case 2) that rejected materially the same argument without
comment — meaning these aren't proposals for new ground so much as unflagged
regressions against standing practice. Correcting to `medium` restores consistency
with the archive's own prior calls on the same pattern.

## Validation

`python -m py_compile src/*.py && python src/validate_all_reports.py` — all 76
reports pass schema validation after both corrections.

## Files touched this run

- `data/reports/2027-05-17.json` — `confidence` high -> medium, `revision_history`
  entry added via `save_report()`, `human_editor_note` appended (not rewritten).
- `data/reports/2027-07-12.json` — same, for `couture-fw27-debuts-reception`.
- `docs/agent-logs/confidence-precedent-resolution-run84.md` (this file).

No changes to `docs/confidence-discipline-precedents.md` (no new precedent
warranted), `TODO.md`, or `CHANGELOG.md`. No `.env`/secret contents accessed.
