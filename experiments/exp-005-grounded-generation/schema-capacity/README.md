# EXP-005 SC-1: schema capacity

**Question:** does stating the existing schema v2 size limits in the prompt raise first-attempt schema validity, without new integrity failures or a material loss of grounding or completeness?

**Conditions:**
- **A:** Prompt v2, unchanged.
- **B:** Prompt v2.1. It is Prompt v2 with one appended "Size limits" section. No other byte differs.

Schema v2, the serializer, the frozen hybrid retriever, the provider settings and the retry policy are unchanged. Both conditions receive the same evidence packet for each question.

**Batch:** 8 EXP-004 DEV questions never used in EXP-005 generation, chosen by fixed rules before any output (`runs/sc-batch-1/batch.json`). Every condition runs once per question.

**Primary metric:** first-attempt schema validity per condition. The comparison rule is frozen in `protocol/protocol_sc1.json` before any call.

**Review:** human review is blind. The deck "Schema-capacity blind review (EXP-005 SC-1)" hides the condition and judges only against the evidence packet. `runs/sc-batch-1/blind_key.json` and `outputs.jsonl` reveal the conditions, so they are not opened before the review is frozen.

No prompt is chosen until the owner's review is complete.

## Result (2026-10-03)

The owner's blind review of all 87 tasks was frozen and pushed before unblinding (`84340cb`, review SHA-256 `14cf96ba…`). The conditions were then unblinded once with the frozen key and scored with the frozen metrics (`runs/sc-batch-1/sc1_scores.json`).

| | A: Prompt v2 | B: Prompt v2.1 |
|---|---|---|
| First-attempt schema validity | 8/8 | 8/8 |
| Retries | 0 | 0 |
| Claim support | 21/21 | 20/20 |
| Grounded outputs | 8/8 | 8/8 |
| Abstentions (correct / incorrect / missed) | 3 / 0 / 0 | 3 / 0 / 0 |
| Completeness | 5 COMPLETE | 5 COMPLETE |
| Uncited item-specific limitations | 0 | 0 |
| Deterministic integrity failures | 0 | 0 |
| Tokens (prompt / completion) | 19,282 / 2,047 | 20,170 / 1,818 |
| Median latency | 1,744 ms | 1,765 ms |
| Estimated cost | 0.0041 USD | 0.0039 USD |

On every question the two conditions received the same human judgments. The frozen comparison rule gives **INCONCLUSIVE**: B did not raise first-attempt validity, so neither SCHEMA_AWARENESS nor FORMAT_GROUNDING_TRADEOFF can apply, and B had no cap violations. Prompt v2 remains the working prompt, and no prompt change follows from SC-1.

These are development results on 8 questions, judged only against the evidence each answer was given. They are not an estimate of general performance.
