# Amendment 2026-10-01: the evidence boundary for human review

**Status:** `EVIDENCE_BOUNDARY_AMBIGUITY_DISCOVERED`. Recorded after the Prompt v2 scores (`59568e1`). No output, prompt, schema, metric formula or retrieval setting changes.

## The rule

Human semantic evaluation judges the model only against the exact evidence packet supplied to the model.

Reviewers do not use:
- the full external article;
- information available behind a URL;
- outside knowledge;
- search snippets;
- web research.

A URL inside the packet is packet text. A reviewer may read the URL string but does not open it.

## What was ambiguous

Rubric v2 asked whether a statement was supported by "the cited items" and whether "the supplied context" held enough evidence. It did not say whether an item meant the stored headline and excerpt the model received or the full source behind the item's URL. In the Prompt v2 review, several judgments used the full source:

| Task | Original judgment | Outside content used |
|---|---|---|
| q017 abstention | INCORRECT | The full article for item 278, which discusses loafers. The 417-character stored excerpt does not mention them. |
| q017 limitation 0 | NO | The reviewer's note checks the limitation against the full article for item 278. |
| q023 abstention | INCORRECT | The underlying i-D articles. The note says the stored excerpts do not mention ballet flats. |
| q031 claim 1 | SUPPORTED | The full Vogue interview with Julia Jacklin. |
| q031 completeness | PARTIAL | An outside Vogue page. |
| q031 context sufficiency | NO | An outside Vogue page. Scored as a missed abstention. |
| q013 regression, summary detail | FIXED | The Who What Wear article behind item 1363's URL. Probe only, never in fresh metrics. |

These judgments answer a mixed question: was the output right about the world the sources describe? EXP-005 asks a narrower one: did the model stay within the evidence it was given?

## What is preserved

The original review and scores are not fabricated and not invalid. They are the mixed-boundary historical record and stay unchanged:

| File | SHA-256 |
|---|---|
| `reviews/dev-batch-2_fresh_reviews.jsonl` (append-only log) | `5942e51b…` |
| `reviews/dev-batch-2_fresh_reviews_frozen_v1.jsonl` | `9d0d2c7a…` |
| `reviews/dev-batch-2_regression_reviews.jsonl` (append-only log) | `4135bc85…` |
| `reviews/dev-batch-2_regression_reviews_frozen_v1.jsonl` | `ae6e4dd7…` |
| `runs/dev-batch-2/prompt_v2_scores.json` | `b8e30e36…` |
| `runs/dev-batch-2/prompt_v2_evaluation.json` (failure assignments) | `808ce293…` |

The mixed-boundary fresh scores were:
- claim support 1.000 (10/10);
- grounded answer rate 0.60 (3/5);
- abstention 0 correct, 2 incorrect, 1 missed.

They are not the canonical context-grounded score.

## Context-only adjudication v2

The ARI3 Review deck "Prompt v2 context-only adjudication v2" re-asks only the seven judgments in the table above. Each card shows:
- the question;
- the frozen metadata;
- the generated answer or abstention;
- the evidence packet, rebuilt from the store and checked byte for byte against the record's `context_sha256`.

Each task keeps its original options. The cards show no earlier judgment and no note, because the notes quote outside sources. The deck has no link to open.

Judgments go to a separate append-only log, `reviews/dev-batch-2_context_adjudication_v2.jsonl`. It is frozen once (`src/exp005_adjudicate.py freeze`) and committed before scoring.

## Context-grounded metrics

`src/exp005_adjudicate.py score-context` writes `runs/dev-batch-2/prompt_v2_context_grounded_scores.json`. It takes the original frozen judgments, replaces the seven adjudicated ones, and applies `metrics_v2` exactly as frozen at `04ea296`. Outputs, prompt and formulas are unchanged.

The file reports both scores:
- the mixed-boundary score (from `prompt_v2_scores.json`);
- the context-grounded score, which is the canonical score for EXP-005 generation.

It also lists every judgment that changed. The original score file is not replaced.

## Separate questions

Two questions are kept apart from the generation score:
- **Corpus sufficiency.** Did the stored text keep what made a source relevant? See `analysis/corpus_sufficiency_dev-batch-2.md`. An answer limited by stored text that omits the relevant content is not a generation failure.
- **Schema capacity.** Fresh first-attempt schema validity was 2/5. See `analysis/schema_capacity_finding.md`.

Options for representing sources are listed in `analysis/source_representation_options.md`. None is adopted.
