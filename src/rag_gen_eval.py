"""EXP-004 generation evaluation harness. Retrieval quality is measured separately
(rag_eval.py); this harness measures grounding and answer behavior.

For each question it runs ask_ari3 and appends an audit record: question, filters,
retrieved items and scores, provider and settings, prompt and schema versions, the raw
structured output, the validation result, the public answer, tokens, latency, estimated
cost and time. Nothing is written to the evidence store.

Automatic metrics (deterministic):
  status counts; schema validity of final outputs; citation validity (valid citations /
  all citations); context-membership violations; temporal leaks; refusal behavior,
  reported separately as the correct-refusal rate on unanswerable questions and the
  false-refusal rate on answerable ones; latency median and p95; tokens and estimated cost.
Answerability comes from the editor's judgments when they exist (gold: at least one item
judged relevant). Otherwise it falls back to the drafted expectation and is labeled so.

Human metrics: the harness writes a review template with one row per answer (correctness,
completeness, usefulness on a 1 to 3 scale) and one grade per claim (supported, partial,
unsupported). Unsupported-claim counts come only from that human review, never from a
language model judging itself.

TEST runs once, and only after frozen/generation_prereg_v1.json exists.

usage:
  python src/rag_gen_eval.py run --split dev --provider refuse-all      # offline pipeline check
  python src/rag_gen_eval.py run --split dev --provider deepseek        # needs the live-call gate
  python src/rag_gen_eval.py human-summary --review FILE
"""

import argparse
import collections
import json
import math
import os
import statistics
import sys
from datetime import datetime, timezone

from rag_answer import ask_ari3
from rag_eval import EXP, PATHS, Judgment, judgments_by_question, load_jsonl, load_split
from llm_provider import ScriptedProvider

GEN_PREREG = os.path.join(EXP, "frozen", "generation_prereg_v1.json")
REFUSAL = json.dumps({"insufficient_evidence": True, "claims": [], "limitations": ["offline check: no model called"]})


class RefuseAllProvider(ScriptedProvider):
    """Always declines. Exercises the whole pipeline without a model or a network call."""
    name = "refuse-all"

    def __init__(self):
        super().__init__([], model="refuse-all-v1")

    def generate_json(self, messages):
        self.responses = [REFUSAL]
        return super().generate_json(messages)


def _pct(values, q):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)] if ordered else None


def answerability(questions, judged):
    """({qid: True/False}, source). Gold when judgments exist for every question."""
    if judged and all(q.question_id in judged for q in questions):
        return {q.question_id: any(v == "relevant" for v in judged[q.question_id].values()) for q in questions}, "gold"
    return {q.question_id: q.answerable_expected for q in questions}, "drafted_expectation_not_gold"


def metrics(records, answerable, source):
    statuses = collections.Counter(r["status"] for r in records)
    final = [r for r in records if r["validation"].get("schema_valid") is not None]
    citations = sum(r["validation"].get("citations", 0) for r in final)
    valid = sum(r["validation"].get("valid_citations", 0) for r in final)
    membership = sum(1 for r in final for v in r["validation"].get("violations", []) if v["reason"] == "not_in_context")
    leaks = sum(len(r["validation"].get("temporal_leaks", [])) for r in final)
    unans = [r for r in records if answerable.get(r["question_id"]) is False]
    ans = [r for r in records if answerable.get(r["question_id"]) is True]
    latency = [r["latency_s"] for r in records]
    usage = collections.Counter()
    for r in records:
        for a in r["attempts"]:
            usage.update({k: v for k, v in a["usage"].items() if isinstance(v, (int, float))})
    costs = [r["estimated_cost_usd"] for r in records if r["estimated_cost_usd"] is not None]
    return {
        "questions": len(records), "status_counts": dict(statuses),
        "schema_validity": round(sum(r["validation"]["schema_valid"] for r in final) / len(final), 4) if final else None,
        "citation_validity": round(valid / citations, 4) if citations else None,
        "citations": citations, "membership_violations": membership, "temporal_leaks": leaks,
        "answerability_source": source,
        "correct_refusal_rate_unanswerable": round(sum(r["status"] == "insufficient_evidence" for r in unans)
                                                   / len(unans), 4) if unans else None,
        "false_refusal_rate_answerable": round(sum(r["status"] == "insufficient_evidence" for r in ans)
                                               / len(ans), 4) if ans else None,
        "latency_s": {"median": round(statistics.median(latency), 3) if latency else None,
                      "p95": round(_pct(latency, 0.95), 3) if latency else None},
        "tokens": dict(usage), "estimated_cost_usd": {"total": round(sum(costs), 6), "per_query": round(
            sum(costs) / len(costs), 8)} if costs else None,
    }


