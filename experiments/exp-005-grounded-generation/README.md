# EXP-005: grounded generation

**Question.** Given evidence retrieved by ARI3's frozen hybrid retriever, can a language model produce useful answers without claiming more than the supplied evidence supports?

EXP-005 does not tune retrieval. The frozen EXP-004 hybrid retriever (`experiments/exp-004-grounded-retrieval/frozen/retriever_v1.json`) is its evidence boundary. Any change to retrieval is a new retrieval version or experiment.

## Pipeline

1. Question.
2. Frozen hybrid retriever, top 10.
3. Context check. Every item exists and passes the filters and the time boundary. An empty context gives a system abstention with no model call.
4. Context serializer v1.
5. Prompt v1 and the provider.
6. Schema v1. One retry only if the output does not parse.
7. Output validation: membership, corpus, time, filters, citation presence, provenance.
8. Human review in ARI3 Review ("Answer review (EXP-005)").

Generated text is written only to files in this folder. It never enters the item store, labels, events, predictions, EXP-003A or EXP-004 gold.

## Questions used

- **Development:** the 37 EXP-004 DEV questions. They are used for prompt development and failure analysis.
- **Not used:** the 19 EXP-004 TEST questions. That set was inspected descriptively after the retrieval TEST run, so it is not a pristine test of generation.
- **Final evaluation:** a fresh generation holdout. It will be authored, reviewed by the owner and frozen before the final prompt is evaluated on it.

## Protocol v1

`protocol/protocol_v1.json` freezes:
- the provider and its settings, with the documentation check it rests on;
- the retry policy;
- the prompt (`protocol/prompt_v1.txt`), the schema and the context serializer, with fingerprints;
- both stages of deterministic validation;
- the human rubric, the metrics and their exact definitions;
- the failure taxonomy;
- fingerprints of the EXP-005 code.

Prompt v1 is not edited after any output exists. Changes become prompt v2, after failure analysis.

## Runs

- `runs/dev-batch-1/`: the first live batch, 5 DEV questions chosen by fixed rules (`batch.json`) before any output existed. It runs once. Each record keeps the retrieval, every attempt's raw output, the parsed answer, the validation result, token usage, latency and estimated cost.
- `reviews/`: the owner's review judgments, append-only.
- `runs/dev-batch-2/`: Prompt v2. One run of q013 labelled POST-TUNING REGRESSION PROBE, which never enters fresh metrics, and five fresh DEV questions that exclude every v1 question. They are chosen by the v1 rules before any output exists.

## Prompt v2

Prompt v2 (`protocol/prompt_v2.txt`, `protocol/protocol_v2.json`) changes only what the Prompt v1 failures on q013 point to:

- **No summary.** The model writes no summary. The answer is the validated claims, joined by code. A deterministic check cannot verify that a free-text summary adds no fact, so the summary was removed rather than restricted.
- **Coverage.** The model reads every item, gives each distinct relevant finding a claim, groups items that support the same finding, and cites nothing irrelevant. A claim can cite up to 10 items. Answers still have at most 4 claims.
- **Limitations.** Each limitation is `{text, supporting_item_ids}`. A limitation about a specific item must cite it and is reviewed like a claim.

The retriever, serializer, provider settings and retry policy are unchanged. Rubric v2 adds optional reviewer notes, which are qualitative only. Metrics v2 keeps the v1 grounded-answer rule, so the two versions can be compared.

## Evidence boundary (amendment 2026-10-01)

Human review judges the model only against the exact evidence packet it received. Full articles, pages behind URLs and outside knowledge are not evidence. See `AMENDMENT_2026-10-01_evidence_boundary.md`.

The original Prompt v2 review and scores are kept unchanged as the mixed-boundary record. The deck "Prompt v2 context-only adjudication v2" (`src/exp005_adjudicate.py`) re-asks the seven judgments that used outside content. The context-grounded score is computed from it separately.

`analysis/` holds findings that are not generation metrics:
- corpus sufficiency;
- source-representation options;
- schema capacity.
