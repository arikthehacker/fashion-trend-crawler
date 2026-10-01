"""EXP-005 human review: the generation-review queue for ARI3 Review, the append-only
review log, and the protocol v1 metrics computed from them.

Tasks (protocol v1, human rubric):
  claim_support         summary and each claim of an answer that passed validation:
                        SUPPORTED / UNSUPPORTED / UNSURE, shown with the cited items only
  answer_completeness   answered questions: COMPLETE / PARTIAL / INSUFFICIENT / UNSURE,
                        shown with the answer and the whole supplied context
  context_sufficiency   answered questions: does the context hold enough evidence? YES / NO / UNSURE
  limitations           answers with limitations: do they add an uncited fact? NO / YES / UNSURE
  abstention            model abstentions: CORRECT / INCORRECT / UNSURE, shown with the context
Rejected outputs and system abstentions have no human task. UNSURE is never counted as
unsupported or incorrect.

usage: python src/exp005_review.py make-queue
       python src/exp005_review.py metrics
"""

import argparse
import json
import os
import sys

from item_store import ROOT, utc_now
import label_tool

EXP = os.path.join(ROOT, "experiments", "exp-005-grounded-generation")
OUTPUTS = os.path.join(EXP, "runs", "dev-batch-1", "outputs.jsonl")
REVIEWS = os.path.join(EXP, "reviews", "dev-batch-1_reviews.jsonl")
QUEUE_NAME = "exp005_dev_batch_1"
OPTIONS = {
    "claim_support": [("s", "Supported", "SUPPORTED"), ("x", "Unsupported", "UNSUPPORTED"), ("u", "Unsure", "UNSURE")],
    "answer_completeness": [("c", "Complete", "COMPLETE"), ("p", "Partial", "PARTIAL"),
                            ("i", "Insufficient", "INSUFFICIENT"), ("u", "Unsure", "UNSURE")],
    "context_sufficiency": [("y", "Yes, enough evidence", "YES"), ("n", "No", "NO"), ("u", "Unsure", "UNSURE")],
    "limitations": [("n", "No uncited fact", "NO"), ("y", "Adds an uncited fact", "YES"), ("u", "Unsure", "UNSURE")],
    "abstention": [("c", "Correct abstention", "CORRECT"), ("i", "Incorrect abstention", "INCORRECT"),
                   ("u", "Unsure", "UNSURE")],
}
PROMPTS = {
    "claim_support": "Do the cited items support this statement as written?",
    "answer_completeness": "Does the answer capture the important evidence in the supplied context?",
    "context_sufficiency": "Does the supplied context hold enough evidence to answer the question?",
    "limitations": "Do the limitations add a factual claim that no item supports?",
    "abstention": "The system said the evidence is insufficient. Is that correct for this context?",
}


def load_records(path=OUTPUTS):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _item_text(e, n=None):
    head = f"[{n}] " if n is not None else ""
    return (f"{head}item {e.item_id}  |  {e.outlet}  |  {e.published_at[:10]}  |  {e.lang or 'unknown'}\n"
            f"{e.title or '(no headline)'}\n{(e.excerpt or '').strip()}\n")


def build_tasks(records, corpus):
    from rag_corpus import get_items
    tasks = []
    for r in records:
        if r["status"] not in ("answered", "model_abstention"):
            continue
        ids = r["retrieval"]["item_ids"]
        ev = {e.item_id: e for e in get_items(corpus, ids)}
        context = "SUPPLIED CONTEXT (frozen ranking order)\n\n" + "\n".join(_item_text(ev[i], n) for n, i in
                                                                           enumerate(ids, 1))
        head = {"question_id": r["question_id"], "question": r["question"]}
        a = r["answer"]
        if r["status"] == "model_abstention":
            lim = "\n".join(f"- {x}" for x in a["limitations"]) or "(none given)"
            tasks.append({**head, "task_id": f"{r['question_id']}:abstention", "kind": "abstention",
                          "target": "answer", "body": f"MODEL'S STATED LIMITATIONS\n{lim}\n\n{context}"})
            continue
        statements = [("summary", a["answer_summary"])] + [(f"claim {n}", c) for n, c in enumerate(a["claims"])]
        for target, c in statements:
            cited = "\n".join(_item_text(ev[i]) for i in c["supporting_item_ids"] if i in ev)
            tasks.append({**head, "task_id": f"{r['question_id']}:{target}", "kind": "claim_support",
                          "target": target, "statement": c["text"],
                          "body": f"STATEMENT ({target})\n{c['text']}\n\nCITED EVIDENCE\n\n{cited}"})
        answer_text = f"SUMMARY\n{a['answer_summary']['text']}\n\nCLAIMS\n" + \
            "\n".join(f"{n}. {c['text']}  (items {', '.join(map(str, c['supporting_item_ids']))})"
                      for n, c in enumerate(a["claims"]))
        tasks.append({**head, "task_id": f"{r['question_id']}:completeness", "kind": "answer_completeness",
                      "target": "answer", "body": f"{answer_text}\n\n{context}"})
        tasks.append({**head, "task_id": f"{r['question_id']}:sufficiency", "kind": "context_sufficiency",
                      "target": "answer", "body": context})
        if a["limitations"]:
            lim = "\n".join(f"- {x}" for x in a["limitations"])
            tasks.append({**head, "task_id": f"{r['question_id']}:limitations", "kind": "limitations",
                          "target": "answer", "body": f"LIMITATIONS\n{lim}\n\n{context}"})
    for t in tasks:
        t["prompt"] = PROMPTS[t["kind"]]
        t["options"] = [{"key": k, "label": label, "value": v} for k, label, v in OPTIONS[t["kind"]]]
    return tasks


