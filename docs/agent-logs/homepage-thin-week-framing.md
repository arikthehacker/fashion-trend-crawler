# Homepage thin-week framing

Checked how the "Latest Report" teaser (run 13) renders the current latest
report, `data/reports/2026-08-24.json`, which is `collection_status: "thin"`.

The `executive_summary` doesn't abruptly say "collection was thin" — but it
also doesn't read like homepage teaser copy. It's dense internal
methods-review language (dormancy thresholds, `get_signal_status_history()`
references, closing out signals via revision), written for the report-detail
audience, not a first-time homepage visitor. Dropped onto the homepage with
no framing, a thin week reads as an unexplained wall of caveats rather than a
stated editorial policy.

## Change

`web/app/page.tsx`: added a conditional note directly under the executive
summary paragraph, shown only when
`(latest as unknown as { collection_status?: string }).collection_status === "thin"`
(cast used since `collection_status` isn't on the `Report` TS interface yet,
matching the precedent in `web/lib/reports.ts`'s
`getConsecutiveThinWeekCount()`). One line, wire-service tone, no
defensiveness: states the window is classified thin, that low-volatility
periods are recorded as a verified data point rather than filled to a target
count, and links to `/methodology` instead of repeating that page's full
explanation.

## Archive page

Read `web/app/archive/page.tsx`'s existing thin-streak note (run 13). It
already matches the required tone (flat, factual, "no alarm, no apology") and
needs no edit. Not touched.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 44
routes generated.

Not committed, per instructions.
