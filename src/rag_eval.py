"""EXP-004 retrieval evaluation: question and judgment formats, pooling, the frozen
DEV/TEST split, and retrieval metrics.

Gold relevance comes only from the editor's judgments (judgments/*.jsonl, written by
ARI3 Review). Machine output is a candidate pool, never gold.

Metrics, binary relevance, over questions with at least one item judged relevant:
  Hit@K     1 if any relevant item is in the top K, else 0
  Recall@K  relevant items in the top K / all items judged relevant
  MRR       1 / rank of the first relevant item (0 if none is retrieved)
  nDCG@10   discounted cumulative gain of the top 10, over the ideal ordering
Recall is measured against the judged pool, the union of each method's top results
(TREC-style pooling, Voorhees and Harman 2005). A relevant item that no method
retrieved is never judged, so recall is relative to the pool and is not exhaustive.
"unsure" judgments count as not relevant.

Usage:
  python src/rag_eval.py pool         --questions Q.jsonl --out POOL.jsonl [--depth 10]
  python src/rag_eval.py freeze-split --questions Q.jsonl --out SPLIT.json [--n-test 20]
  python src/rag_eval.py eval-dev     --questions Q.jsonl --split SPLIT.json --judgments J.jsonl --out DIR
"""

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field

from rag_schema import Filters, SearchArgs

