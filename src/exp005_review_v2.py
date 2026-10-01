"""EXP-005 rubric v2 and metrics v2 for dev-batch-2 (Prompt v2).

Two separate decks and logs:
  fresh       the five fresh DEV questions, scored by metrics v2
  regression  the q013 POST-TUNING REGRESSION PROBE, descriptive only, never scored with
              the fresh questions

Fresh tasks: claim_support for each claim and each limitation that cites items;
limitation_uncited for each limitation that cites nothing; answer_completeness and
context_sufficiency for answered questions; abstention for model abstentions. Every task
can also carry an optional reviewer note, which is qualitative only.

usage: python src/exp005_review_v2.py make-queues
       python src/exp005_review_v2.py metrics      # after the owner's review is complete
"""

import argparse
import json
import os
import sys

from item_store import ROOT, utc_now
import exp005_review as r1
import label_tool

EXP = r1.EXP
OUTPUTS = os.path.join(EXP, "runs", "dev-batch-2", "outputs.jsonl")
FRESH_REVIEWS = os.path.join(EXP, "reviews", "dev-batch-2_fresh_reviews.jsonl")
PROBE_REVIEWS = os.path.join(EXP, "reviews", "dev-batch-2_regression_reviews.jsonl")
OPTIONS = dict(r1.OPTIONS, limitation_uncited=[("n", "No item-specific fact", "NO"), ("y", "States an uncited item fact",
                                                                                     "YES"), ("u", "Unsure", "UNSURE")],
               regression=[("f", "Fixed", "FIXED"), ("r", "Recurred", "RECURRED"), ("c", "Changed form", "CHANGED_FORM"),
                           ("u", "Unsure", "UNSURE")])
PROMPTS = dict(r1.PROMPTS, limitation_uncited="This limitation cites no item. Does it state a fact about a specific item?")
V1_FAILURES = {
    "summary_detail": "Prompt v1 added a detail ('hair') that its citations did not support. Does the v2 answer add any "
                      "detail that its citations do not support?",
    "coverage": "Prompt v1 left out relevant items in the context (PARTIAL). Does the v2 answer represent the distinct "
                "relevant evidence in the context?",
    "uncited_limitation": "Prompt v1 stated an uncited fact about item 1363 in a limitation. Do the v2 limitations state "
                          "an uncited fact about a specific item?"}


def load_records(path=OUTPUTS):
    return r1.load_records(path)


def _context(record, corpus):
    from rag_corpus import get_items
    ids = record["retrieval"]["item_ids"]
    ev = {e.item_id: e for e in get_items(corpus, ids)}
    return ev, "SUPPLIED CONTEXT (frozen ranking order)\n\n" + "\n".join(r1._item_text(ev[i], n)
                                                                        for n, i in enumerate(ids, 1))


def _answer_text(a):
    claims = "\n".join(f"{n}. {c['text']}  (items {', '.join(map(str, c['supporting_item_ids']))})"
                       for n, c in enumerate(a["claims"]))
    lims = "\n".join(f"- {x['text']}" + (f"  (items {', '.join(map(str, x['supporting_item_ids']))})"
                                         if x["supporting_item_ids"] else "") for x in a["limitations"]) or "(none)"
    return f"CLAIMS\n{claims or '(none: insufficient evidence)'}\n\nLIMITATIONS\n{lims}"


def fresh_tasks(records, corpus):
    tasks = []
    for r in records:
        if r.get("role") != "fresh" or r["status"] not in ("answered", "model_abstention"):
            continue
        ev, context = _context(r, corpus)
        head = {"question_id": r["question_id"], "question": r["question"]}
        a = r["answer"]
        if r["status"] == "model_abstention":
            tasks.append({**head, "task_id": f"{r['question_id']}:abstention", "kind": "abstention", "target": "answer",
                          "body": f"{_answer_text(a)}\n\n{context}"})
        for n, c in enumerate(a["claims"]):
            cited = "\n".join(r1._item_text(ev[i]) for i in c["supporting_item_ids"] if i in ev)
            tasks.append({**head, "task_id": f"{r['question_id']}:claim {n}", "kind": "claim_support",
                          "target": f"claim {n}", "body": f"CLAIM {n}\n{c['text']}\n\nCITED EVIDENCE\n\n{cited}"})
        for n, lim in enumerate(a["limitations"]):
            if lim["supporting_item_ids"]:
                cited = "\n".join(r1._item_text(ev[i]) for i in lim["supporting_item_ids"] if i in ev)
                tasks.append({**head, "task_id": f"{r['question_id']}:limitation {n}", "kind": "claim_support",
                              "target": f"limitation {n}",
                              "body": f"LIMITATION {n} (cites items)\n{lim['text']}\n\nCITED EVIDENCE\n\n{cited}"})
            else:
                tasks.append({**head, "task_id": f"{r['question_id']}:limitation {n}", "kind": "limitation_uncited",
                              "target": f"limitation {n}", "body": f"LIMITATION {n} (cites no item)\n{lim['text']}\n\n"
                                                                   f"{context}"})
        if r["status"] == "answered":
            tasks.append({**head, "task_id": f"{r['question_id']}:completeness", "kind": "answer_completeness",
                          "target": "answer", "body": f"{_answer_text(a)}\n\n{context}"})
            tasks.append({**head, "task_id": f"{r['question_id']}:sufficiency", "kind": "context_sufficiency",
                          "target": "answer", "body": context})
    return _finish(tasks)


