# Journalism standards check — run 51: operator transparency

## Topic chosen
Operator/ownership transparency on the About page — distinct from the AI-use disclosure
already covered. The Trust Project's 8 Trust Indicators explicitly include "who and what is
behind a story" as its own indicator, separate from AI/authorship disclosure; American Press
Institute and INN guidance on disclosure/transparency likewise treat "who runs this and how
is it funded/owned" as a standalone trust signal a reader should be able to find without
digging.

## What the site had
`web/app/about/page.tsx`'s "Independence, Corrections, AI Use" section disclosed:
non-affiliation with brands/platforms, AI's role in the pipeline, and the correction policy.
It never stated who or what actually operates ARI3LLA INDEX — a reader had no way to tell
whether this is a staffed publication, a company, or an individual's project. The
`/case-study` page reveals it's a solo build only if a reader happens to click through to a
portfolio-framed page; that's not equivalent to the About page (the canonical
transparency/trust destination) stating it directly.

## Fix
Added one paragraph to the About page's Independence/Corrections/AI Use section, right after
the non-affiliation paragraph, stating plainly: ARI3LLA INDEX is an independently operated
research and reporting project, not a staffed newsroom or commercial publication; it is built
and maintained by a single researcher-developer with source published on the project's public
repository; there is no separate editorial board, ownership structure, or funding source to
disclose beyond that. Kept in report/wire-service voice (no first person, no hype), matching
existing paragraph styling.

## Verification
`cd web && npx tsc --noEmit` — passes, no errors.

## Not touched
No other files modified. Did not commit (per instructions). Another agent was concurrently
editing the same `about/page.tsx` file mid-task (an AI-review-recorded-by paragraph appeared
between my read and my edit) — re-read the file and re-applied the edit against current
content rather than clobbering it.
