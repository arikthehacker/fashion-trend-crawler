# Recurrence milestone review (run 47)

Re-ran the actual signal_id recurrence count from run 24/32's methodology against
current data: 39 reports on file (data/reports/*.json), 50 unique signal_ids.

**Counts:**
- Recurring 2+ times: 14 signal_ids
- Recurring exactly 3 times: 5 (all style aesthetics: sheer-layering, soft-tailoring,
  off-duty-varsity, peplum-waist-revival, lfw-wholesale-eligibility-dropped)
- Recurring 4+ times: **4** signal_ids — cfda-fashion-fund-winner (11x),
  wales-bonner-hermes-debut (8x), cfda-fashion-awards-2026 (6x),
  paris-post-show-coverage-gap (6x)

Run 24's threshold: "4-5 signals recurring 4+ times." **This is now numerically met**
(4, the low end of the stated range) — the first time since the threshold was set.

**But the composition matters.** All four qualifying signals are unresolved
factual/institutional tracking items (an unannounced award winner, an unconfirmed
awards date, a designer-debut timeline, a coverage gap), not recurring style
aesthetics. No style-aesthetic signal has ever exceeded 3 consecutive reports —
confirming the pattern run 32 flagged. These items recur mechanically because
they're carried forward until resolved (per the existing prolonged-silence
convention), not because a style trend is genuinely re-emerging over time. A
narrative quarterly/year-in-review retrospective — the feature actually declined
at runs 24 and 32 — would still misrepresent what's recurring: it would read as
trend continuity when the real story is "these four questions remain open."

**Decision:** build the minimal, honestly-scoped thing the numbers support, not
the feature that was declined. Added:
- `getRecurringSignals(minOccurrences)` in `web/lib/reports.ts` — aggregates
  existing per-signal-id data (same source `/signals/[slug]` already reads),
  no new schema or data collection.
- A "Recurring across the archive" section on `web/app/archive/page.tsx` listing
  the 4 qualifying signals, their occurrence count/date range, linking to their
  existing `/signals/[slug]` history pages, with prose stating plainly that all
  four are factual/administrative items rather than style aesthetics.

This is not a quarterly retrospective (no narrative synthesis, no "trends of the
quarter" framing) — it's a factual surface of data the archive already has,
scoped honestly to what the numbers actually show.

**Threshold going forward:** the "4-5 signals recurring 4+ times" bar was
calibrated at run 24 assuming recurrence would mean style-aesthetic persistence.
That assumption hasn't held — style signals cap at 3, factual questions recur
by carry-forward mechanics. Recommend the threshold be reframed at the next
review to require the *style* half of the archive's signals to clear 4+
recurrences before a narrative retrospective is warranted (i.e., don't count
factual/administrative carry-forwards toward the retrospective trigger at all —
they measure "unresolved," not "trending"). Left as a note for the next
retrospective-format review rather than changed unilaterally here, since
redefining the metric is a bigger judgment call than this run's scope.

**Verification:** `cd web && npx tsc --noEmit` clean; `python -m py_compile src/*.py`
clean (no Python files touched this run).
