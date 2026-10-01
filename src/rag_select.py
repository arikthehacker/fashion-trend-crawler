"""EXP-004 retriever selection: the pre-registered rule, the one-time DEV run, and the
mechanical application of the rule (directive 028).

The rule is written to frozen/retriever_selection_rule_v1.json by `freeze-rule` and must
be committed and pushed before `run-dev` will score anything. `run-dev` runs once.

Metric semantics (fixed before any DEV result):
  A ranking is used exactly as the retriever produced it. An item judged `unsure` keeps
  its rank. It counts as neither relevant nor not relevant, but it occupies its position.
  relevant(q) = items judged relevant for q in the frozen gold.
  Hit@k     1 if any relevant item is at rank <= k, else 0
  Recall@k  |relevant items at rank <= k| / |relevant(q)|
  MRR       1 / rank of the first relevant item, 0 if none is retrieved
  Unsure@k  unsure items at rank <= k / items retrieved at rank <= k
  Hit, Recall and MRR are computed only for questions with |relevant(q)| >= 1.
  Unsure@k is computed for every question with at least one retrieved item.
  Averages are macro: each question has equal weight.

usage:
  python src/rag_select.py freeze-rule
  python src/rag_select.py run-dev
  python src/rag_select.py freeze-retriever     # the DEV-selected configuration, bound to every fingerprint
  python src/rag_select.py run-test             # once, frozen retriever only
"""

import argparse
import json
import math
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone

from rag_eval import EXP, PATHS, load_gold, load_split, sha256_file, stratum

RULE_PATH = os.path.join(EXP, "frozen", "retriever_selection_rule_v1.json")
AMENDMENT_PATH = os.path.join(EXP, "frozen", "retriever_selection_rule_v1_amendment_1.json")
DEV_RESULT = os.path.join(EXP, "results", "dev-retrieval-v1.json")
DEV_ROWS = os.path.join(EXP, "results", "dev-retrieval-v1.per_question.jsonl")
RETRIEVER_PATH = os.path.join(EXP, "frozen", "retriever_v1.json")
TEST_RESULT = os.path.join(EXP, "results", "test-retrieval-v1.json")
TEST_ROWS = os.path.join(EXP, "results", "test-retrieval-v1.per_question.jsonl")
SRC = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC)
INDEX_DIR = os.path.join(ROOT_DIR, "data", "index", "exp004-v1")
CODE_FILES = ("rag_retrieve.py", "rag_corpus.py", "rag_index.py", "rag_schema.py", "rag_validate.py",
              "rag_eval.py", "rag_select.py", "item_store.py")
K = 10
SEED = 20261001

CANDIDATES = {
    "bm25": {"method": "bm25", "lexical": "auto",
             "note": "the production BM25: word tokens, character trigrams for CJK queries"},
    "dense": {"method": "dense", "lexical": None, "note": "frozen paraphrase-multilingual-MiniLM-L12-v2"},
    "hybrid": {"method": "hybrid", "lexical": "auto", "note": "reciprocal rank fusion (k = 60) of bm25 and dense"},
}
DESCRIPTIVE_ONLY = {"bm25_words": {"method": "bm25", "lexical": "words",
                                   "note": "word tokens only; reported for the Japanese comparison, never selectable"}}