def make_queue(corpus, outputs=OUTPUTS, reviews=REVIEWS):
    from rag_eval import sha256_file
    tasks = build_tasks(load_records(outputs), corpus)
    queue = {"kind": "gen_review", "task": "exp005_generation_review", "title": "Answer review (EXP-005)",
             "outputs_sha256": sha256_file(outputs), "reviews_path": os.path.relpath(reviews, ROOT).replace(os.sep, "/"),
             "tasks": tasks, "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue)


def reviews_file(queue):
    return os.path.join(ROOT, queue["reviews_path"])


def load_reviews(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def latest(reviews):
    out = {}
    for r in sorted(reviews, key=lambda r: r["reviewed_at"]):
        out[r["task_id"]] = r
    return out


def done(queue, reviewer="ariella"):
    return {t for t, r in latest(load_reviews(reviews_file(queue))).items() if r["reviewer"] == reviewer}


def record(queue, task, value, reviewer="ariella"):
    allowed = {o["value"] for o in task["options"]}
    if value not in allowed:
        raise ValueError(f"{value!r} is not one of {sorted(allowed)}")
    row = {"task_id": task["task_id"], "question_id": task["question_id"], "kind": task["kind"],
           "target": task["target"], "value": value, "reviewer": reviewer, "reviewed_at": utc_now(),
           "outputs_sha256": queue["outputs_sha256"]}
    path = reviews_file(queue)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def metrics(records, reviews):
    """Protocol v1 metrics, exactly as frozen in protocol_v1.json."""
    rv = {k: r["value"] for k, r in latest(reviews).items()}
    claims = [v for k, v in rv.items() if k.split(":")[1].startswith(("summary", "claim"))]
    sup, uns, unsure = claims.count("SUPPORTED"), claims.count("UNSUPPORTED"), claims.count("UNSURE")
    model_outputs = [r for r in records if r["status"] in ("answered", "model_abstention", "rejected_schema",
                                                           "rejected_citation")]
    evaluable, grounded = 0, 0
    correct = incorrect = missed = 0
    for r in model_outputs:
        q = r["question_id"]
        if r["status"].startswith("rejected"):
            evaluable += 1
            continue
        if r["status"] == "model_abstention":
            v = rv.get(f"{q}:abstention")
            if v in (None, "UNSURE"):
                continue
            evaluable += 1
            correct += v == "CORRECT"
            incorrect += v == "INCORRECT"
            grounded += v == "CORRECT"
            continue
        suff = rv.get(f"{q}:sufficiency")
        if suff in (None, "UNSURE"):
            continue
        evaluable += 1
        missed += suff == "NO"
        own = [v for k, v in rv.items() if k.startswith(f"{q}:") and k.split(":")[1].startswith(("summary", "claim"))]
        ok = "UNSUPPORTED" not in own and not (rv.get(f"{q}:completeness") == "INSUFFICIENT" and suff == "YES")
        grounded += ok
    return {
        "claim_support_precision": round(sup / (sup + uns), 4) if sup + uns else None,
        "claims_reviewed": len(claims), "supported": sup, "unsupported": uns, "claims_unsure": unsure,
        "grounded_answer_rate": round(grounded / evaluable, 4) if evaluable else None,
        "grounded": grounded, "evaluable_outputs": evaluable,
        "system_abstentions": sum(r["status"] == "system_abstention" for r in records),
        "abstention": {"correct": correct, "incorrect": incorrect, "missed": missed,
                       "precision": round(correct / (correct + incorrect), 4) if correct + incorrect else None,
                       "recall": round(correct / (correct + missed), 4) if correct + missed else None},
        "completeness": {v: sum(1 for k, x in rv.items() if k.endswith(":completeness") and x == v)
                         for v in ("COMPLETE", "PARTIAL", "INSUFFICIENT", "UNSURE")},
        "limitations_with_uncited_fact": sum(1 for k, x in rv.items() if k.endswith(":limitations") and x == "YES"),
        "human_unsure_rate": round(sum(x == "UNSURE" for x in rv.values()) / len(rv), 4) if rv else None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make-queue", "metrics"])
    args = ap.parse_args(argv)
    from rag_corpus import open_corpus
    if args.cmd == "make-queue":
        path = make_queue(open_corpus())
        with open(path, encoding="utf-8") as f:
            print(f"Wrote {len(json.load(f)['tasks'])} review tasks to {path}")
        return 0
    print(json.dumps(metrics(load_records(), load_reviews(REVIEWS)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
