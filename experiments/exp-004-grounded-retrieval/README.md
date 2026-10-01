# EXP-004: grounded retrieval over the ARI3 stored evidence corpus

**Closed 2026-10-01.** The final result is claim C-0010 in `CLAIM_LEDGER.md`. `CLOSED.json` lists the fingerprint of every final artifact. Any change to retrieval is a new version or a new experiment. EXP-005 uses the frozen hybrid retriever as its evidence boundary.

**Question.** Can ARI3 answer questions about its corpus with a citation to a stored record for every claim, while keeping the temporal and provenance constraints?

EXP-004 is an experiment number, not a release. It does not imply ARI3 v0.0.4. The release roadmap is unchanged.

## What the corpus is

Each record is a headline plus the feed's summary, stored as `text_excerpt` and capped at 500 characters. The store holds no full article text. EXP-004 therefore measures retrieval and question answering over ARI3's **stored evidence**. It does not test reasoning over complete news articles, and no result from it should be described that way.

The evaluation index is frozen at a first-seen cutoff of 2026-09-30 08:00 UTC: 7,955 items from 94 outlets, corpus fingerprint `c571670b…` (`data/index/exp004-v1/manifest.json`). 94% of items come from editorial outlets. The social sector has no items, and the resale sector has 10. Stored language tags cover English, Japanese, Italian, French and Portuguese. 14% of items have no language tag, so a language filter excludes them.

## Status

| Step | State |
|---|---|
| Retrieval layer (`src/rag_*.py`) | Built and tested. No language model is involved |
| Draft questions (`questions_v1.jsonl`) | 60 machine drafts, unchanged since `5d4b688` (SHA-256 `5cd3bc10…`) |
| Question review | Complete: 52 approved unchanged, 4 edited (q004, q011, q013, q017), 4 rejected (q007, q014, q059, q060). Log committed in `390f842` |
| Question freeze | **Frozen** 2026-09-30 22:35 UTC: 56 questions, SHA-256 `d1d17cb4cfe34196…`. 46 drafted answerable, 10 drafted unanswerable, 13 temporal (4 replay). Languages: en 46, ja 4, it 2, fr 2, pt 2 |
| Depth-5 pool | **Superseded before labeling** (`superseded/`). 0 judgments were ever made on it |
| Depth-10 pool (`pool_v2.jsonl`) | **Built** from the frozen questions: 819 pairs, 646 distinct items, median 15.5 per question (max 25), pool SHA-256 `b021d0eed87c3373…`. 4 questions have no eligible item (q024, q026, q027, q040) |
| Relevance judgments | **Frozen gold**: 819 judgments (318 relevant, 273 not relevant, 228 unsure), SHA-256 `bda481d2…` (`1bbab11`) |
| DEV/TEST split | **Frozen**: 37 DEV / 19 TEST, seed 4. DEV IDs SHA-256 `fc7d5a4d…`, TEST IDs `0ed719fa…`, split `62f6a892…` |
| Retriever comparison on DEV | **Run once** under the rule (`8ce1b74`) and amendment 1 (`383d3c7`): PRACTICAL_TIE_SELECTION, hybrid (`fca940d`) |
| Retriever freeze | **Frozen** hybrid, `frozen/retriever_v1.json` (`44421a5`, SHA-256 `3b55fceb…`), accepted by the owner |
| TEST | **Run once** 2026-10-01 01:44 UTC, frozen hybrid only. `results/test-retrieval-v1.json` |
| Generation | `ask_ari3` (`src/rag_answer.py`), the grounded-answer schema, deterministic validators, the provider interface, a DeepSeek adapter and the harness (`src/rag_gen_eval.py`) are built and tested with scripted providers. No live provider has been called. Live calls need `ARI3_LIVE_LLM=approved`, set by the owner |

## Files

