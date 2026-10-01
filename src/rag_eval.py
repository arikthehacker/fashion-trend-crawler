"""EXP-004 retrieval evaluation: question and judgment formats, pooling, the frozen
DEV/TEST split, retrieval metrics and the run-once TEST guard.

Gold relevance comes only from the editor's judgments (judgments/*.jsonl, written by
ARI3 Review). Machine output is a candidate pool, never gold.

Pool. For every frozen question, the union of the top 10 items from each candidate
method (CANDIDATE_METHODS), so every item any candidate ranks in its top 10 is judged
(TREC-style pooling, Voorhees and Harman 2005). Recall is relative to that pool: a
relevant item no candidate retrieved is never judged.

Unsure. Judgments are relevant, not_relevant or unsure. A ranking is scored exactly as
the retriever produced it: an unsure item keeps its rank and counts as neither relevant
nor not relevant (owner correction, directive 028, replacing condensed lists). Each
result also reports the unsure share and the judged coverage of the top 10.

Metrics, over questions with at least one item judged relevant:
  Hit@K     1 if any relevant item is in the top K, else 0
  Recall@K  relevant items in the top K / all items judged relevant
  MRR       1 / rank of the first relevant item (0 if none is retrieved)
  nDCG@10   discounted cumulative gain of the top 10 over the ideal ordering

TEST is scored once, only after a retriever has been frozen from DEV results.

Usage:
  python src/rag_eval.py pool-preview              # sizes a pool over the draft questions; writes no deck
  python src/rag_eval.py pool                      # builds pool_v2 from the frozen questions
  python src/rag_eval.py freeze-split              # DEV/TEST split of the frozen questions, once
  python src/rag_eval.py freeze-gold               # the editor's final judgments for the whole pool, once
  python src/rag_select.py run-dev                 # DEV, once, under the frozen selection rule
  python src/rag_select.py freeze-retriever         # the DEV-selected retriever
  python src/rag_select.py run-test                 # once, for the frozen retriever only
"""

import argparse
import collections
import hashlib
import json
import math
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from rag_schema import Filters, SearchArgs

QUERY_TYPES = ("term", "temporal", "source_filter", "sector_filter", "multilingual", "general")
JUDGMENTS = ("relevant", "not_relevant", "unsure")
# bm25:auto uses character trigrams for CJK queries and word tokens otherwise, so it
# differs from bm25:words only on CJK queries. Both are candidates for those queries.
CANDIDATE_METHODS = (("bm25", "words"), ("bm25", "auto"), ("dense", None), ("hybrid", "auto"))
POOL_DEPTH = 10
FAILURE_CATEGORIES = ("vocabulary_mismatch", "semantic_near_miss", "temporal_mismatch", "wrong_sector_or_context",
                      "multilingual_failure", "overly_broad_query", "no_relevant_evidence_in_corpus", "other")

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(os.path.dirname(HERE), "experiments", "exp-004-grounded-retrieval")
PATHS = {
    "pool": os.path.join(EXP, "pool_v2.jsonl"),
    "pool_manifest": os.path.join(EXP, "pool_v2.manifest.json"),
    "split": os.path.join(EXP, "frozen", "split_v1.json"),
    "judgments": os.path.join(EXP, "judgments", "rag_relevance_v2.jsonl"),
    "gold": os.path.join(EXP, "frozen", "gold_relevance_v1.jsonl"),
    "gold_manifest": os.path.join(EXP, "frozen", "gold_relevance_v1.json"),
    "results": os.path.join(EXP, "results"),
    "retriever_freeze": os.path.join(EXP, "frozen", "retriever_v1.json"),
    "test_result": os.path.join(EXP, "results", "test-retrieval-v1.json"),
}


def method_name(method, lexical):
    return f"{method}:{lexical}" if lexical else method


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
    review_status: Literal["draft", "approved", "edited"] = "draft"


