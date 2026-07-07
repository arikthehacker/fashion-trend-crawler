# Fashion-specific archive standards research

Question: how do real fashion/costume archives handle uncertain attribution,
dating ambiguity, and provenance gaps, and does that suggest anything for
`src/report_schema.py`'s confidence/origin_classification/corrections model?

## What was found

**The Met's Costume Institute** (via "Fashion Back Stories," which links
archival designer material to Costume Institute objects) and general museum
provenance practice use standardized qualifier language rather than binary
attributed/unattributed states: "Attributed to [name]" for probable-but-unconfirmed
authorship, and "reportedly," "possibly," "probably" for degrees of uncertainty
in provenance chains (Brooklyn Museum's stated convention). Historical gaps are
recorded explicitly rather than omitted — "unknown buyer," "private collection,"
"circa [date]" — and museums frame full disclosure of what is *not* known as a
duty, not a weakness (Brooklyn Museum's provenance pages, MFA Boston's
Acquisitions and Provenance Policy).

**FIT's Special Collections & FIT Archive (SPARC)** publishes finding aids
(archival description documents) for each of its ~500 manuscript collections,
and separately maintains a web-archive layer (via Archive-It) whose explicit
purpose is to capture supporting context for the *provenance* of its physical
holdings — i.e., the institution treats "why do we believe this is what we
say it is" as its own archival object, kept apart from the primary holding.

## Comparison to this project's current practice

- `origin_classification` in the taxonomy is closer to the Met's "Attributed
  to" convention than it first appears: it already forces a sourced claim
  about who originated a look (designer/editorial/retail/social) rather than
  flattening it, which is the same instinct as not just writing "Worth" but
  "Attributed to Worth."
- `Signal.confidence` + `confidence_source` ("manual" vs "derived") already
  does what museums do with qualifier language ("possibly," "probably") —
  it's a discrete tier instead of prose, but it serves the same function:
  making uncertainty visible instead of silently upgrading it.
- `revision_history` in `save_report()` (requiring a non-empty `reason` and
  `corrected_at` when overwriting a report with different content) is a
  closer, more rigorous analog to provenance record-keeping than most
  digital-archive practice reviewed in the prior journalism-standards run —
  it already captures "what changed and why" the way a finding aid captures
  ownership-chain gaps.

## Recommendation

Nothing found here requires new schema fields. One low-cost, low-risk
addition genuinely modeled on museum practice: allow a signal's
`origin_classification` to carry the same "attributed" qualifier museums use
for authorship uncertainty — e.g. a signal known to have designer-adjacent
language but not confirmed as designer-originated currently has to pick one
discrete `origin_classification` value or omit the claim. If this comes up
in practice (an editor genuinely unsure between two origin classifications),
consider letting `index_note` carry that hedge in prose rather than adding a
new schema field — which is consistent with how FIT/Met handle it (qualifier
language in the description, not a new controlled-vocabulary term for every
degree of doubt). This is a documentation-pattern confirmation, not a gap:
current practice already tracks well with how fashion-specific institutional
archives handle the same problem.

## Sources

- https://www.metmuseum.org/perspectives/designer-archives ("Fashion Back Stories: Linking Archival Material to Costume Institute Objects")
- https://www.brooklynmuseum.org/research/provenance
- https://www.mfa.org/collections/provenance/acquisitions-and-provenance-policy
- https://www.philamuseum.org/provenance
- https://fitnyc.libguides.com/sparc (Special Collections & FIT Archive home)
- https://atom-sparc.fitnyc.edu/ (SPARC Connect finding aids)
- https://archive-it.org/organizations/1173 (FIT web archive, provenance-support purpose)