- `draft_questions.py` wrote `questions_v1.jsonl`. `answerable_expected` is the drafter's guess. The judgments decide whether a question is answerable.
- `reviews/question_reviews_v1.jsonl`: the editor's decisions (approve, edit, reject, ambiguous, duplicate), appended by ARI3 Review. Each names the fingerprint of the draft file it reviewed. The review card never shows retrieval output.
- `frozen/questions_v1_frozen.jsonl` and `frozen/questions_v1_freeze.json`: the approved set with edits applied, its SHA-256 and counts. Written once. IDs never change, so rejected questions leave gaps.
- `frozen/split_v1.json`: DEV and TEST question IDs with fingerprints of each list. Written once.
- `pool_v2.jsonl` and `pool_v2.manifest.json`: the candidate pool with the methods that found each pair (for analysis only), plus sizes, overlap and fingerprints.
- `judgments/rag_relevance_v2.jsonl`: one line per answer, with task, dataset version, pool fingerprint, question, item, URL, judgment, labeler and time. It records nothing about methods. This file is the only source of gold relevance.
- `superseded/pool_v1_depth5.jsonl` and its status file: kept for provenance, never judged or used.

## Evaluation design, fixed before any judgment

- **Filters before ranking.** Dates, language, sector, outlet and the temporal cutoff are SQL constraints. Ranking only orders the items that pass them.
- **Temporal modes.** Publication mode admits items published by `as_of`. Replay mode also requires `first_seen_at <= as_of`. Reconstructed first-seen values can be later than the true first sighting, so replay can omit evidence ARI3 had, and never admits evidence it acquired later.
- **Candidates.** `bm25:words`, `bm25:auto` (character trigrams for Japanese queries, word tokens otherwise, so it differs from `bm25:words` only on Japanese queries), `dense` and `hybrid:auto` (reciprocal rank fusion of `bm25:auto` and `dense`).
- **Pool depth 10.** The pool is the union of every candidate's top 10, so every item a candidate ranks in its top 10 is judged, and Hit@10 and Recall@10 are fully judged. A preview over the 60 drafts gives 899 pairs (median 16.5 per question, maximum 25), 720 distinct items and 4 questions with no eligible item. BM25 and dense overlap little (Jaccard 0.12), which is why both are pooled. The real pool is built from the frozen questions and its numbers will differ.
- **Pooled recall.** Recall is measured against the judged pool (Voorhees and Harman 2005). A relevant item that no candidate retrieved is never judged, so recall is relative to the pool and is not exhaustive.
- **Unsure.** Metrics use condensed lists (Sakai 2007): an item judged `unsure` is removed from a ranking before scoring and counts neither as relevant nor as not relevant. Every result also reports the share of each top 10 that is unsure and the judged coverage of the top 10.
- **Metrics.** Hit@5, Hit@10, Recall@5, Recall@10, MRR and nDCG@10 over questions with at least one relevant item, plus query latency (median and p95). Each is reported for all questions, English and non-English, Japanese, temporal and non-temporal, drafted-answerable and drafted-unanswerable, and questions the judgments show to be answerable.
- **Failure annotation.** Each DEV miss (no relevant item in a method's top 10) is listed for human annotation with one of: vocabulary mismatch, semantic near miss, temporal mismatch, wrong sector or context, multilingual failure, overly broad query, no relevant evidence in the corpus (assigned by rule when nothing was judged relevant), other.
- **Split.** By question, stratified by drafted answerability, temporal constraint, non-English language and query type, one third to TEST, seed 4. TEST is never used to compare or tune retrievers. `eval-test` refuses to run without a retriever frozen from a DEV result, and refuses to run a second time.
- **Blind judging.** A judging card shows the question, its filters and the stored item, never the method, rank, score or number of methods that found the item.
- **No chunking.** Title plus excerpt has a median of 57 tokens. 997 items (12.5%) exceed the encoder's 128-token window. DEV results will show whether those items are over-represented among dense misses before chunking is considered.

## Retrieval result

DEV selected the retriever. TEST was run once, on the frozen hybrid retriever only. Metrics are macro averages. Hit, Recall and MRR cover questions with at least one item judged relevant. An item judged unsure keeps its rank and counts as neither relevant nor not relevant.

| Split | Questions | With a relevant item | Recall@5 | Recall@10 | Hit@5 | Hit@10 | MRR | Unsure@10 | Latency median / p95 |
|---|---|---|---|---|---|---|---|---|---|
| DEV, hybrid | 37 | 24 | 0.526 | 0.751 | 1.000 | 1.000 | 0.858 | 0.224 | 26.5 / 311.3 ms |
| TEST, hybrid | 19 | 12 | 0.438 | 0.770 | 1.000 | 1.000 | 0.958 | 0.311 | 67.4 / 344.4 ms |

On DEV, hybrid's Recall@10 exceeded dense's by 0.181 (95% interval 0.086 to 0.288) and BM25's by 0.169 (interval -0.006 to 0.352), so the practical-tie rule decided.

### Limitations

1. **Non-English retrieval is not evaluated.** Most non-English judgments are unsure (85% of non-English items on DEV, 93% on TEST), which the editor attributes largely to not reading those languages. On TEST no non-English question has a resolved relevant item. On DEV one does. Feed language tags are also unreliable: some items tagged English have Spanish or German headlines.
2. **Some filtered questions have very small candidate sets.** When a filter leaves 10 to 16 eligible items, a retriever that returns all of them reaches high recall by construction. On DEV, leaving out the four answerable questions with 12 or fewer eligible items (a check made after the results, not part of selection) narrows hybrid's lead over BM25 to 0.045 (0.702 against 0.657).
3. **Recall is pooled.** It is measured against the judged pool, the union of each candidate's top 10. A relevant item that no candidate retrieved was never judged.
4. **Recall@10 has a ceiling.** For a question with more than 10 relevant items, Recall@10 cannot exceed 10 divided by the number of relevant items. Two TEST questions (q008, q028) reached that ceiling.
5. **One drafted-unanswerable DEV question had relevant evidence.** The editor judged two items relevant for q035 (Poshmark and quiet luxury).
6. **Samples are small.** 24 DEV and 12 TEST questions carry the recall figures, and most subgroups have fewer than 10 questions.

## Generation boundary

- **Answer schema.** The model returns only `claims` (each with one or more `supporting_item_ids`), up to five short `limitations`, and `insufficient_evidence`. There is no free prose field. URLs, outlets and dates in a response come from the store.
- **Context.** At most 10 retrieved items, each excerpt capped at 500 characters. Before any call, every context item is checked against the question's filters and temporal cutoff. With no eligible evidence the provider is not called.
- **Validation.** Every cited item must be in the supplied context, exist in the store, pass every filter and the temporal cutoff, and have a URL and publication time. One retry is allowed for a schema failure. A citation failure rejects the answer and withholds its claims.
- **Provider.** `llm_provider.py` is the interface. `llm_deepseek.py` uses plain HTTP, `deepseek-flash`, temperature 0, JSON output, non-thinking mode, a 60-second timeout and at most 2 retries. The key is read from the environment only and never logged. The adapter refuses to send a request unless it was created with `allow_live=True` and `ARI3_LIVE_LLM=approved`.
- **Evaluation.** Retrieval and generation are scored separately. The harness records an audit line per question and reports schema validity, citation validity, membership violations, temporal leaks, correct refusals on unanswerable questions and false refusals on answerable ones (separately), latency, tokens and estimated cost. Correctness, completeness, usefulness and unsupported claims come from the editor's review of each answer, never from a language model judging itself.

## Next steps

1. The editor reviews the 60 drafts in ARI3 Review.
2. `python src/rag_questions.py freeze`, then `python src/rag_eval.py freeze-split` and `python src/rag_eval.py pool`, then `python src/rag_review.py make-queue`. All four outputs are committed before any judgment.
3. The editor judges the depth-10 pool in ARI3 Review.
4. `python src/rag_eval.py eval-dev` compares the candidates on DEV. The editor annotates the misses. A retriever is frozen from DEV only.
5. Generation is pre-registered before any live provider call or TEST evaluation.
