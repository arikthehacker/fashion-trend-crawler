# Journalism standards check (run 45): "How we did this" transparency box

## Topic

Checked existing "How we did this"/"How we did our analysis" box convention used by
Pew Research Center and FiveThirtyEight for data-driven articles: a short, visually
distinct box (bordered/shaded, a few lines) placed near the top of an article, separate
from the site's full-length methodology page. It states the essential source/collection
facts for that specific piece and links out to the long-form methodology for readers who
want more — the point is that most readers never click through to a full methodology
page, so the load-bearing facts need to live where they'll actually be seen.

Web search results were general (Pew's own methodology/FAQ pages, "State of the News
Media" methodology, FiveThirtyEight's polling methodology pages) rather than a page
specifically describing the box's design pattern by name, but the convention itself —
compact box, near the top, distinct from long-form methodology — is well-established
editorial practice and consistent with what those pages model in practice.

## What the site had

`web/app/reports/[date]/page.tsx`'s header already carried the right *content*
(collection window / sources scanned / items collected stats, plus a byline-level AI
disclosure line linking to `/methodology`) near the top, per-report rather than only on
the general methodology page. But it wasn't visually distinct from surrounding header
text — no border/box, no label — so it read as ambient header metadata rather than a
deliberately scoped "here's how this was made" unit, unlike Pew/FiveThirtyEight's boxed
treatment.

## Change made

Wrapped the existing stats line + AI disclosure paragraph in a single bordered box
labeled "How This Report Was Compiled" (matching the site's existing uppercase-label
style used elsewhere), placed directly under the report date, above the executive
summary. Changed the AI-disclosure link text from "AI use & corrections policy" to "Full
methodology" for clarity now that it sits inside a box making the same point. No new
facts added — this is a presentation-only change reorganizing already-true content into
the standard box pattern; content otherwise unchanged.

File touched: `web/app/reports/[date]/page.tsx` only.

## Verification

`cd web && npx tsc --noEmit` — passed clean, no type errors.

Not committed, per instructions.
