"""EXP-004 relevance judging: the queue ARI3 Review shows, and the judgment log it writes.

A relevance queue pairs each draft question with the items pooled for it. The editor
answers relevant, not relevant or unsure. Every answer is appended to a JSONL log in the
experiment folder, so the gold labels are a tracked, reviewable file. Nothing is ever
rewritten: a changed answer is a new line, and the latest line for a (question, item,
labeler) wins (rag_eval.gold).

Cards are shuffled within each question with a fixed seed, and the card never shows which
retrieval method found the item or at what rank, so judging stays blind to the methods.

usage: python src/rag_review.py make-queue [--pool P] [--questions Q] [--judgments J]
"""

import argparse
import json
import os
import random
import sys

from item_store import ROOT, utc_now
from rag_eval import Judgment, Question, load_jsonl
import label_tool

EXP = os.path.join(ROOT, "experiments", "exp-004-grounded-retrieval")
QUEUE_NAME = "rag_relevance_v1"
CHOICES = [{"key": "r", "label": "Relevant", "value": "relevant"},
           {"key": "n", "label": "Not relevant", "value": "not_relevant"},
           {"key": "u", "label": "Unsure", "value": "unsure"}]
HELP = ("Relevant: the headline or excerpt gives evidence that helps answer the question, "
        "within its filters. Not relevant: it does not. Unsure: the stored text is not enough to tell.")


def describe_filters(f):
    parts = []
    if f.get("start_date") or f.get("end_date"):
        parts.append(f"published {f.get('start_date') or 'any time'} to {f.get('end_date') or 'now'}")
    if f.get("as_of"):
        mode = "known to ARI3 by" if f.get("temporal_mode") == "replay" else "published by"
        parts.append(f"{mode} {f['as_of']}")
    for key, name in (("languages", "language"), ("sectors", "sector"), ("coarse_groups", "sector group"),
                      ("outlets", "outlet")):
        if f.get(key):
            parts.append(f"{name}: {', '.join(f[key])}")
    return "; ".join(parts) or "no filters"


def make_queue(pool_path, questions_path, judgments_path, seed=20260930):
    questions = {q.question_id: q for q in load_jsonl(questions_path, Question)}
    by_q = {}
    with open(pool_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            by_q.setdefault(row["question_id"], []).append(row)
    rng = random.Random(seed)
    cards = []
    for qid in sorted(by_q):
        rows = sorted(by_q[qid], key=lambda r: r["item_id"])
        rng.shuffle(rows)
        q = questions[qid]
        cards += [{"question_id": qid, "question": q.question,
                   "filters": describe_filters(q.filters.model_dump(exclude_none=True)),
                   "item_id": r["item_id"], "pool_source": r["pool_source"]} for r in rows]
    queue = {"kind": "rag_relevance", "task": "rag_relevance", "title": "Evidence relevance (EXP-004)",
             "question": "Does this item help answer the question?", "help": HELP, "choices": CHOICES,
             "dataset_version": questions[next(iter(questions))].dataset_version,
             "judgments_path": os.path.relpath(judgments_path, ROOT).replace(os.sep, "/"),
             "cards": cards, "item_ids": [c["item_id"] for c in cards]}
    return label_tool._write_queue(QUEUE_NAME, queue)


def judgments_file(queue):
    return os.path.join(ROOT, queue["judgments_path"])


def judged(queue, labeler="ariella"):
    """(question_id, item_id) pairs this labeler has answered."""
    path = judgments_file(queue)
    if not os.path.exists(path):
        return set()
    return {(j.question_id, j.item_id) for j in load_jsonl(path, Judgment) if j.labeler == labeler}


def left(queue, labeler="ariella"):
    done = judged(queue, labeler)
    return sum(1 for c in queue["cards"] if (c["question_id"], c["item_id"]) not in done), len(queue["cards"])


def record(con, queue, card, value, labeler="ariella"):
    """Append one validated judgment to the log and return it."""
    url = con.execute("SELECT url FROM items WHERE item_id = ?", (card["item_id"],)).fetchone()[0]
    j = Judgment(question_id=card["question_id"], item_id=card["item_id"], url=url, judgment=value,
                 labeler=labeler, labeled_at=utc_now(), pool_source=card["pool_source"],
                 dataset_version=queue["dataset_version"])
    path = judgments_file(queue)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(j.model_dump_json() + "\n")
    return j


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make-queue"])
    ap.add_argument("--pool", default=os.path.join(EXP, "pool_v1.jsonl"))
    ap.add_argument("--questions", default=os.path.join(EXP, "questions_v1.jsonl"))
    ap.add_argument("--judgments", default=os.path.join(EXP, "judgments", "rag_relevance_v1.jsonl"))
    args = ap.parse_args(argv)
    path = make_queue(args.pool, args.questions, args.judgments)
    with open(path, encoding="utf-8") as f:
        print(f"Wrote {len(json.load(f)['cards'])} cards to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