def run(questions, provider, corpus, index, out_dir, run_id, method="hybrid", cost_fn=None, judged=None):
    """Run every question, write the audit log, metrics and the human review template."""
    os.makedirs(out_dir, exist_ok=True)
    audit_path = os.path.join(out_dir, f"{run_id}.audit.jsonl")
    records = []
    with open(audit_path, "x", encoding="utf-8", newline="\n") as audit:
        for q in questions:
            r = ask_ari3(q.question, q.filters, provider=provider, corpus=corpus, index=index, method=method,
                         retrieval_query=q.query)
            now = datetime.now(timezone.utc)
            cost = None
            if cost_fn is not None:
                parts = [cost_fn(provider.model, a["usage"], now) for a in r.debug.get("attempts", [])]
                cost = sum(p for p in parts if p is not None) if parts else 0.0
            record = {"question_id": q.question_id, "question": q.question, "retrieval_query": q.query,
                      "filters": q.filters.model_dump(mode="json", exclude_none=True),
                      "temporal_mode": q.filters.temporal_mode, "status": r.status, "message": r.message,
                      "retrieval": r.debug.get("retrieval"), "tool_calls": [],
                      "provider": r.debug.get("provider"), "prompt_version": r.debug.get("prompt_version"),
                      "schema_version": r.debug.get("schema_version"), "attempts": r.debug.get("attempts", []),
                      "validation": r.validation, "answer": r.public(), "latency_s": r.debug.get("latency_s"),
                      "estimated_cost_usd": cost, "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
            audit.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.append(record)
    answerable, source = answerability(questions, judged or {})
    body = {"run_id": run_id, "questions": len(questions), "method": method, "metrics": metrics(records, answerable,
                                                                                                source)}
    with open(os.path.join(out_dir, f"{run_id}.metrics.json"), "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    with open(os.path.join(out_dir, f"{run_id}.human_review.jsonl"), "x", encoding="utf-8", newline="\n") as f:
        for r in records:
            if r["status"] == "answered":
                f.write(json.dumps({"question_id": r["question_id"], "correctness": None, "completeness": None,
                                    "usefulness": None, "claims": [{"text": c["text"], "grade": None}
                                                                   for c in r["answer"]["claims"]],
                                    "reviewer": None, "reviewed_at": None, "notes": ""}, ensure_ascii=False) + "\n")
    return body


def human_summary(path):
    """Summarize a completed review file. Rows with missing grades are counted as unreviewed."""
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    grades = collections.Counter(c["grade"] for r in rows for c in r["claims"])
    scores = {k: [r[k] for r in rows if r[k] is not None] for k in ("correctness", "completeness", "usefulness")}
    return {"answers": len(rows), "claims": sum(grades.values()), "claim_grades": dict(grades),
            "unsupported_claims": grades.get("unsupported", 0), "unreviewed_claims": grades.get(None, 0),
            **{f"mean_{k}": round(statistics.mean(v), 3) if v else None for k, v in scores.items()}}


def main(argv=None):
    import rag_questions as rq
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["run", "human-summary"])
    ap.add_argument("--split", choices=["dev", "test"], default="dev")
    ap.add_argument("--provider", choices=["refuse-all", "deepseek"], default="refuse-all")
    ap.add_argument("--method", default="hybrid")
    ap.add_argument("--review")
    ap.add_argument("--db")
    ap.add_argument("--index", default=os.path.join(os.path.dirname(os.path.dirname(EXP)), "data", "index",
                                                    "exp004-v1"))
    args = ap.parse_args(argv)
    if args.cmd == "human-summary":
        print(json.dumps(human_summary(args.review), indent=1))
        return 0

    questions, qmanifest = rq.load_frozen()
    split = load_split(qmanifest["questions_sha256"])
    if args.split == "test":
        if not os.path.exists(GEN_PREREG):
            print("TEST needs frozen/generation_prereg_v1.json first", file=sys.stderr)
            return 1
        run_id = "test-generation-v1"
    else:
        run_id = f"dev-generation-{args.provider}-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ')}"
    chosen = [q for q in questions if q.question_id in set(split[args.split])]

    from item_store import DEFAULT_DB
    from rag_corpus import open_corpus
    from rag_index import Index
    cost_fn = None
    if args.provider == "deepseek":
        import llm_deepseek
        provider, cost_fn = llm_deepseek.DeepSeekProvider(allow_live=True), llm_deepseek.estimate_cost
    else:
        provider = RefuseAllProvider()
    judged = judgments_by_question(load_jsonl(PATHS["judgments"], Judgment)) if os.path.exists(PATHS["judgments"]) else {}
    try:
        body = run(chosen, provider, open_corpus(args.db or DEFAULT_DB), Index(args.index),
                   os.path.join(EXP, "results"), run_id, args.method, cost_fn, judged)
    except FileExistsError:
        print(f"{run_id} already exists. A run is never overwritten, and TEST runs once.", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
