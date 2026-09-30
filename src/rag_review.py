"""EXP-004 relevance judging: the queue ARI3 Review shows, and the judgment log it writes.

The queue is built only from pool_v2 (depth 10, over the frozen questions). Each card
holds the question, its filters and the item ID, and nothing about which method found
the item, at what rank or score, or how many methods found it. Cards are shuffled within
each question with a fixed seed.

Every answer (relevant, not_relevant or unsure) is appended to
judgments/rag_relevance_v2.jsonl. Nothing is rewritten: a changed answer is a new line,
and the latest line for a (question, item, labeler) wins.

usage: python src/rag_review.py make-queue
"""

import argparse
import json
import os
import random
import sys

from item_store import ROOT, utc_now
from rag_eval import PATHS, Judgment, sha256_file
import label_tool
import rag_questions

QUEUE_NAME = "rag_relevance_v2"
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


def make_queue(pool_path=None, manifest_path=None, judgments_path=None, frozen=None, freeze_manifest=None,
               seed=20260930):
    pool_path = pool_path or PATHS["pool"]
    manifest_path = manifest_path or PATHS["pool_manifest"]
    judgments_path = judgments_path or PATHS["judgments"]
    questions, qmanifest = rag_questions.load_frozen(frozen, freeze_manifest)
    with open(manifest_path, encoding="utf-8") as f:
        pmanifest = json.load(f)
    if pmanifest["questions_sha256"] != qmanifest["questions_sha256"]:
        raise RuntimeError("the pool was built from a different question set")
    if sha256_file(pool_path) != pmanifest["pool_file_sha256"]:
        raise RuntimeError("the pool file no longer matches its manifest")
    by_q = {}
    with open(pool_path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            by_q.setdefault(row["question_id"], []).append(row["item_id"])
    qs = {q.question_id: q for q in questions}
    rng = random.Random(seed)
    cards = []
    for qid in sorted(by_q):
        items = sorted(by_q[qid])
        rng.shuffle(items)
        q = qs[qid]
        cards += [{"question_id": qid, "question": q.question,
                   "filters": describe_filters(q.filters.model_dump(exclude_none=True)), "item_id": i} for i in items]
    queue = {"kind": "rag_relevance", "task": "rag_relevance", "title": "Evidence relevance (EXP-004)",
             "question": "Does this item help answer the question?", "help": HELP, "choices": CHOICES,
             "dataset_version": qmanifest["dataset_version"], "pool_sha256": pmanifest["pool_sha256"],
             "judgments_path": os.path.relpath(judgments_path, ROOT).replace(os.sep, "/"),
             "cards": cards, "item_ids": [c["item_id"] for c in cards]}
    return label_tool._write_queue(QUEUE_NAME, queue)


def judgments_file(queue):
    return os.path.join(ROOT, queue["judgments_path"])


def judged(queue, labeler="ariella"):
    """(question_id, item_id) pairs this labeler has answered for this pool."""
    from rag_eval import load_jsonl
    path = judgments_file(queue)
    if not os.path.exists(path):
        return set()
    return {(j.question_id, j.item_id) for j in load_jsonl(path, Judgment)
            if j.labeler == labeler and j.pool_sha256 == queue["pool_sha256"]}


def left(queue, labeler="ariella"):
    done = judged(queue, labeler)
    return sum(1 for c in queue["cards"] if (c["question_id"], c["item_id"]) not in done), len(queue["cards"])


def record(con, queue, card, value, labeler="ariella"):
    """Append one validated judgment to the log and return it."""
    url = con.execute("SELECT url FROM items WHERE item_id = ?", (card["item_id"],)).fetchone()[0]
    j = Judgment(task="rag_relevance", dataset_version=queue["dataset_version"], pool_sha256=queue["pool_sha256"],
                 question_id=card["question_id"], item_id=card["item_id"], url=url, judgment=value,
                 labeler=labeler, judged_at=utc_now())
    path = judgments_file(queue)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(j.model_dump_json() + "\n")
    return j


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make-queue"])
    ap.parse_args(argv)
    path = make_queue()
    with open(path, encoding="utf-8") as f:
        print(f"Wrote {len(json.load(f)['cards'])} cards to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
