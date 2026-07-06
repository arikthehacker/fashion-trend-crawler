# Recurrence threshold revision (run 48)

Run 47 found the "4-5 signals recurring 4+ times" retrospective-trigger threshold
(set run 24, re-confirmed run 32) was numerically met for the first time, but only
because 4 unresolved factual/institutional-tracking signals (CFDA fund, CFDA awards,
Wales Bonner debut, Paris coverage gap) recur mechanically via carry-forward, while
no genuine style-aesthetic signal has ever exceeded 3 consecutive reports. Run 47
correctly declined to build a retrospective on that basis but left the threshold's
composition problem as a note rather than fixing it.

**Decision: option (a), add real filtering logic**, not just documentation. The
archive already has exactly the distinction needed: `Signal.type` (populated in
data, typed in `TopSignal`) already separates style-aesthetic types
(`styling_behavior`, `silhouette`, `aesthetic_term`, `cultural_term`, `color`,
`social_observation`) from factual/administrative types (`institutional_policy`,
`designer_signal`, `market_behavior`, `industry_recognition`, `media_integrity`,
`industry_event`, `retail_calendar_event`). Verified directly against data: all 4
of run 47's qualifying signals are `institutional_policy` except
`wales-bonner-hermes-debut`, which is `designer_signal` — also non-style, since it's
a debut-timing question, not an aesthetic description. `origin_classification` was
considered but rejected: it distinguishes designer/editorial/retail/social origin,
not fact-vs-aesthetic, and doesn't map cleanly to this question.

**Implemented in `web/lib/reports.ts`:**
- Added `STYLE_AESTHETIC_TYPES` allowlist and an `is_style_aesthetic` field on
  `RecurringSignal`.
- `getRecurringSignals(minOccurrences, { styleOnly })` — new optional second
  argument, backward compatible (default `{}`, existing single-arg callers on
  `/archive` unaffected).
- Filters on each signal's *most recent* occurrence's `type`, since a signal's
  framing can shift across reports.

**Threshold going forward:** the run-24/47 retrospective trigger must be
evaluated with `getRecurringSignals(4, { styleOnly: true })`, not the raw call.
The raw/unfiltered count remains correct as-is for the archive page's existing
"Recurring across the archive" factual/administrative surface (run 47) — that
is a legitimately different, already honestly-scoped use of the same data and
was not touched.

Did not change `/archive`'s rendering this run — out of scope; the fix was the
threshold definition/filtering capability, not a new UI surface. A future run
evaluating the retrospective trigger should call the `styleOnly` variant and
will currently get 0 qualifying signals, correctly not meeting the bar.

**Verification:** `cd web && npx tsc --noEmit` — clean.

TODO.md's run-48 carried-forward note updated to reflect this as closed rather
than deferred again.