class Judgment(BaseModel):
    """One relevance judgment. It records nothing about which method found the item."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    task: Literal["rag_relevance"]
    dataset_version: str
    pool_sha256: str = Field(min_length=64, max_length=64)
    question_id: str
    item_id: int
    url: str
    judgment: Literal[JUDGMENTS]
    labeler: str
    judged_at: str


def load_jsonl(path, model):
    with open(path, encoding="utf-8") as f:
        return [model.model_validate_json(line) for line in f if line.strip()]


def sha256_file(path):
    """SHA-256 of a text file with line endings normalized to LF, so a Windows checkout
    (CRLF) and the committed file (LF) give the same fingerprint."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def sha256_ids(ids):
    return hashlib.sha256(json.dumps(sorted(ids)).encode()).hexdigest()


# ---------- judgments and metrics ----------

def judgments_by_question(judgments, labeler=None):
    """{question_id: {item_id: judgment}}, latest answer per (question, item, labeler)."""
    latest = {}
    for j in sorted(judgments, key=lambda j: j.judged_at):
        if labeler is None or j.labeler == labeler:
            latest[(j.question_id, j.item_id, j.labeler)] = j.judgment
    out = {}
    for (qid, item, _), value in latest.items():
        out.setdefault(qid, {})[item] = value
    return out


def gold(judgments, labeler=None):
    """{question_id: set of item_ids judged relevant}."""
    return {q: {i for i, v in items.items() if v == "relevant"}
            for q, items in judgments_by_question(judgments, labeler).items()}


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


def score(rankings, judged):
    """Mean metrics over questions with at least one relevant item, on rankings exactly as
    produced (unsure items keep their rank). rankings: {qid: [item_id, ...]}.
    judged: {qid: {item_id: judgment}}."""
    rows, unresolved, coverage = [], [], []
    for q, ranking in rankings.items():
        marks = judged.get(q, {})
        top = ranking[:10]
        if top:
            unresolved.append(sum(marks.get(i) == "unsure" for i in top) / len(top))
            coverage.append(sum(i in marks for i in top) / len(top))
        relevant = {i for i, v in marks.items() if v == "relevant"}
        if not relevant:
            continue
        rows.append((hit_at(ranking, relevant, 5), hit_at(ranking, relevant, 10),
                     recall_at(ranking, relevant, 5), recall_at(ranking, relevant, 10),
                     mrr(ranking, relevant), ndcg_at(ranking, relevant, 10)))
    names = ("hit@5", "hit@10", "recall@5", "recall@10", "mrr", "ndcg@10")
    out = {"questions_scored": len(rows), "questions_without_relevant": len(rankings) - len(rows),
           "unresolved_share_top10": round(statistics.mean(unresolved), 4) if unresolved else None,
           "judged_coverage_top10": round(statistics.mean(coverage), 4) if coverage else None}
    if rows:
        out.update({n: round(sum(r[i] for r in rows) / len(rows), 4) for i, n in enumerate(names)})
    return out


def groups(questions, judged):
    """Question subsets reported separately."""
    def non_en(q):
        return q.language != "en" or (q.filters.languages or ["en"]) != ["en"]
    return {
        "all": questions,
        "english": [q for q in questions if not non_en(q)],
        "non_english": [q for q in questions if non_en(q)],
        "japanese": [q for q in questions if q.language == "ja" or q.filters.languages == ["ja"]],
        "temporal": [q for q in questions if stratum(q)[1]],
        "not_temporal": [q for q in questions if not stratum(q)[1]],
        "answerable_expected": [q for q in questions if q.answerable_expected],
        "unanswerable_expected": [q for q in questions if not q.answerable_expected],
        "gold_answerable": [q for q in questions if any(v == "relevant" for v in judged.get(q.question_id, {}).values())],
    }


# ---------- retrieval runs and pooling ----------

def run_method(corpus_con, index, question, method, lexical, k):
    """(item_ids, seconds) for one question and one candidate method."""
    from rag_retrieve import search
    args = SearchArgs(query=question.query, filters=question.filters, method=method, k=k)
    t0 = time.perf_counter()
    ids = [h.evidence.item_id for h in search(corpus_con, index, args, lexical or "auto").hits]
    return ids, time.perf_counter() - t0