def rule_body(gold_manifest, qmanifest, split, pool_manifest):
    return {
        "version": "exp004-retriever-selection-v1",
        "decided_by": "the owner, directive 028",
        "candidates": CANDIDATES,
        "descriptive_only": DESCRIPTIVE_ONLY,
        "k": K,
        "unsure_semantics": "fixed ranks: unsure keeps its position, counts as neither relevant nor not relevant. "
                            "Supersedes the condensed-list note in gold_relevance_v1.json and decision 0014.",
        "metrics": {"hit@k": "1 if any relevant item at rank <= k", "recall@k": "relevant at rank <= k / all relevant "
                    "in frozen gold", "mrr": "1 / rank of first relevant item, 0 if none",
                    "unsure@k": "unsure at rank <= k / items retrieved at rank <= k",
                    "averaging": "macro over questions", "recall_denominator_questions":
                    "DEV questions with >= 1 item judged relevant; others reported separately"},
        "eligibility": {"p95_latency_ms_max": 500,
                        "latency_protocol": "one untimed warm-up query per candidate, then each DEV question timed once, "
                                            "in DEV question order, wall-clock around retrieval only",
                        "integrity": ["every retrieved item exists", "every retrieved item satisfies the question's "
                                      "filters", "no retrieved item breaks the temporal cutoff (published_at, and "
                                      "first_seen_at in replay mode)", "no duplicate item in a ranking",
                                      "at most k items"]},
        "primary_metric": "macro Recall@10 on DEV questions with >= 1 resolved relevant item",
        "clear_winner": {"bootstrap_resamples": 10000, "seed": SEED, "confidence": 0.95,
                         "method": "paired by question; resample questions with replacement; mean difference; "
                                   "percentile interval",
                         "condition": "the candidate's Recall@10 difference against every other eligible candidate "
                                      "has a 95% CI lower bound > 0"},
        "practical_tie": {"recall_margin": 0.03, "hit_margin": 0.03,
                          "order": ["keep eligible candidates within 0.03 of the best macro Recall@10",
                                    "among them, keep those within 0.03 of the best Hit@10",
                                    "choose the lowest p95 latency", "then the lowest median latency"]},
        "subgroup_safeguard": {"min_answerable_questions": 3,
                               "condition": "HARD_STOP if the selected candidate has Hit@10 = 0 on a subgroup with >= 3 "
                                            "gold-answerable DEV questions while another eligible candidate has "
                                            "Hit@10 > 0 there",
                               "subgroups": "english, non_english, temporal, not_temporal, answerable_expected, "
                                            "unanswerable_expected, gold_answerable, each query_type, "
                                            "filtered_sector_or_source"},
        "outcomes": ["CLEAR_SELECTION", "PRACTICAL_TIE_SELECTION", "HARD_STOP_SUBGROUP", "HARD_STOP_OTHER"],
        "fingerprints": {"questions_sha256": qmanifest["questions_sha256"],
                         "dev_ids_sha256": split["dev_ids_sha256"], "test_ids_sha256": split["test_ids_sha256"],
                         "split_sha256": split["split_sha256"], "pool_sha256": pool_manifest["pool_sha256"],
                         "gold_sha256": gold_manifest["gold_sha256"]},
    }


# ---------- metrics ----------

def question_metrics(ranking, marks, k=K):
    """Per-question metrics on the ranking exactly as produced."""
    relevant = {i for i, v in marks.items() if v == "relevant"}
    out = {"n_relevant": len(relevant), "retrieved": len(ranking)}
    for cut in (5, 10):
        top = ranking[:cut]
        out[f"unsure@{cut}"] = (sum(marks.get(i) == "unsure" for i in top) / len(top)) if top else None
        if relevant:
            out[f"hit@{cut}"] = 1.0 if relevant & set(top) else 0.0
            out[f"recall@{cut}"] = len(relevant & set(top)) / len(relevant)
    if relevant:
        out["mrr"] = next((1.0 / n for n, i in enumerate(ranking[:k], 1) if i in relevant), 0.0)
    return out


def aggregate(rows):
    """Macro means with the number of questions behind each."""
    out = {}
    for m in ("hit@5", "hit@10", "recall@5", "recall@10", "mrr", "unsure@5", "unsure@10"):
        values = [r[m] for r in rows if r.get(m) is not None]
        out[m] = round(statistics.mean(values), 4) if values else None
        out[f"n_{m}"] = len(values)
    out["questions"] = len(rows)
    out["questions_without_relevant"] = sum(1 for r in rows if r["n_relevant"] == 0)
    return out


def subgroups(questions, judged):
    def non_en(q):
        return q.language != "en" or (q.filters.languages or ["en"]) != ["en"]
    out = {
        "all": questions,
        "english": [q for q in questions if not non_en(q)],
        "non_english": [q for q in questions if non_en(q)],
        "japanese": [q for q in questions if q.language == "ja" or q.filters.languages == ["ja"]],
        "temporal": [q for q in questions if stratum(q)[1]],
        "not_temporal": [q for q in questions if not stratum(q)[1]],
        "answerable_expected": [q for q in questions if q.answerable_expected],
        "unanswerable_expected": [q for q in questions if not q.answerable_expected],
        "gold_answerable": [q for q in questions if any(v == "relevant" for v in judged.get(q.question_id, {}).values())],
        "filtered_sector_or_source": [q for q in questions if q.filters.sectors or q.filters.coarse_groups
                                      or q.filters.outlets],
    }
    for t in sorted({q.query_type for q in questions}):
        out[f"type:{t}"] = [q for q in questions if q.query_type == t]
    return out


