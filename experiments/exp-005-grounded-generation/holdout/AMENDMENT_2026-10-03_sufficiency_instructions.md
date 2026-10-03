# Amendment 2026-10-03: packet-sufficiency reviewer instructions (C1)

**Status:** pre-review clarification, made by the owner's ruling. It was created at 2026-10-03 20:40 UTC, when 0 of 30 packet-sufficiency cards had been answered (no review log existed) and before any generation or model call for the holdout.

**Applies to:** the C1 packet-sufficiency review of the 30 holdout packets (`packets_v1_manifest.json`, SHA-256 `cfb304502588deabf23350f1a2d718321d49b46fdefcf07c3e831abf7f61dbc6`).

**Unchanged:** `protocol_v1_frozen.json` (SHA-256 `0e0e6a98fa3982e246e12a959b50ae5ede237748275a626c017c8bf5c6232af5`) is not edited. The questions, packets, labels, card prompt, metric formulas, hypotheses, Prompt v2 and Schema v2 are unchanged. Where the frozen label wording (`sufficiency_review.labels`) is less specific, these instructions decide how the reviewer applies it.

## The labels

**SUFFICIENT.** The exact evidence packet alone contains enough evidence to answer the question as asked, within its stated constraints, without adding outside facts or unsupported inference. If the question has multiple material parts, the packet must support all material parts.

**INSUFFICIENT.** The packet may contain relevant evidence, but it does not contain enough evidence to answer the question as asked without adding unsupported facts or inference. Partial support is still INSUFFICIENT.

**UNSURE.** The packet itself is ambiguous or unclear enough that the reviewer genuinely cannot determine whether it supports an answer. UNSURE is not used merely because the judgment is difficult, because some relevant evidence exists, or because the packet is only partially sufficient.

## Rules for every card

- 10 items does not automatically mean sufficient.
- Relevant evidence does not automatically mean sufficient.
- Judge only the exact packet shown.
- Do not open URLs, search, or use outside knowledge. A URL in the packet is packet text only (as in the 2026-10-01 evidence-boundary amendment).

## Metric treatment (unchanged)

| Label | Treatment |
|---|---|
| SUFFICIENT | H2 denominator (grounded answer rate) |
| INSUFFICIENT | H3 denominator (correct abstention rate) |
| UNSURE | excluded from both the H2 and H3 denominators, never translated into either label, reported separately |