def build_pool(corpus_con, index, questions, depth=POOL_DEPTH, methods=CANDIDATE_METHODS):
    """[{question_id, item_id, pool_source}]: the union of each method's top `depth`."""
    rows = []
    for q in questions:
        sources = {}
        for method, lexical in methods:
            for item_id in run_method(corpus_con, index, q, method, lexical, depth)[0]:
                sources.setdefault(item_id, []).append(method_name(method, lexical))
        rows += [{"question_id": q.question_id, "item_id": i, "pool_source": s} for i, s in sorted(sources.items())]
    return rows


def pool_stats(rows, questions, methods=CANDIDATE_METHODS):
    per_q = collections.Counter(r["question_id"] for r in rows)
    counts = [per_q.get(q.question_id, 0) for q in questions]
    names = [method_name(m, lx) for m, lx in methods]
    found = {n: {(r["question_id"], r["item_id"]) for r in rows if n in r["pool_source"]} for n in names}
    overlap = {f"{a} & {b}": round(len(found[a] & found[b]) / max(1, len(found[a] | found[b])), 4)
               for n, a in enumerate(names) for b in names[n + 1:]}
    return {"pairs": len(rows), "unique_items": len({r["item_id"] for r in rows}),
            "questions": len(questions), "questions_with_zero_candidates": sum(c == 0 for c in counts),
            "per_question": {"min": min(counts), "median": statistics.median(counts), "max": max(counts)},
            "pairs_by_method": {n: len(found[n]) for n in names},
            "pairs_found_by_n_methods": dict(sorted(collections.Counter(len(r["pool_source"]) for r in rows).items())),
            "jaccard_overlap": overlap}


def pool_fingerprint(rows):
    body = "\n".join(json.dumps([r["question_id"], r["item_id"]]) for r in
                     sorted(rows, key=lambda r: (r["question_id"], r["item_id"])))
    return hashlib.sha256(body.encode()).hexdigest()


# ---------- frozen gold ----------

def materialize_gold(judgments, pool_rows, pool_sha256):
    """The final judgment per pooled pair (latest answer wins), sorted by question and
    item. Raises unless every pooled pair has exactly one final judgment and nothing
    outside the pool was judged."""
    if {j.pool_sha256 for j in judgments} != {pool_sha256}:
        raise RuntimeError("judgments name a different pool")
    labelers = {j.labeler for j in judgments}
    if len(labelers) != 1:
        raise RuntimeError(f"expected one labeler, found {sorted(labelers)}")
    latest = {}
    for j in sorted(judgments, key=lambda j: j.judged_at):
        key = (j.question_id, j.item_id)
        if key in latest and latest[key].judged_at == j.judged_at and latest[key].judgment != j.judgment:
            raise RuntimeError(f"conflicting answers at the same second for {key}")
        latest[key] = j
    pool = {(r["question_id"], r["item_id"]) for r in pool_rows}
    if set(latest) != pool:
        raise RuntimeError(f"{len(pool - set(latest))} pooled pairs unjudged, {len(set(latest) - pool)} judged outside the pool")
    return [latest[k] for k in sorted(latest)]


def load_gold(path=None, manifest=None):
    """{question_id: {item_id: judgment}} from the frozen gold, after its fingerprint check."""
    path, manifest = path or PATHS["gold"], manifest or PATHS["gold_manifest"]
    with open(manifest, encoding="utf-8") as f:
        body = json.load(f)
    if sha256_file(path) != body["gold_sha256"]:
        raise RuntimeError("the frozen gold no longer matches its fingerprint")
    return judgments_by_question(load_jsonl(path, Judgment)), body


# ---------- split ----------

def stratum(q):
    temporal = q.filters.as_of is not None or q.filters.start_date is not None or q.filters.end_date is not None
    return (q.answerable_expected, temporal, q.language != "en", q.query_type)