def unsure_breakdown(questions, judged, item_lang):
    """Amendment 1, descriptive only: the unsure share of the gold judgments for the given
    questions, by question language, item language, English or not, and language match.
    item_lang: {item_id: two-letter code or None}."""
    cells = {"question_language": {}, "item_language": {}, "item_english_vs_non_english": {},
             "question_item_language_match": {}}

    def add(table, key, unsure):
        n, u = table.get(key, (0, 0))
        table[key] = (n + 1, u + unsure)

    for q in questions:
        for item, value in judged.get(q.question_id, {}).items():
            unsure = int(value == "unsure")
            lang = item_lang.get(item)
            add(cells["question_language"], q.language, unsure)
            add(cells["item_language"], lang or "unknown", unsure)
            add(cells["item_english_vs_non_english"], "unknown" if lang is None else "en" if lang == "en" else "non-en",
                unsure)
            add(cells["question_item_language_match"], "unknown" if lang is None else
                "match" if lang == q.language else "mismatch", unsure)
    return {name: {k: {"judgments": n, "unsure": u, "unsure_rate": round(u / n, 4)}
                   for k, (n, u) in sorted(table.items())} for name, table in cells.items()}


# ---------- bootstrap and the rule ----------

def paired_bootstrap(a, b, resamples=10000, seed=SEED):
    """Mean of a - b (paired by question) with a 95% percentile interval."""
    import numpy as np
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(resamples, len(d)))
    means = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"mean_difference": round(float(d.mean()), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "questions": len(d)}


def apply_rule(summary, recall_by_q, rule, subgroup_hits):
    """Mechanical application of the frozen rule. Returns the outcome dict."""
    eligible = [c for c, s in summary.items()
                if s["eligible"]["latency_ok"] and s["eligible"]["integrity_ok"]]
    if not eligible:
        return {"outcome": "HARD_STOP_OTHER", "reason": "no eligible candidate", "eligible": eligible}
    pairs = {}
    for a in eligible:
        for b in eligible:
            if a != b:
                pairs[f"{a} - {b}"] = paired_bootstrap(recall_by_q[a], recall_by_q[b],
                                                       rule["clear_winner"]["bootstrap_resamples"],
                                                       rule["clear_winner"]["seed"])
    clear = [a for a in eligible if all(pairs[f"{a} - {b}"]["ci95"][0] > 0 for b in eligible if b != a)]
    if len(clear) == 1:
        selected, outcome, path = clear[0], "CLEAR_SELECTION", "clear winner"
    elif len(clear) > 1:
        return {"outcome": "HARD_STOP_OTHER", "reason": "more than one clear winner", "pairs": pairs}
    else:
        pt = rule["practical_tie"]
        best_r = max(summary[c]["all"]["recall@10"] for c in eligible)
        tie = [c for c in eligible if summary[c]["all"]["recall@10"] >= best_r - pt["recall_margin"] - 1e-12]
        best_h = max(summary[c]["all"]["hit@10"] for c in tie)
        tie = [c for c in tie if summary[c]["all"]["hit@10"] >= best_h - pt["hit_margin"] - 1e-12]
        tie.sort(key=lambda c: (summary[c]["latency_ms"]["p95"], summary[c]["latency_ms"]["median"]))
        if len(tie) > 1 and (summary[tie[0]]["latency_ms"]["p95"], summary[tie[0]]["latency_ms"]["median"]) == \
                (summary[tie[1]]["latency_ms"]["p95"], summary[tie[1]]["latency_ms"]["median"]):
            return {"outcome": "HARD_STOP_OTHER", "reason": "practical tie not broken by latency", "pairs": pairs}
        selected, outcome, path = tie[0], "PRACTICAL_TIE_SELECTION", f"practical-tie set after margins: {tie}"
    failures = []
    minimum = rule["subgroup_safeguard"]["min_answerable_questions"]
    for g, info in subgroup_hits.items():
        if info["n_answerable"] >= minimum and info["hit@10"][selected] == 0 and \
                any(info["hit@10"][c] > 0 for c in eligible if c != selected):
            failures.append(g)
    if failures:
        return {"outcome": "HARD_STOP_SUBGROUP", "candidate": selected, "subgroups": failures, "pairs": pairs}
    return {"outcome": outcome, "selected": selected, "path": path, "eligible": eligible, "pairs": pairs}


