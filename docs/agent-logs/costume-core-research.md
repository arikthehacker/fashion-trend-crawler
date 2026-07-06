# Costume Core / Getty AAT research (run 19 follow-up)

Researched via WebSearch. **Costume Core** is a controlled, hierarchical metadata schema
for garments/accessories developed for museum and archival cataloging (born out of the
Costume Society/CIETA-adjacent digitization community); it defines fixed term sets per
garment class, material, and construction feature so two institutions describing the same
object converge on the same string. The **Getty Art & Architecture Thesaurus (AAT)** is
the broader ISO/NISO-compliant thesaurus Costume Core term choices are meant to map into —
it enforces preferred terms plus documented synonym/variant relationships (e.g. "peplum" as
a garment-part facet with cross-references, not a free-text tag).

## Checked against all 12 reports in `data/reports/*.json`

Grepped `garments`, `materials`, `aesthetic_terms` across every report. Most recurring
terms are actually consistent: "quiet luxury," "structured blazer," "soccer jersey,"
"denim," "Y2K nostalgia" all reappear with identical spelling/form across windows, often
explicitly marked `(carryover)`. The team is already doing informal consistency discipline
via `signal_id` continuity.

**One genuine drift case found:** `signal_id: "peplum-waist-revival"` is carried across
2026-08-10, 2026-08-17, and 2026-08-24 as the same trend line. The `garments` field for it
reads:
- 2026-08-10 / 2026-08-17: `"peplum skirt"`, `"peplum trouser"`
- 2026-08-24: `"peplum jacket"`

Same signal_id, same close-out narrative, but the garment noun silently changes from
trouser to jacket with no note explaining whether the underlying evidence (Dior/McQueen/
Stella McCartney runway pieces) actually shifted garment type or whether this is just
looser labeling in the extraction step. A controlled vocabulary wouldn't fix the
underlying evidence gap (already flagged in the report's own methods-limitation note), but
it would have forced a deliberate choice — either log both terms explicitly as variants of
one signal, or note the change — rather than let it pass silently.

## Recommendation

Not worth a dedicated adoption run yet. With one clear drift instance across 12 reports
and ~35 total garment mentions, the archive is too small for a formal vocabulary's
overhead (schema design, mapping existing terms, maintaining a lookup table) to pay off.
The cheaper fix is a lightweight practice: when a `signal_id` is carried forward, keep its
garment term list append-only unless a note documents why it changed. Revisit real
adoption once the archive is materially larger (order of 50+ reports) or drift instances
recur.
