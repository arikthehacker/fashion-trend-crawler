# EXP-004: grounded retrieval over the ARI3 stored evidence corpus

**Question.** Can ARI3 answer questions about its corpus with a citation to a stored record for every claim, while keeping the temporal and provenance constraints?

EXP-004 is an experiment number, not a release. It does not imply ARI3 v0.0.4. The release roadmap is unchanged.

## What the corpus is

Each record is a headline plus the feed's summary, stored as `text_excerpt` and capped at 500 characters. The store holds no full article text. EXP-004 therefore measures retrieval and question answering over ARI3's **stored evidence**. It does not test reasoning over complete news articles, and no result from it should be described that way.

At the evaluation cutoff (items first seen by 2026-09-30 08:00 UTC), the corpus holds 7,955 items from 94 outlets. 94% of items come from editorial outlets. The social sector has no items, and the resale sector has 10. Stored language tags cover English, Japanese, Italian, French and Portuguese. 14% of items have no language tag, so a language filter excludes them.

## Status (2026-09-30)

| Step | State |
|---|---|
| Retrieval layer (`src/rag_*.py`) | Built and tested. No language model is involved |
| Evaluation index | Built with cutoff `2026-09-30T08:00:00Z`: 7,955 items, corpus fingerprint `c571670b…` |
| Questions (`questions_v1.jsonl`) | 60 drafts, written by `draft_questions.py` from the corpus inventory. They wait for the editor's review |
| Candidate pool (`pool_v1.jsonl`) | 475 question and item pairs |
| Relevance judgments | Not started. ARI3 Review has the "Evidence relevance (EXP-004)" deck |
| DEV/TEST split | Not frozen. It is frozen after the questions are reviewed and before any retriever is scored |
| Retriever comparison on DEV | Not run |
| Generation | Not started. No provider has been called |

## Files

- `draft_questions.py` writes `questions_v1.jsonl`. Every question carries `drafted_by: machine_draft` until the editor accepts or edits it. `answerable_expected` is the drafter's guess. Whether a question is answerable is decided by the judgments.
- `pool_v1.jsonl` holds the machine-generated candidates: for each question, the union of the top 5 items from each of `bm25:words`, `bm25:auto` (trigram tokens for Japanese queries, word tokens otherwise), dense and hybrid retrieval, with the methods that found each item. These are suggestions, never gold.
- `judgments/rag_relevance_v1.jsonl` is written by ARI3 Review: one line per answer (`relevant`, `not_relevant` or `unsure`), with the question, item, URL, labeler, time, pool source and dataset version. It is append-only. The latest answer per question and item counts. This file is the only source of gold relevance.

## Method decisions made before any judgment

- **Filters before ranking.** Dates, language, sector, outlet and the temporal cutoff are SQL constraints. Ranking only orders the items that pass them.
- **Temporal modes.** Publication mode admits items published by `as_of`. Replay mode also requires `first_seen_at <= as_of`. Reconstructed first-seen values (migration 0004) can be later than the true first sighting, so replay can omit evidence ARI3 had, and never admits evidence it acquired later.
- **No chunking.** Title plus excerpt has a median of 57 tokens. 997 items (12.5%) exceed the encoder's 128-token window, and the encoder sees only their first 128 tokens. DEV results will show whether those items are over-represented among dense-retrieval misses before chunking is considered.
- **Pool depth 5.** It gives 475 judgments, within the planned 400 to 600. A depth of 10 would give 899. Every item a method ranks in its top 5 is judged, so metrics at K = 5 are fully judged. At K = 10, items a method ranks 6 to 10 are judged only if another method ranked them in its top 5. Unjudged items count as not relevant, which can understate Hit@10 and Recall@10.
- **Pooled recall.** Recall is measured against the judged pool, following TREC practice (Voorhees and Harman 2005). A relevant item that no method retrieved is never judged, so recall is relative to the pool and is not exhaustive.
- **Blind judging.** The review card shows the question, its filters and the stored item. It does not show the method or the rank that produced the item.

## Next steps

1. The editor reviews `questions_v1.jsonl`, editing or rejecting drafts.
2. The DEV/TEST split (40/20, stratified) is frozen with `python src/rag_eval.py freeze-split` and committed.
3. The editor judges the pool in ARI3 Review.
4. BM25, dense and hybrid retrieval are compared on DEV only, with Japanese and other non-English questions reported separately.
5. The chosen retriever, the generation provider and its settings, prompts, metrics and thresholds are pre-registered before any generation run or TEST evaluation.
