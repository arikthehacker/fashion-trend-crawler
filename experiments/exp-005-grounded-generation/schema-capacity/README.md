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
