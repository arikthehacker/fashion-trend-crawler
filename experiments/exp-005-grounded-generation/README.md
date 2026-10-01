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
