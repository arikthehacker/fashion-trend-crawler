# "Year in review" research + updated recurrence check (run 29-ish, proposal only)

## Is a responsible "year in review" a distinct practice?

Yes — trade-press/newsletter guidance (Substack creator posts on year-end and
retrospective formats, general journalism-cadence advice) describes it as structurally
different from both a hype "best of" listicle and a quarterly retrospective:

1. **Data-grounded, not vibes-grounded.** Effective year-end pieces use real inputs
   (what recurred, what was tracked, what stayed unresolved) rather than "team feelings"
   or subjective favorites — the same principle run 24 already found for quarterly
   recaps.
2. **Organized by trajectory across the whole year**, not a top-10 countdown: what
   persisted, what emerged once and faded, what's still open/unresolved at year-end.
   This is a wider time window than a quarterly retrospective but the same underlying
   unit of analysis (trajectory, not weekly snapshot).
3. **Cites back to the source issues**, doesn't replace them — consistent with this
   archive's source-linked model.
4. **Threshold-gated in spirit**: the guidance repeatedly warns against manufacturing a
   year-end piece just because the calendar rolled over with nothing substantive to
   report — the exact failure mode run 27 already rejected for the 6-month milestone.

Net: a "year in review" is real, but it inherits run 24's data bar, only stretched over
a longer window — it doesn't lower the bar just because "year" sounds more significant
than "quarter."

## Updated recurrence count (all current reports)

Re-ran the `signal_id` recurrence count directly against `data/reports/*.json`:

- **24 reports** now on file (2026-05-07 through 2026-12-07) — up from 16 at run 24.
- **42 unique signal_ids** (up from 36).
- Only **one** signal_id recurs 4+ times: `cfda-vogue-fashion-fund-2026-winner`, in 7
  reports (2026-10-26 through 2026-12-07). That's not a style signal — it's the same
  unresolved-award-status item TODO.md already flags as "awaiting resolution," carried
  forward week to week because it hasn't resolved, not because a style thread is
  sustaining.
- Everything else tops out at 3 recurrences: `soft-tailoring`, `sheer-layering`,
  `off-duty-varsity`, `peplum-waist-revival` (3 each), plus a `lfw-eligibility` logistics
  item (3) — unchanged in kind from run 24's findings, just slightly more instances.

## Assessment

**Threshold not met — for either format.** Run 24 set the bar at 4-5 signals recurring
4+ times. Current data has **zero** style signals clearing 4+, and only one non-style
logistics/status item does. That's further from the bar in substance than run 24's
count, even though report volume grew by 8. A year-in-review inherits this same bar per
the research above (real recurrence, not calendar timing), so the calendar rolling into
December is not itself a reason to ship one.

**Recommendation:** don't build a year-in-review page for Dec 2026. Re-run this same
count after fashion month's aftermath fully settles (a few more reports past 12-07) —
if `off-duty-varsity`/`peplum-waist-revival`-style patterns pick up a 4th non-adjacent
appearance, revisit both the quarterly and year-in-review options together, since
they'd draw on the same underlying trajectory data.