def freeze_split(questions, questions_sha256, n_test=None, seed=4):
    """Stratified DEV/TEST assignment by question. Within each stratum, questions are
    ordered by SHA-256 of seed and question_id, and TEST receives its share by largest
    remainder. The default TEST size is one third of the questions."""
    total = len(questions)
    n_test = round(total / 3) if n_test is None else n_test
    strata = {}
    for q in questions:
        strata.setdefault(stratum(q), []).append(q.question_id)
    quotas = {s: n_test * len(ids) / total for s, ids in strata.items()}
    alloc = {s: int(v) for s, v in quotas.items()}
    for s in sorted(quotas, key=lambda s: (-(quotas[s] - alloc[s]), str(s)))[:n_test - sum(alloc.values())]:
        alloc[s] += 1
    test = []
    for s, ids in strata.items():
        test += sorted(ids, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).hexdigest())[:alloc[s]]
    test = sorted(test)
    dev = sorted(q.question_id for q in questions if q.question_id not in set(test))
    return {"questions_sha256": questions_sha256, "seed": seed, "n_dev": len(dev), "n_test": len(test),
            "dev": dev, "test": test, "dev_ids_sha256": sha256_ids(dev), "test_ids_sha256": sha256_ids(test),
            "split_sha256": hashlib.sha256(json.dumps({"dev": dev, "test": test}).encode()).hexdigest(),
            "strata": {json.dumps(list(s)): len(ids) for s, ids in sorted(strata.items(), key=lambda x: str(x[0]))}}


def load_split(questions_sha256, path=PATHS["split"]):
    with open(path, encoding="utf-8") as f:
        split = json.load(f)
    if split["questions_sha256"] != questions_sha256:
        raise RuntimeError("the frozen questions changed after the split was frozen")
    if set(split["dev"]) & set(split["test"]):
        raise RuntimeError("a question is in both DEV and TEST")
    if sha256_ids(split["dev"]) != split["dev_ids_sha256"] or sha256_ids(split["test"]) != split["test_ids_sha256"]:
        raise RuntimeError("the split IDs do not match their fingerprints")
    return split


# ---------- evaluation ----------

def evaluate(corpus_con, index, questions, judged, methods=CANDIDATE_METHODS, k=10):
    """Per-method metrics by group, latency, and the worksheet of misses for human
    failure annotation. The caller decides which questions are passed in."""
    out, misses = {}, []
    for method, lexical in methods:
        name = method_name(method, lexical)
        rankings, seconds = {}, []
        for q in questions:
            rankings[q.question_id], s = run_method(corpus_con, index, q, method, lexical, k)
            seconds.append(s)
        out[name] = {g: score({q.question_id: rankings[q.question_id] for q in qs}, judged)
                     for g, qs in groups(questions, judged).items()}
        ordered = sorted(seconds)
        out[name]["latency_ms"] = {"median": round(1000 * statistics.median(ordered), 1),
                                   "p95": round(1000 * ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)], 1)}
        for q in questions:
            relevant = {i for i, v in judged.get(q.question_id, {}).items() if v == "relevant"}
            if not relevant:
                misses.append({"question_id": q.question_id, "method": name,
                               "category": "no_relevant_evidence_in_corpus", "assigned_by": "rule: no item judged relevant"})
            elif not relevant & set(rankings[q.question_id][:10]):
                misses.append({"question_id": q.question_id, "method": name, "category": None,
                               "assigned_by": None, "allowed": list(FAILURE_CATEGORIES)})
    return out, misses


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _open(args):
    from item_store import DEFAULT_DB
    from rag_corpus import open_corpus
    from rag_index import Index
    return open_corpus(args.db or DEFAULT_DB), Index(args.index)


