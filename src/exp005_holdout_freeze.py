"""Freeze the C1 packet-sufficiency review of the EXP-005 holdout (once).

Reads the append-only review log, checks every row, keeps the latest judgment per card
(the frozen protocol's rule) plus any notes, and writes the frozen review and its manifest.
The log, the packets and every frozen C1 file are read, never changed. No retrieval and no
provider call happen here. exp005_holdout.py is pinned by the frozen protocol, so this step
lives in its own file.

usage: python src/exp005_holdout_freeze.py
"""

import collections
import json
import os
import re
import sys
from datetime import datetime, timezone

import exp005_holdout as h

FROZEN_REVIEW = os.path.join(h.HOLDOUT, "reviews", "sufficiency_reviews_v1_frozen.jsonl")
FROZEN_MANIFEST = os.path.join(h.HOLDOUT, "reviews", "sufficiency_reviews_v1_frozen.json")
AMENDMENT = os.path.join(h.HOLDOUT, "AMENDMENT_2026-10-03_sufficiency_instructions.md")
AMENDMENT_CREATED = "2026-10-03T20:40:00Z"
ROW_KEYS = {"task_id", "question_id", "kind", "target", "value", "reviewer", "reviewed_at", "outputs_sha256"}
LABELS = {v for _, _, v in h.SUFFICIENCY_OPTIONS}
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def check_rows(rows, question_ids, manifest_sha):
    """Every problem with the log. An empty list means it can be frozen."""
    problems = []
    for n, r in enumerate(rows, 1):
        if set(r) != ROW_KEYS:
            problems.append(f"row {n}: fields {sorted(set(r) ^ ROW_KEYS)}")
            continue
        qid = r["task_id"].split(":")[0]
        if r["kind"] == "note":
            if not str(r["value"]).strip():
                problems.append(f"row {n}: empty note")
        elif r["kind"] != "packet_sufficiency" or r["value"] not in LABELS:
            problems.append(f"row {n}: kind {r['kind']!r} value {r['value']!r}")
        if r["task_id"] != f"{qid}:sufficiency" or qid not in question_ids or r["question_id"] != qid:
            problems.append(f"row {n}: unknown task {r['task_id']!r}")
        if r["target"] != "packet" or r["reviewer"] != "ariella":
            problems.append(f"row {n}: target {r['target']!r} reviewer {r['reviewer']!r}")
        if r["outputs_sha256"] != manifest_sha:
            problems.append(f"row {n}: names packet manifest {r['outputs_sha256'][:12]}, not the committed one")
        if not STAMP.match(r["reviewed_at"]) or r["reviewed_at"] < AMENDMENT_CREATED:
            problems.append(f"row {n}: reviewed_at {r['reviewed_at']!r} is malformed or before the amendment")
    return problems


def latest(rows, question_ids):
    """(final judgments in question order, superseded count, problems)."""
    by = collections.defaultdict(list)
    for r in rows:
        if r["kind"] != "note":
            by[r["task_id"]].append(r)
    problems = [f"{q}: no judgment" for q in question_ids if f"{q}:sufficiency" not in by]
    final, superseded = [], 0
    for q in question_ids:
        ordered = sorted(by.get(f"{q}:sufficiency", []), key=lambda r: r["reviewed_at"])
        if not ordered:
            continue
        last = ordered[-1]
        if any(r["reviewed_at"] == last["reviewed_at"] and r["value"] != last["value"] for r in ordered[:-1]):
            problems.append(f"{q}: conflicting answers in the same second")
        superseded += len(ordered) - 1
        final.append(last)
    return final, superseded, problems


def packets_unchanged(m):
    packets = h.load_packets()
    rows = m["packets"]
    same = len(packets) == len(rows) == h.N_QUESTIONS and all(
        p["question_id"] == r["question_id"] and p["item_ids"] == r["item_ids"]
        and h.sha256_json(p["context"]) == r["context_sha256"] == p["context_sha256"]
        and h.sha256_json(p["messages"]) == r["messages_sha256"] for p, r in zip(packets, rows))
    return same and h.sha256_json(rows) == m["packets_sha256"]


def main():
    if os.path.exists(FROZEN_REVIEW) or os.path.exists(FROZEN_MANIFEST):
        raise RuntimeError("the C1 sufficiency review is already frozen")
    question_ids = [q.question_id for q in h.load_deck()]
    manifest_sha = h.sha256_file(h.MANIFEST)
    with open(h.MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    rows = h.load_packets(h.REVIEWS)  # one JSON object per line
    problems = check_rows(rows, set(question_ids), manifest_sha)
    final, superseded, more = latest(rows, question_ids)
    problems += more
    if not packets_unchanged(m) or h.sha256_file(h.SNAPSHOT) != m["store_snapshot"]["sha256"]:
        problems.append("a packet or the store snapshot differs from the committed manifest")
    if problems:
        print(json.dumps({"frozen": False, "problems": problems}, indent=1))
        return 1
    notes = sorted((r for r in rows if r["kind"] == "note"), key=lambda r: (r["task_id"], r["reviewed_at"]))
    with open(FROZEN_REVIEW, "x", encoding="utf-8", newline="\n") as f:
        for r in final + notes:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    counts = collections.Counter(r["value"] for r in final)
    body = {"version": "exp005-holdout-sufficiency-review-v1",
            "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "cards": len(final), "counts": {k: counts.get(k, 0) for k in ("SUFFICIENT", "INSUFFICIENT", "UNSURE")},
            "log_rows": len(rows), "superseded_answers": superseded, "notes": len(notes),
            "reviewers": sorted({r["reviewer"] for r in rows}),
            "reviewed_from": min(r["reviewed_at"] for r in rows), "reviewed_to": max(r["reviewed_at"] for r in rows),
            "values": {r["question_id"]: r["value"] for r in final},
            "metric_treatment": "SUFFICIENT: H2 denominator. INSUFFICIENT: H3 denominator. UNSURE: excluded from both, "
                                "reported separately (protocol_v1_frozen.json metrics.sufficiency; amendment 2026-10-03)",
            "log_sha256": h.sha256_file(h.REVIEWS), "frozen_review_sha256": h.sha256_file(FROZEN_REVIEW),
            "packet_manifest_sha256": manifest_sha, "packets_sha256": m["packets_sha256"],
            "store_snapshot_sha256": m["store_snapshot"]["sha256"],
            "amendment_sha256": h.sha256_file(AMENDMENT), "protocol_sha256": h.sha256_file(h.PROTOCOL),
            "questions_sha256": h.sha256_file(h.FROZEN), "provider_calls": 0}
    with open(FROZEN_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: v for k, v in body.items() if k != "values"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
