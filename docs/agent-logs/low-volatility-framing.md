# Low-volatility framing (thin collection status)

Following run 15's live-crawl-vs-websearch check, which confirmed the recent
thin-week streak reflects genuinely low style-discourse volatility rather than
a crawl or research gap, added a new methodology section: "How Low-Volatility
Windows Are Reported" in `web/app/methodology/page.tsx`, placed between
"Limitations" and "Corrections."

The section states plainly that `collection_status: "thin"` means fewer
signals met recurrence/diversity thresholds than usual, that this is checked
against raw source volume where possible, and that a verified low-volatility
period is recorded as a data point rather than filled with manufactured
signals to hit a target count.

Kept in wire-service voice matching the Corrections/Editorial Independence
sections (run 7) — no first person, no "we're proud of," no defensiveness or
self-congratulation. It states the policy the same flat way those sections
state correction and independence policy.

Only `web/app/methodology/page.tsx` was touched.

Verified with `cd web && npx tsc --noEmit && npx next build` — both passed
clean, all 43 routes generated successfully.

Not committed, per instructions.