def main(argv=None):
    import rag_questions as rq
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["pool-preview", "pool", "freeze-split", "freeze-gold", "freeze-retriever",
                                    "eval-test"])
    ap.add_argument("--db")
    ap.add_argument("--index", default=os.path.join(os.path.dirname(os.path.dirname(EXP)), "data", "index",
                                                    "exp004-v1"))
    ap.add_argument("--method")
    ap.add_argument("--dev-result")
    args = ap.parse_args(argv)

    if args.cmd == "pool-preview":
        corpus, index = _open(args)
        drafts = load_jsonl(rq.DRAFTS, Question)
        print(json.dumps({"preview_over": "draft questions (not frozen); no deck is written",
                          **pool_stats(build_pool(corpus, index, drafts), drafts)}, indent=1))
        return 0

    questions, qmanifest = rq.load_frozen()

    if args.cmd == "pool":
        if os.path.exists(PATHS["pool"]):
            print("pool_v2 exists. A pool is never rebuilt once written.", file=sys.stderr)
            return 1
        corpus, index = _open(args)
        rows = build_pool(corpus, index, questions)
        with open(PATHS["pool"], "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        body = {"built_at": _now(), "depth": POOL_DEPTH, "methods": [method_name(*m) for m in CANDIDATE_METHODS],
                "questions_sha256": qmanifest["questions_sha256"], "index": index.manifest,
                "pool_sha256": pool_fingerprint(rows), "pool_file_sha256": sha256_file(PATHS["pool"]),
                **pool_stats(rows, questions)}
        with open(PATHS["pool_manifest"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1)
        print(json.dumps(body, indent=1))
        return 0

    if args.cmd == "freeze-split":
        if os.path.exists(PATHS["split"]):
            print("the split is already frozen", file=sys.stderr)
            return 1
        body = dict(freeze_split(questions, qmanifest["questions_sha256"]), frozen_at=_now())
        with open(PATHS["split"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1)
        print(json.dumps(body, indent=1))
        return 0

    if args.cmd == "freeze-gold":
        if os.path.exists(PATHS["gold"]) or os.path.exists(PATHS["gold_manifest"]):
            print("the gold is already frozen. A change needs a new version.", file=sys.stderr)
            return 1
        with open(PATHS["pool_manifest"], encoding="utf-8") as f:
            pmanifest = json.load(f)
        if sha256_file(PATHS["pool"]) != pmanifest["pool_file_sha256"] or pmanifest["questions_sha256"] != qmanifest["questions_sha256"]:
            print("the pool does not match its manifest or the frozen questions", file=sys.stderr)
            return 1
        with open(PATHS["pool"], encoding="utf-8") as f:
            pool_rows = [json.loads(line) for line in f if line.strip()]
        judgments = load_jsonl(PATHS["judgments"], Judgment)
        gold = materialize_gold(judgments, pool_rows, pmanifest["pool_sha256"])
        with open(PATHS["gold"], "w", encoding="utf-8", newline="\n") as f:
            for j in gold:
                f.write(json.dumps(j.model_dump(mode="json"), ensure_ascii=False, sort_keys=True) + "\n")
        counts = collections.Counter(j.judgment for j in gold)
        body = {"frozen_at": _now(), "dataset_version": qmanifest["dataset_version"], "task": "rag_relevance",
                "labeler": gold[0].labeler, "judgments": len(gold), "relevant": counts["relevant"],
                "not_relevant": counts["not_relevant"], "unsure": counts["unsure"],
                "resolved": counts["relevant"] + counts["not_relevant"],
                "unsure_handling": "fixed ranks: an unsure item keeps its rank and counts as neither relevant nor "
                                   "not relevant; the unsure share of each top 10 is reported",
                "log_lines": len(judgments), "log_sha256": sha256_file(PATHS["judgments"]),
                "pairs_answered_more_than_once": sum(c > 1 for c in collections.Counter(
                    (j.question_id, j.item_id) for j in judgments).values()),
                "questions_sha256": qmanifest["questions_sha256"], "pool_sha256": pmanifest["pool_sha256"],
                "gold_sha256": sha256_file(PATHS["gold"])}
        with open(PATHS["gold_manifest"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1)
        print(json.dumps(body, indent=1))
        return 0

    split = load_split(qmanifest["questions_sha256"])
    judged, _ = load_gold()

    print("freeze-retriever and eval-test moved to rag_select.py (same scoring as DEV); nothing was run",
          file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