# ---------- the one-time DEV run ----------

def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def rule_is_committed_and_pushed(path=RULE_PATH):
    """(True, commit) when the file is committed, unchanged and on a remote branch."""
    rel = os.path.relpath(path, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace(os.sep, "/")
    if _git("ls-files", "--error-unmatch", rel).returncode != 0:
        return False, "the rule file is not committed"
    if _git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        return False, "the rule file has uncommitted changes"
    commit = _git("log", "-1", "--format=%H", "--", rel).stdout.strip()
    if _git("branch", "-r", "--contains", commit).stdout.strip() == "":
        return False, "the commit that adds the rule is not on any remote branch"
    return True, commit


def integrity(corpus, question, ranking):
    from rag_validate import check_items
    problems = check_items(corpus, ranking, question.filters)
    return {"bad_items": problems, "duplicates": len(ranking) != len(set(ranking)), "too_many": len(ranking) > K}


def run_dev():
    import rag_questions as rq
    from item_store import DEFAULT_DB
    from rag_corpus import open_corpus
    from rag_index import Index
    from rag_eval import run_method

    if os.path.exists(DEV_RESULT) or os.path.exists(DEV_ROWS):
        raise RuntimeError("DEV has already been scored under rule v1. It runs once.")
    ok, commit = rule_is_committed_and_pushed()
    if not ok:
        raise RuntimeError(commit)
    ok, amendment_commit = rule_is_committed_and_pushed(AMENDMENT_PATH)
    if not ok:
        raise RuntimeError(f"amendment 1: {amendment_commit}")
    with open(AMENDMENT_PATH, encoding="utf-8") as f:
        amendment = json.load(f)
    if amendment["amends_sha256"] != sha256_file(RULE_PATH):
        raise RuntimeError("amendment 1 names a different rule file")
    with open(RULE_PATH, encoding="utf-8") as f:
        rule = json.load(f)
    questions, qmanifest = rq.load_frozen()
    split = load_split(qmanifest["questions_sha256"])
    judged, gmanifest = load_gold()
    with open(PATHS["pool_manifest"], encoding="utf-8") as f:
        pmanifest = json.load(f)
    expected = rule["fingerprints"]
    actual = {"questions_sha256": qmanifest["questions_sha256"], "dev_ids_sha256": split["dev_ids_sha256"],
              "test_ids_sha256": split["test_ids_sha256"], "split_sha256": split["split_sha256"],
              "pool_sha256": pmanifest["pool_sha256"], "gold_sha256": gmanifest["gold_sha256"]}
    if expected != actual:
        raise RuntimeError(f"fingerprints differ from the rule: {expected} vs {actual}")
    dev = [q for q in questions if q.question_id in set(split["dev"])]  # TEST questions are never loaded below
    corpus = open_corpus(DEFAULT_DB)
    index = Index(os.path.join(os.path.dirname(os.path.dirname(EXP)), "data", "index", "exp004-v1"))

    configs = dict(CANDIDATES, **DESCRIPTIVE_ONLY)
    rows, summary = [], {}
    for name, cfg in configs.items():
        run_method(corpus, index, dev[0], cfg["method"], cfg["lexical"], K)  # untimed warm-up
        seconds, per_q, bad = [], {}, []
        for q in dev:
            ranking, s = run_method(corpus, index, q, cfg["method"], cfg["lexical"], K)
            seconds.append(s)
            check = integrity(corpus, q, ranking)
            if check["bad_items"] or check["duplicates"] or check["too_many"]:
                bad.append({"question_id": q.question_id, **{k: v for k, v in check.items() if v}})
            m = question_metrics(ranking, judged.get(q.question_id, {}))
            per_q[q.question_id] = m
            rows.append({"candidate": name, "question_id": q.question_id, "ranking": ranking,
                         "judgments": [judged.get(q.question_id, {}).get(i, "unjudged") for i in ranking], **m})
        ordered = sorted(seconds)
        latency = {"median": round(1000 * statistics.median(ordered), 1),
                   "p95": round(1000 * ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)], 1)}
        groups = {g: aggregate([per_q[q.question_id] for q in qs]) for g, qs in subgroups(dev, judged).items()}
        summary[name] = {**groups, "latency_ms": latency, "integrity_failures": bad,
                         "eligible": {"latency_ok": latency["p95"] <= rule["eligibility"]["p95_latency_ms_max"],
                                      "integrity_ok": not bad, "selectable": name in CANDIDATES}}

    answerable = [q.question_id for q in dev if any(v == "relevant" for v in judged.get(q.question_id, {}).values())]
    recall_by_q = {c: [next(r["recall@10"] for r in rows if r["candidate"] == c and r["question_id"] == qid)
                       for qid in answerable] for c in CANDIDATES}
    subgroup_hits = {}
    for g, qs in subgroups(dev, judged).items():
        ids = {q.question_id for q in qs} & set(answerable)
        subgroup_hits[g] = {"n_answerable": len(ids), "hit@10": {
            c: (statistics.mean(r["hit@10"] for r in rows if r["candidate"] == c and r["question_id"] in ids)
                if ids else None)
            for c in CANDIDATES}}
    from rag_corpus import get_items
    dev_items = {i for q in dev for i in judged.get(q.question_id, {})}
    item_lang = {e.item_id: e.lang for e in get_items(corpus, sorted(dev_items))}
    unsure_rates = unsure_breakdown(dev, judged, item_lang)
    selectable = {c: summary[c] for c in CANDIDATES}
    outcome = apply_rule(selectable, recall_by_q, rule, subgroup_hits)

    os.makedirs(os.path.dirname(DEV_RESULT), exist_ok=True)
    with open(DEV_ROWS, "x", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    body = {"run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "split": "dev",
            "dev_questions": len(dev), "gold_answerable_dev_questions": len(answerable),
            "rule_sha256": sha256_file(RULE_PATH), "rule_commit": commit,
            "amendment_sha256": sha256_file(AMENDMENT_PATH), "amendment_commit": amendment_commit,
            "unsure_rate_by_language_descriptive": unsure_rates, "fingerprints": actual,
            "index": index.manifest, "summary": summary, "subgroup_hit10_for_safeguard": subgroup_hits,
            "selection": outcome, "per_question_file": os.path.basename(DEV_ROWS),
            "per_question_sha256": sha256_file(DEV_ROWS)}
    with open(DEV_RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


# ---------- the frozen retriever and the one-time TEST run ----------

def _sha256_bytes(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def current_fingerprints():
    import rag_questions as rq
    _, qmanifest = rq.load_frozen()
    split = load_split(qmanifest["questions_sha256"])
    _, gmanifest = load_gold()
    with open(PATHS["pool_manifest"], encoding="utf-8") as f:
        pmanifest = json.load(f)
    return {"questions_sha256": qmanifest["questions_sha256"], "dev_ids_sha256": split["dev_ids_sha256"],
            "test_ids_sha256": split["test_ids_sha256"], "split_sha256": split["split_sha256"],
            "pool_sha256": pmanifest["pool_sha256"], "gold_sha256": gmanifest["gold_sha256"],
            "selection_rule_sha256": sha256_file(RULE_PATH), "amendment_1_sha256": sha256_file(AMENDMENT_PATH),
            "dev_result_sha256": sha256_file(DEV_RESULT), "dev_per_question_sha256": sha256_file(DEV_ROWS)}


def code_and_index_fingerprints():
    code = {f: sha256_file(os.path.join(SRC, f)) for f in CODE_FILES}
    index = {f: _sha256_bytes(os.path.join(INDEX_DIR, f)) for f in ("fts.db", "embeddings.npz", "manifest.json")}
    return code, index


def retriever_config():
    """Everything needed to reproduce the DEV-selected hybrid retriever."""
    import sqlite3
    import rag_retrieve
    from rag_index import EMBEDDER, EMBEDDER_REVISION
    with open(os.path.join(INDEX_DIR, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    versions = {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version}
    for mod in ("numpy", "pydantic", "sentence_transformers", "transformers", "torch"):
        try:
            versions[mod] = getattr(__import__(mod), "__version__", None) or getattr(__import__(mod), "VERSION")
        except ImportError:
            versions[mod] = None
    return {
        "name": "hybrid", "selected_by": "PRACTICAL_TIE_SELECTION under retriever_selection_rule_v1 (owner accepted, "
                                         "directive 029)",
        "call": {"method": "hybrid", "lexical": "auto", "k": K},
        "query_preprocessing": "none beyond tokenization: the question's retrieval query is used as written",
        "filters": "dates, language (primary subtag of the item tag), sector as of the publication day, sector group "
                   "and outlet are SQL constraints applied before ranking; syndicated copies excluded",
        "temporal_semantics": "publication: published_at <= as_of (a bare date means 23:59:59Z). replay: also "
                              "first_seen_at <= as_of",
        "candidate_set": "items passing every filter AND present in the frozen index",
        "bm25": {"engine": "SQLite FTS5 bm25(), score = -bm25", "tables": manifest["lexical_tokenizers"],
                 "mode": "auto: trigram table when the query contains a CJK character (regex "
                         f"{rag_retrieve.CJK.pattern!r}), word table otherwise",
                 "query": "lowercased \\w+ tokens; words mode keeps tokens of 2+ characters; trigram mode uses every "
                          "3-character substring of tokens of 3+ characters; each term quoted, joined with OR",
                 "depth": f"max(k, {rag_retrieve.FUSION_DEPTH})"},
        "dense": {"encoder": EMBEDDER, "revision": EMBEDDER_REVISION, "max_seq_length": 128,
                  "text": manifest["text"], "normalization": "L2-normalized embeddings (normalize_embeddings=True)",
                  "similarity": "dot product of normalized vectors, brute force",
                  "depth": f"max(k, {rag_retrieve.FUSION_DEPTH})"},
        "fusion": {"type": "reciprocal rank fusion", "rrf_k": rag_retrieve.RRF_K,
                   "fusion_depth": rag_retrieve.FUSION_DEPTH, "score": "sum of 1 / (rrf_k + rank) over bm25 and dense",
                   "tie_break": "item_id ascending"},
        "index": {"path": "data/index/exp004-v1", "index_version": manifest["index_version"],
                  "cutoff_first_seen_at": manifest["cutoff_first_seen_at"], "items": manifest["items"],
                  "corpus_fingerprint": manifest["corpus_fingerprint"], "built_at": manifest["built_at"],
                  "chunking": manifest["chunking"]},
        "dependency_versions": versions,
    }


def freeze_retriever():
    if os.path.exists(RETRIEVER_PATH):
        raise RuntimeError("the retriever is already frozen")
    with open(DEV_RESULT, encoding="utf-8") as f:
        dev = json.load(f)
    if dev["selection"]["outcome"] not in ("CLEAR_SELECTION", "PRACTICAL_TIE_SELECTION") or \
            dev["selection"]["selected"] != "hybrid":
        raise RuntimeError("the DEV result does not select hybrid")
    code, index = code_and_index_fingerprints()
    head = _git("rev-parse", "HEAD").stdout.strip()
    body = {"version": "exp004-retriever-v1", "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "configuration": retriever_config(), "dev_selection": dev["selection"]["outcome"],
            "dev_recall@10": dev["summary"]["hybrid"]["all"]["recall@10"], "code_commit": head,
            "code_sha256": code, "index_files_sha256": index, "fingerprints": current_fingerprints()}
    with open(RETRIEVER_PATH, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def run_test():
    import rag_questions as rq
    from item_store import DEFAULT_DB
    from rag_corpus import get_items, open_corpus
    from rag_eval import run_method
    from rag_index import Index

    if os.path.exists(TEST_RESULT) or os.path.exists(TEST_ROWS):
        raise RuntimeError("TEST has already been scored. It runs once.")
    ok, freeze_commit = rule_is_committed_and_pushed(RETRIEVER_PATH)
    if not ok:
        raise RuntimeError(f"frozen retriever: {freeze_commit}")
    with open(RETRIEVER_PATH, encoding="utf-8") as f:
        frozen = json.load(f)
    if frozen["fingerprints"] != current_fingerprints():
        raise RuntimeError("a frozen artifact changed after the retriever was frozen")
    code, index_files = code_and_index_fingerprints()
    if code != frozen["code_sha256"] or index_files != frozen["index_files_sha256"]:
        raise RuntimeError("retrieval code or index files changed after the retriever was frozen")
    with open(RULE_PATH, encoding="utf-8") as f:
        rule = json.load(f)
    questions, qmanifest = rq.load_frozen()
    split = load_split(qmanifest["questions_sha256"])
    judged, _ = load_gold()
    test = [q for q in questions if q.question_id in set(split["test"])]
    corpus = open_corpus(DEFAULT_DB)
    index = Index(INDEX_DIR)
    call = frozen["configuration"]["call"]

    run_method(corpus, index, test[0], call["method"], call["lexical"], call["k"])  # untimed warm-up, as on DEV
    rows, per_q, seconds, bad = [], {}, [], []
    for q in test:
        ranking, sec = run_method(corpus, index, q, call["method"], call["lexical"], call["k"])
        seconds.append(sec)
        check = integrity(corpus, q, ranking)
        if check["bad_items"] or check["duplicates"] or check["too_many"]:
            bad.append({"question_id": q.question_id, **{k: v for k, v in check.items() if v}})
        m = question_metrics(ranking, judged.get(q.question_id, {}))
        per_q[q.question_id] = m
        rows.append({"candidate": "hybrid", "question_id": q.question_id, "ranking": ranking,
                     "judgments": [judged.get(q.question_id, {}).get(i, "unjudged") for i in ranking], **m})
    ordered = sorted(seconds)
    latency = {"median": round(1000 * statistics.median(ordered), 1),
               "p95": round(1000 * ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)], 1), "queries": len(ordered)}
    groups = {g: aggregate([per_q[q.question_id] for q in qs]) for g, qs in subgroups(test, judged).items()}
    test_items = {i for q in test for i in judged.get(q.question_id, {})}
    item_lang = {e.item_id: e.lang for e in get_items(corpus, sorted(test_items))}

    os.makedirs(os.path.dirname(TEST_RESULT), exist_ok=True)
    with open(TEST_ROWS, "x", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    body = {"run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "split": "test",
            "retriever": "hybrid", "retriever_freeze_commit": freeze_commit,
            "retriever_sha256": sha256_file(RETRIEVER_PATH), "test_questions": len(test),
            "gold_answerable_test_questions": sum(1 for q in test if any(
                v == "relevant" for v in judged.get(q.question_id, {}).values())),
            "metrics": groups, "latency_ms": latency, "integrity_failures": bad,
            "unsure_rate_by_language_descriptive": unsure_breakdown(test, judged, item_lang),
            "eligibility_reference": {"p95_latency_ms_max": rule["eligibility"]["p95_latency_ms_max"]},
            "fingerprints": frozen["fingerprints"], "per_question_file": os.path.basename(TEST_ROWS),
            "per_question_sha256": sha256_file(TEST_ROWS)}
    with open(TEST_RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def main(argv=None):
    import rag_questions as rq
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-rule", "run-dev", "freeze-retriever", "run-test"])
    args = ap.parse_args(argv)
    if args.cmd == "freeze-rule":
        if os.path.exists(RULE_PATH):
            print("the selection rule is already frozen", file=sys.stderr)
            return 1
        _, qmanifest = rq.load_frozen()
        split = load_split(qmanifest["questions_sha256"])
        _, gmanifest = load_gold()
        with open(PATHS["pool_manifest"], encoding="utf-8") as f:
            pmanifest = json.load(f)
        body = dict(rule_body(gmanifest, qmanifest, split, pmanifest),
                    frozen_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        with open(RULE_PATH, "x", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1)
        print(json.dumps({"rule": os.path.basename(RULE_PATH), "sha256": sha256_file(RULE_PATH)}, indent=1))
        return 0
    try:
        if args.cmd == "freeze-retriever":
            body = freeze_retriever()
            print(json.dumps({"retriever": os.path.basename(RETRIEVER_PATH), "sha256": sha256_file(RETRIEVER_PATH)},
                             indent=1))
            return 0
        if args.cmd == "run-test":
            body = run_test()
            print(json.dumps({"all": body["metrics"]["all"], "latency_ms": body["latency_ms"],
                              "integrity_failures": body["integrity_failures"]}, indent=1))
            return 0
        body = run_dev()
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body["selection"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