QUERY_TYPES = ("term", "temporal", "source_filter", "sector_filter", "multilingual", "general")
JUDGMENTS = ("relevant", "not_relevant", "unsure")
# bm25:auto uses trigrams for CJK queries and words otherwise. bm25:words is the baseline it is compared with.
POOL_METHODS = (("bm25", "words"), ("bm25", "auto"), ("dense", None), ("hybrid", "auto"))


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    question_id: str = Field(pattern=r"^q\d{3}$")
    question: str = Field(min_length=3, max_length=500)
    query: str = Field(min_length=1, max_length=500)  # the text sent to the retriever
    answerable_expected: bool  # the drafter's expectation, checked against the judgments
    language: str = Field(pattern=r"^[a-z]{2}$")
    query_type: Literal[QUERY_TYPES]
    filters: Filters = Filters()
    reference_time: str = Field(pattern=r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
    dataset_version: str
    drafted_by: str
    notes: str = ""


class Judgment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    question_id: str
    item_id: int
    url: str
    judgment: Literal[JUDGMENTS]
    labeler: str
    labeled_at: str
    pool_source: List[str]
    dataset_version: str


def load_jsonl(path, model):
    with open(path, encoding="utf-8") as f:
        return [model.model_validate_json(line) for line in f if line.strip()]


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------- metrics ----------

def hit_at(ranked, relevant, k):
    return 1.0 if set(ranked[:k]) & relevant else 0.0


def recall_at(ranked, relevant, k):
    return len(set(ranked[:k]) & relevant) / len(relevant)


def mrr(ranked, relevant):
    return next((1.0 / n for n, i in enumerate(ranked, 1) if i in relevant), 0.0)


def ndcg_at(ranked, relevant, k=10):
    dcg = sum(1.0 / math.log2(n + 1) for n, i in enumerate(ranked[:k], 1) if i in relevant)
    ideal = sum(1.0 / math.log2(n + 1) for n in range(1, min(len(relevant), k) + 1))
    return dcg / ideal


def gold(judgments, labeler=None):
    """{question_id: set of item_ids judged relevant}. The latest judgment per
    (question, item, labeler) wins."""
    latest = {}
    for j in sorted(judgments, key=lambda j: j.labeled_at):
        if labeler is None or j.labeler == labeler:
            latest[(j.question_id, j.item_id, j.labeler)] = j.judgment
    out = {}
    for (qid, item, _), value in latest.items():
        out.setdefault(qid, set())
        if value == "relevant":
            out[qid].add(item)
    return out


def score(rankings, relevant_by_q):
    """Mean metrics over questions with at least one relevant item."""
    qids = [q for q, rel in relevant_by_q.items() if rel and q in rankings]
    if not qids:
        return {"questions": 0}
    rows = [(hit_at(rankings[q], relevant_by_q[q], 5), hit_at(rankings[q], relevant_by_q[q], 10),
             recall_at(rankings[q], relevant_by_q[q], 5), recall_at(rankings[q], relevant_by_q[q], 10),
             mrr(rankings[q], relevant_by_q[q]), ndcg_at(rankings[q], relevant_by_q[q], 10)) for q in qids]
    names = ("hit@5", "hit@10", "recall@5", "recall@10", "mrr", "ndcg@10")
    return {"questions": len(qids), **{n: round(sum(r[i] for r in rows) / len(rows), 4) for i, n in enumerate(names)}}


# ---------- pooling ----------

def run_method(corpus_con, index, question, method, lexical, k):
    from rag_retrieve import search
    args = SearchArgs(query=question.query, filters=question.filters, method=method, k=k)
    return [h.evidence.item_id for h in search(corpus_con, index, args, lexical or "auto").hits]


def build_pool(corpus_con, index, questions, depth=10):
    """[{question_id, item_id, pool_source}] : the union of each method's top `depth`."""
    rows = []
    for q in questions:
        sources = {}
        for method, lexical in POOL_METHODS:
            for item_id in run_method(corpus_con, index, q, method, lexical, depth):
                sources.setdefault(item_id, []).append(f"{method}:{lexical}" if lexical else method)
        rows += [{"question_id": q.question_id, "item_id": i, "pool_source": s} for i, s in sorted(sources.items())]
    return rows


# ---------- split ----------

def stratum(q):
    temporal = q.filters.as_of is not None or q.filters.start_date is not None or q.filters.end_date is not None
    return (q.answerable_expected, temporal, q.language != "en", q.query_type)


def freeze_split(questions, questions_sha256, n_test=20, seed=4):
    """Stratified DEV/TEST assignment. Within each stratum, questions are ordered by
    SHA-256 of seed and question_id, and TEST receives its share by largest remainder."""
    strata = {}
    for q in questions:
        strata.setdefault(stratum(q), []).append(q.question_id)
    total = len(questions)
    quotas = {s: n_test * len(ids) / total for s, ids in strata.items()}
    alloc = {s: int(v) for s, v in quotas.items()}
    for s in sorted(quotas, key=lambda s: (-(quotas[s] - alloc[s]), str(s)))[:n_test - sum(alloc.values())]:
        alloc[s] += 1
    test = []
    for s, ids in strata.items():
        ordered = sorted(ids, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).hexdigest())
        test += ordered[:alloc[s]]
    test = sorted(test)
    dev = sorted(q.question_id for q in questions if q.question_id not in set(test))
    body = {"questions_sha256": questions_sha256, "seed": seed, "n_dev": len(dev), "n_test": len(test),
            "dev": dev, "test": test,
            "strata": {json.dumps(list(s)): len(ids) for s, ids in sorted(strata.items(), key=lambda x: str(x[0]))}}
    body["split_sha256"] = hashlib.sha256(json.dumps({"dev": dev, "test": test}).encode()).hexdigest()
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["pool", "freeze-split", "eval-dev"])
    ap.add_argument("--questions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split")
    ap.add_argument("--judgments")
    ap.add_argument("--depth", type=int, default=10)
    ap.add_argument("--n-test", type=int, default=20)
    ap.add_argument("--db")
    ap.add_argument("--index")
    args = ap.parse_args(argv)
    questions = load_jsonl(args.questions, Question)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.cmd == "freeze-split":
        if os.path.exists(args.out):
            print(f"{args.out} exists. A frozen split is never regenerated.", file=sys.stderr)
            return 1
        body = freeze_split(questions, sha256_file(args.questions), args.n_test)
        body["frozen_at"] = now
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(body, f, indent=1)
        print(json.dumps(body, indent=1))
        return 0

    from item_store import DEFAULT_DB
    from rag_corpus import open_corpus
    from rag_index import DEFAULT_DIR, Index
    corpus, index = open_corpus(args.db or DEFAULT_DB), Index(args.index or DEFAULT_DIR)

    if args.cmd == "pool":
        rows = build_pool(corpus, index, questions, args.depth)
        with open(args.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"{len(rows)} candidates for {len(questions)} questions -> {args.out}")
        return 0

    with open(args.split, encoding="utf-8") as f:
        split = json.load(f)
    if split["questions_sha256"] != sha256_file(args.questions):
        print("the questions file changed after the split was frozen", file=sys.stderr)
        return 1
    dev = [q for q in questions if q.question_id in set(split["dev"])]
    relevant = gold(load_jsonl(args.judgments, Judgment))
    results = {"split": "dev", "questions": len(dev), "run_at": now, "index": index.manifest, "methods": {}}
    groups = {"all": dev, "japanese": [q for q in dev if q.language == "ja" or q.filters.languages == ["ja"]],
              "non_english": [q for q in dev if q.language != "en" or (q.filters.languages or ["en"]) != ["en"]]}
    for method, lexical in POOL_METHODS:
        rankings = {q.question_id: run_method(corpus, index, q, method, lexical, 10) for q in dev}
        results["methods"][f"{method}:{lexical}" if lexical else method] = {
            g: score({q.question_id: rankings[q.question_id] for q in qs}, relevant) for g, qs in groups.items()}
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, f"dev-retrievers-{now.replace(':', '')}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results["methods"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
