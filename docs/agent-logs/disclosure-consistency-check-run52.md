# Disclosure consistency check (run 52)

Scope: re-read the full current text of `about/page.tsx`, `methodology/page.tsx`, and
the report page's "How This Report Was Compiled" box/byline post-run-51, checking for
cross-page inconsistency, leftover awkward repetition, and clarity of the disclosure.

## Finding: internal inconsistency within methodology.tsx itself

Run 51 fixed the overclaim in exactly one section of `methodology/page.tsx` ("AI
Involvement," near the bottom of the page) and in `about/page.tsx`. Those two now agree
and read clearly. But the same page had **two other sections, written earlier in the
page, that still flatly asserted human review** without the disclosure added below them:

- "How AI Is Used": "Final classification depends on the Index taxonomy and human
  review." (no hedge)
- "Limitations": "Signal classification involves human judgment applied to
  machine-extracted data..." (no hedge)
- A section literally titled **"Human Review Process"** near the end of the page, never
  touched by run 51, stating "Human review interprets whether those terms belong
  together..." as flat fact.

A first-time reader hitting "How AI Is Used" (section 5 of ~16) would get a confident,
unhedged claim of human review, then reach "AI Involvement" (much later) and "Human
Review Process" (the very last section) and find a contradicting disclosure — or, in
the "Human Review Process" section's case, no disclosure at all. This is exactly the
inconsistency pattern the task was checking for, and it was real.

## Fix applied

- "How AI Is Used": now says classification depends on taxonomy and "a review step
  against editorial guidelines, currently carried out by the same automated process
  rather than a separate named human editor," pointing to "AI Involvement" below.
- "Limitations": reworded "human judgment" to "an interpretive review layer... currently
  performed by the same automated process," pointing to "AI Involvement."
- Renamed "Human Review Process" to "Review Process" and added the same disclosure
  sentence, pointing back to "AI Involvement" above.

`about/page.tsx` and the report page's byline/box (`reports/[date]/page.tsx`) were
re-read and already agree with each other and with methodology's "AI Involvement"
section — no changes needed there. Phrasing across the three is not verbatim-duplicated
(no awkward repetition), and each disclosure reads as a direct, plain sentence rather
than buried legal hedging.

## Verification

`cd web && npx tsc --noEmit && npx eslint .` — both clean, no errors.

## Not touched

No schema, data, or process changes. Copy-only, confined to
`web/app/methodology/page.tsx`.
