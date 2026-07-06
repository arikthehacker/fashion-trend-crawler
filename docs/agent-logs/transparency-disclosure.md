# Transparency / disclosure pass

Addressed gap from `docs/agent-logs/gap-analysis-run6.md`: no corrections, editorial
independence, or AI-involvement disclosure anywhere on the site.

Files touched (only these two, as scoped):
- `web/app/methodology/page.tsx`
- `web/app/about/page.tsx`

## Methodology page
Inserted three new sections into the `sections` array, ahead of "Ethical Scraping and
Source Policy": **Corrections** (dated correction notes appended to affected reports,
original entry preserved, not silently edited), **Editorial Independence** (independent
project, not sponsored by or affiliated with any named brand/publication/platform;
editorial treated as a source sector with its own incentives, not neutral authority —
extends the existing "How Editorial Authority Is Treated" section rather than
duplicating it), and **AI Involvement** (AI assists with crawling/extraction/clustering/
drafting; human reviews and makes final classification/origin calls, recorded via the
human-editor note — ties to the `human_editor_note` schema field and doc §18/19's
human-in-the-loop principle).

## About page
Added one new block ("Independence, Corrections, AI Use") between the existing "This
Index Is" block and the closing philosophical line, matching the page's existing
uppercase-label + body-paragraph pattern. Condenses the same three points for a reader
who never visits Methodology, with an inline link to Methodology for full detail.

Checked `docs/ARI3LLA INDEX.txt` §37/38 first — these only cover the "is/is not" product
list and the philosophical stance already reflected in About; no existing
corrections/independence/AI-disclosure language to extend, so new content was additive
rather than a rewrite.

Voice: no first person, no "we take X seriously" framing, wire-service tone consistent
with rest of both pages.

## Verification
`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 35 routes
generated successfully. Not committed, per instructions.
