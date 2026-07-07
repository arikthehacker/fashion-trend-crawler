# Full doc re-read, run 19

Read `docs/ARI3LLA INDEX.txt` end-to-end (not by section) and cross-checked against the
live codebase/site, rather than trusting CHANGELOG summaries.

## Genuinely missed items (never touched, never mentioned in any changelog/agent-log)

1. **`/glossary` page (doc §24, listed as an explicit optional page: "style terms,
   aesthetic terms, recurring classifications").** Confirmed via repo-wide search — zero
   references anywhere except the source doc itself. Every other page in §24's list
   (including the optional `/signals/[slug]` and `/timeline`) has been built; `/glossary`
   is the one that fell through 19 runs of otherwise-thorough page coverage. Distinct from
   `/taxonomy` (which documents the classification *system*) — a glossary would define the
   aesthetic *terms themselves* (coquette, mob wife, quiet luxury, etc.) as they recur
   across reports, which nothing else on the site currently does.

2. **The "THIS WEEK'S INDEX" condensed metrics module (doc §27/§28).** The doc specifies a
   scannable at-a-glance box modeled on AQI/stock-index UX: top signal, rising term,
   recurring material, dominant mood, highest-volatility sector, overall confidence.
   Checked `web/app/page.tsx` directly — the homepage only surfaces `items_collected`/
   `sources_scanned` as inline text plus the top-5 signal cards. The derived,
   glance-friendly metrics (noise level, editorial saturation, dominant mood) described in
   §28 have never been computed or surfaced anywhere, on the homepage or elsewhere. This is
   the one piece of the "index people check daily" behavioral thesis (§27, the whole reason
   for the AQI/Dow-Jones comparison) that hasn't been built.

Everything else scanned for — three-font typography stack (§35, actually implemented:
Instrument/Franklin/Reenie fonts in `layout.tsx`, just never called out by name in any
changelog), Pinterest "visual world" framing (§30, covered via the manual-sampling
workflow), TikTok/editorial-authority skepticism (§8/§9, covered extensively via
`HIGH_RELIABILITY_SECTORS` bias-audit work), designer-eye/human-review principle (§18/19,
enforced via `human_editor_note`) — turned out to already be addressed, just not always
indexed by section number in the changelog. So this is a short, real list, not a padded
one.

## New external research angle

Prior runs cited AP/Poynter/Reuters wire-style guidance, DPC/NDSA digital-preservation
practice, and WGSN forecasting methodology. One genuinely uncited angle: **controlled
vocabulary standards for costume/fashion terminology from museum/archival practice** — the
Getty Art & Architecture Thesaurus (AAT, ISO/NISO-compliant), and the ICOM Costume
Committee's costume classification system, plus the newer **Costume Core** metadata
schema (a controlled descriptive vocabulary specifically for garments/accessories,
developed for museum and archival cataloging).

Relevance: `taxonomy.py`'s garment/silhouette/material/aesthetic-term vocab is currently
built ad hoc from the concept doc's own lists (§16/§17) and expanded reactively per-sector
in run 12. Costume Core / AAT exist precisely to solve "how do you name a garment
consistently across institutions over time" — the same problem ARI3LLA INDEX has for
signal naming/dedup across reports (e.g. is "ballet flat" the same term as "rehearsal
flat"?). Not proposing adoption wholesale — the project's taxonomy is deliberately about
source/incentive classification, not object cataloging — but the naming-consistency
discipline these standards enforce is a real, uncited external precedent worth citing on
the methodology page if garment/material vocabulary drift ever becomes a problem as the
archive grows past ~11 reports.

Sources: [Getty Vocabularies (Getty Research Institute)](https://www.getty.edu/research/tools/vocabularies/), [Art & Architecture Thesaurus - Wikipedia](https://en.wikipedia.org/wiki/Art_%26_Architecture_Thesaurus)
