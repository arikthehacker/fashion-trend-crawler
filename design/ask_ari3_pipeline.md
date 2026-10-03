# ask_ari3 pipeline identity

**Aligned 2026-10-03 in commit `b808419`.** Application orchestration is now aligned to the Prompt v2 pipeline evaluated on EXP-005 development data (dev-batch-2 and SC-1 condition A). Final generation holdout evaluation has not yet run. Nothing here is a claim about answer quality.

## What `ask_ari3` runs

`src/rag_answer.py` `ask_ari3(question, filters=None, *, provider=None, allow_live=False, corpus=None, index=None, retrieval_query=None)`:

1. `verify_identity()` checks every fingerprint below. Any mismatch raises `PipelineIdentityError` before retrieval or any provider call.
2. It calls the frozen `exp005_v2.answer_question`, the function that produced the evaluated outputs, unchanged:
   - frozen hybrid retrieval, top 10;
   - context check (existence, filters, time boundary);
   - serializer `exp005-context-v1`;
   - Prompt v2;
   - `AnswerV2` parse, with one retry only when the output does not parse into the schema;
   - deterministic validation of claims and cited limitations;
   - `render()`, which joins the validated claims.
3. It returns a structured result: status, abstention flag, rendered answer, validated answer, cited item metadata, validation, retrieval IDs, index cutoff, context hash, attempts, and the pipeline identity.

There is no model-written summary, no network surface, no logging and no persistence.

## Pinned identity

| Item | Value |
|---|---|
| Protocol v2 (`experiments/exp-005-grounded-generation/protocol/protocol_v2.json`) | `87e88618c83167157c7ce0102c50b9a9ca173bf82309841b3f82e3d60d2c6739` |
| Prompt v2 (`protocol/prompt_v2.txt`) | `efea461f8e079eb8c25a3e8f5acb371d5e01b9bf18c617aec123b01f62a7afce` |
| Schema v2 (`exp005-schema-v2`, `AnswerV2`) | `47b747c14b5301df9a790538205e8fdd1014019a136671e38e8d094f06c4a5ee` |
| Frozen retriever (`experiments/exp-004-grounded-retrieval/frozen/retriever_v1.json`, `exp004-retriever-v1`) | `3b55fcebbb08ec54b87198ab4a18e2f1b2bd0b922c6677428f525ceeadfd6b21` |
| Evaluated code (`exp005_v2.py`, `exp005.py`, `llm_provider.py`, `llm_deepseek.py`, `rag_validate.py`, `rag_corpus.py`) | checked file by file against `code_sha256` in protocol v2 |
| Retriever code and index files (`data/index/exp004-v1`) | checked against `code_sha256` and `index_files_sha256` in `retriever_v1.json` |
| Provider settings | must equal `provider_settings_check` in protocol v2 (`deepseek-flash`, temperature 0, top_p 1, max_tokens 1000, thinking disabled, JSON output) |

## Limits (from the frozen code)

- Context: at most 10 items, in the frozen hybrid ranking order. Each item carries `item_id`, `outlet`, `sector_group`, `published_at`, `first_seen_at` (replay mode only), `language`, `headline` (first 300 characters), `excerpt` (first 500 characters) and `url`. The serialized packet is at most 12,000 characters.
- Answer: at most 4 claims, each citing 1 to 10 item IDs. At most 3 limitations, each with text and `supporting_item_ids`. A limitation about a specific item must cite it. That rule is a human-review judgment in the evaluated pipeline; the deterministic validator checks only that cited limitations cite items in the packet.
- Abstention: `insufficient_evidence: true` with no claims. With an empty packet the provider is not called (`system_abstention`).
- Attempts: one generation, plus one retry only for a schema failure. Transport retries (at most 2) apply only when no response arrived.
- Index cutoff: items first seen before 2026-09-30 08:00 UTC (7,955 items). A refreshed index is a new retrieval version (owner decision Q32).

## Live calls

No live call happens by default:
- With no provider, or with any non-scripted provider, `ask_ari3` raises `LiveCallNotAllowed` unless the caller passes `allow_live=True`.
- With `allow_live=True`, the DeepSeek adapter still refuses unless `ARI3_LIVE_LLM=approved` is set.
- The identity check runs before any of this.

No standing public authorization exists.

## Known difference from the evaluated runs

The EXP-005 runs sent each frozen question's curated retrieval query to the retriever. `ask_ari3` sends the question text unless the caller passes `retrieval_query`. Automatic query rewriting is not part of the pipeline.

## Historical path

The EXP-004 orchestration (prompt `exp004-prompt-v1`, schema `GroundedAnswer`) was never called with a live provider. It is kept unchanged as `src/rag_answer_exp004.py` for the EXP-004 generation harness (`src/rag_gen_eval.py`) and is not reachable from `ask_ari3`.
