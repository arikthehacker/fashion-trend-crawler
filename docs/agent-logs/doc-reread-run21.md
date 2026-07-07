# Doc re-read, run 21

Third full pass of `docs/ARI3LLA INDEX.txt`, focused on details within
already-partially-built features (per runs 19/20's own recommendation), plus a
literal check of the two things run 20 just shipped.

## New finding: `human_editor_note` is populated but never rendered

Section 23's per-report schema field list includes `human_editor_note`, and the
skill doc's workflow conventions (#5) treat this field as the load-bearing
artifact of the "human decides what clusters mean" principle — not
decoration. `web/lib/reports.ts` types it (`human_editor_note?: string`), and
most archived reports actually populate it with substantive per-signal editor
review text (`data/reports/2026-07-13.json` has four distinct, meaningful
notes — flagging a Pinterest primary-source gap, a possible recycled-cycle
headline, a confidence-audit correction, a coined-term concern).

None of it surfaces anywhere in `web/app/reports/[date]/page.tsx` — grepped
for the field, no match. The one place the doc's most explicit human-review
evidence exists is silently dropped from the public report view. This is a
real, previously-unflagged gap: the feature (schema field, editorial
discipline of writing the notes) is fully built, but the last rendering step
was missed.

## Glossary vs. doc intent (literal comparison)

Section 24 specs `/glossary` as "style terms, aesthetic terms, recurring
classifications." The shipped page (`web/app/glossary/page.tsx`) only sources
terms from `aesthetic_terms`, `cultural_references`, and `top_signals[].name`
— it explicitly excludes "recurring classifications" (e.g. volatility labels
like flash/microtrend/revival from section 15, confidence tiers from section
14) and documents that exclusion as deliberate, deferring those to
`/taxonomy`. This is a minor, self-aware drift rather than an oversight — the
page's own header comment justifies the split — but it means the doc's
three-part glossary spec is only two-thirds literally implemented. Worth a
one-line note if `/taxonomy` doesn't already cross-link back from `/glossary`
(it doesn't currently — `/glossary` links to `/taxonomy` only via prose, no
direct anchor to specific classification terms).

## "THIS WEEK'S INDEX" vs. doc intent

Compared `web/app/page.tsx` module fields against section 27's example
verbatim: sources scanned, items collected, top signal, rising term,
recurring material, dominant mood, highest-volatility sector, overall
confidence — all eight fields present and correctly labeled. No drift found.

## Everything else

No other new gaps surfaced. Sections already covered by prior runs (schema,
prompt, methodology, taxonomy, sources, archive, timeline, signals/[slug],
search, glossary, this-week's-index, about, case-study, README, ethical
scraping) hold up on this third re-read. Two real re-reads in a row (run 19,
run 21) each found exactly one rendering-layer gap rather than a missing
feature — the concept doc appears close to fully covered at the feature
level; remaining gaps are likely to keep being this granular (a field typed
but not displayed) rather than a whole missing page.