def probe_tasks(records, corpus):
    tasks = []
    for r in records:
        if r.get("role") != "regression_probe":
            continue
        _, context = _context(r, corpus)
        if r["status"] in ("answered", "model_abstention"):
            answer = _answer_text(r["answer"])
        else:
            answer = f"(no valid answer: {r['status']})"
        for key, text in V1_FAILURES.items():
            tasks.append({"question_id": r["question_id"], "question": r["question"],
                          "task_id": f"{r['question_id']}:regression:{key}", "kind": "regression", "target": key,
                          "prompt": text, "body": f"POST-TUNING REGRESSION PROBE (not part of fresh metrics)\n\n"
                                                  f"{answer}\n\n{context}"})
    return _finish(tasks)


def _finish(tasks):
    for t in tasks:
        t.setdefault("prompt", PROMPTS.get(t["kind"], ""))
        t["options"] = [{"key": k, "label": label, "value": v} for k, label, v in OPTIONS[t["kind"]]]
    return tasks


def make_queues(corpus, outputs=OUTPUTS):
    from rag_eval import sha256_file
    records = load_records(outputs)
    sha = sha256_file(outputs)
    paths = []
    for name, title, tasks, log in (("exp005_v2_fresh", "Answer review v2 (EXP-005)", fresh_tasks(records, corpus),
                                     FRESH_REVIEWS),
                                    ("exp005_v2_regression", "Regression probe q013 (EXP-005 v2)",
                                     probe_tasks(records, corpus), PROBE_REVIEWS)):
        queue = {"kind": "gen_review", "task": name, "title": title, "outputs_sha256": sha, "notes": True,
                 "reviews_path": os.path.relpath(log, ROOT).replace(os.sep, "/"), "tasks": tasks, "item_ids": []}
        paths.append(label_tool._write_queue(name, queue))
    return paths


def done(queue, reviewer="ariella"):
    """Tasks with a judgment from this reviewer. Notes alone do not complete a task."""
    rows = [r for r in r1.load_reviews(r1.reviews_file(queue)) if r["kind"] != "note"]
    return {t for t, r in r1.latest(rows).items() if r["reviewer"] == reviewer}


def record_note(queue, task, text, reviewer="ariella"):
    """An optional reviewer note. Qualitative only, never a metric input."""
    text = (text or "").strip()
    if not text:
        raise ValueError("an empty note is not recorded")
    row = {"task_id": task["task_id"], "question_id": task["question_id"], "kind": "note", "target": task["target"],
           "value": text[:1000], "reviewer": reviewer, "reviewed_at": utc_now(), "outputs_sha256": queue["outputs_sha256"]}
    path = r1.reviews_file(queue)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def metrics_v2(records, reviews):
    """Metrics v2 (protocol_v2.json): fresh questions only; notes are ignored."""
    fresh_ids = {r["question_id"] for r in records if r.get("role") == "fresh"}
    judged = [r for r in reviews if r["kind"] != "note" and r["task_id"].split(":")[0] in fresh_ids]
    rv = {k: x["value"] for k, x in r1.latest(judged).items()}
    support = [v for k, v in rv.items() if k.split(":")[1].startswith(("claim", "limitation"))
               and v in ("SUPPORTED", "UNSUPPORTED", "UNSURE")]
    sup, uns, unsure = support.count("SUPPORTED"), support.count("UNSUPPORTED"), support.count("UNSURE")
    fresh = [r for r in records if r.get("role") == "fresh"]
    evaluable = grounded = correct = incorrect = missed = 0
    for r in fresh:
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
        if r["status"] != "answered":
            continue
        suff = rv.get(f"{q}:sufficiency")
        if suff in (None, "UNSURE"):
            continue
        evaluable += 1
        missed += suff == "NO"
        own = [v for k, v in rv.items() if k.startswith(f"{q}:") and k.split(":")[1].startswith(("claim", "limitation"))
               and v in ("SUPPORTED", "UNSUPPORTED", "UNSURE")]
        grounded += "UNSUPPORTED" not in own and not (rv.get(f"{q}:completeness") == "INSUFFICIENT" and suff == "YES")
    return {"claim_support_precision": round(sup / (sup + uns), 4) if sup + uns else None,
            "statements_reviewed": len(support), "supported": sup, "unsupported": uns, "unsure": unsure,
            "grounded_answer_rate": round(grounded / evaluable, 4) if evaluable else None,
            "grounded": grounded, "evaluable_outputs": evaluable,
            "system_abstentions": sum(r["status"] == "system_abstention" for r in fresh),
            "abstention": {"correct": correct, "incorrect": incorrect, "missed": missed,
                           "precision": round(correct / (correct + incorrect), 4) if correct + incorrect else None,
                           "recall": round(correct / (correct + missed), 4) if correct + missed else None},
            "completeness": {v: sum(1 for k, x in rv.items() if k.endswith(":completeness") and x == v)
                             for v in ("COMPLETE", "PARTIAL", "INSUFFICIENT", "UNSURE")},
            "uncited_item_specific_limitations": sum(1 for k, x in rv.items() if x == "YES" and ":limitation" in k),
            "human_unsure_rate": round(sum(x == "UNSURE" for x in rv.values()) / len(rv), 4) if rv else None,
            "notes": sum(1 for r in reviews if r["kind"] == "note" and r["task_id"].split(":")[0] in fresh_ids)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make-queues", "metrics"])
    args = ap.parse_args(argv)
    from rag_corpus import open_corpus
    if args.cmd == "make-queues":
        for p in make_queues(open_corpus()):
            with open(p, encoding="utf-8") as f:
                print(f"Wrote {len(json.load(f)['tasks'])} tasks to {p}")
        return 0
    print(json.dumps(metrics_v2(load_records(), r1.load_reviews(FRESH_REVIEWS)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
