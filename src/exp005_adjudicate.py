"""EXP-005 dev-batch-2: Prompt v2 context-only adjudication v2
(AMENDMENT_2026-10-01_evidence_boundary.md).

The rule: a generated answer is judged only against the exact evidence packet the model
received. Full articles, the pages behind URLs, outside knowledge, search snippets and web
research are not evidence for this judgment.

The original Prompt v2 review (reviews/dev-batch-2_*_frozen_v1.jsonl) and its scores
(runs/dev-batch-2/prompt_v2_scores.json) stay as they are: the mixed-boundary historical
record. This module re-asks only the judgments whose outcome could change under the rule.
Each card shows the question, the frozen metadata, the generated answer or abstention and
the packet rebuilt from the store, verified byte for byte against the record's
context_sha256. Earlier judgments and notes are not shown, because the notes quote outside
sources.

usage:
  python src/exp005_adjudicate.py make-queue      # writes the deck; refuses a packet that does not verify
  python src/exp005_adjudicate.py freeze          # once, after every task has a judgment
  python src/exp005_adjudicate.py score-context   # once, after the frozen adjudication is pushed
"""

import argparse
import collections
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import exp005 as v1
import exp005_review as r1
import exp005_review_v2 as rv2
from item_store import ROOT

EXP = r1.EXP
REVIEWS = os.path.join(EXP, "reviews")
AMENDMENT = os.path.join(EXP, "AMENDMENT_2026-10-01_evidence_boundary.md")
LOG = os.path.join(REVIEWS, "dev-batch-2_context_adjudication_v2.jsonl")
FROZEN = os.path.join(REVIEWS, "dev-batch-2_context_adjudication_v2_frozen.jsonl")
MANIFEST = FROZEN[:-1]  # .jsonl -> .json
ORIGINAL = {"fresh": os.path.join(REVIEWS, "dev-batch-2_fresh_reviews_frozen_v1.jsonl"),
            "probe": os.path.join(REVIEWS, "dev-batch-2_regression_reviews_frozen_v1.jsonl")}
ORIGINAL_SCORES = os.path.join(EXP, "runs", "dev-batch-2", "prompt_v2_scores.json")
RESULT = os.path.join(EXP, "runs", "dev-batch-2", "prompt_v2_context_grounded_scores.json")
QUEUE_NAME = "exp005_v2_context_adjudication"
TITLE = "Prompt v2 context-only adjudication v2"
METRIC_CODE_COMMIT = "04ea296"

# task_id -> why its outcome could change under the context-only rule
TASKS = {
    "q017:abstention": "the INCORRECT judgment rests on item 278's full article, which the packet does not contain",
    "q017:limitation 0": "the reviewer's note judged the limitation against item 278's full article",
    "q023:abstention": "the INCORRECT judgment rests on the underlying i-D articles, not the packet",
    "q031:claim 1": "the reviewer checked the full Vogue interview before judging",
    "q031:completeness": "the PARTIAL judgment cites an outside page and weighs content the packet lacks",
    "q031:sufficiency": "the NO judgment (scored as a missed abstention) cites an outside page",
    "q013:regression:summary_detail": "the FIXED judgment used the Who What Wear article behind the URL (probe only)",
}
HEADER = ("CONTEXT-ONLY RULE: judge only against the evidence packet below, exactly as the model received it. "
          "Do not open links, search, or use the full articles or anything you know about them. URLs are shown "
          "as plain text because they were part of the packet.")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False).encode()).hexdigest()


def rebuild_packet(record, question, corpus):
    """The evidence packet for one record, rebuilt from the store the way exp005_v2 built it.
    Raises if it does not match the record's context_sha256."""
    from rag_corpus import get_items
    ids = record["retrieval"]["item_ids"]
    ev = {e.item_id: e for e in get_items(corpus, ids)}
    packet = v1.serialize_context([ev[i] for i in ids], question.filters)
    if _sha(packet) != record["context_sha256"]:
        raise RuntimeError(f"{record['question_id']}: the rebuilt packet does not match context_sha256")
    return packet


def packet_text(packet, question):
    constraints = v1.describe_constraints(question.filters)
    lines = [f"EVIDENCE PACKET ({len(packet)} item{'' if len(packet) == 1 else 's'}, frozen ranking order; the only evidence for this judgment)",
             f"Constraints given to the model: {constraints}", ""]
    for n, item in enumerate(packet, 1):
        lines.append(f"[{n}] item {item['item_id']}")
        for key, value in item.items():
            if key == "item_id":
                continue
            shown = "(empty)" if value in ("", None) else value
            lines.append(f"    {key}: {shown}" + ("   (text only, do not open)" if key == "url" else ""))
        lines.append("")
    return "\n".join(lines)


def _answer_block(record):
    a = record["answer"]
    status = "MODEL ABSTAINED (insufficient_evidence = true)" if a["insufficient_evidence"] else "MODEL ANSWERED"
    return f"GENERATED OUTPUT: {status}\n\n{rv2._answer_text(a)}"


def build_tasks(records, questions, corpus):
    """The adjudication cards, in TASKS order. Options match each original task's kind."""
    original = {t["task_id"]: t for t in rv2.fresh_tasks(records, corpus) + rv2.probe_tasks(records, corpus)}
    by_q = {r["question_id"]: r for r in records}
    packets, tasks = {}, []
    for task_id, reason in TASKS.items():
        if task_id not in original:
            raise RuntimeError(f"{task_id} is not a Prompt v2 review task")
        orig = original[task_id]
        r = by_q[orig["question_id"]]
        if r["question_id"] not in packets:
            packets[r["question_id"]] = rebuild_packet(r, questions[r["question_id"]], corpus)
        packet = packets[r["question_id"]]
        meta = (f"FROZEN METADATA\nquestion {r['question_id']} ({r.get('role')}), run dev-batch-2, Prompt v2, "
                f"status {r['status']}\nfilters {json.dumps(r['filters'], ensure_ascii=False)}\n"
                f"packet sha256 {r['context_sha256'][:16]}... (rebuilt and verified)")
        if orig["kind"] == "claim_support":
            n = int(orig["target"].split()[-1])
            stmt = r["answer"]["claims" if orig["target"].startswith("claim") else "limitations"][n]
            cited = set(stmt["supporting_item_ids"])
            focus = (f"{orig['target'].upper()}\n{stmt['text']}\n(cites items {', '.join(map(str, sorted(cited)))})\n\n"
                     + packet_text([i for i in packet if i["item_id"] in cited], questions[r["question_id"]])
                     .replace("EVIDENCE PACKET", "CITED ITEMS FROM THE PACKET", 1))
        elif orig["kind"] == "limitation_uncited":
            n = int(orig["target"].split()[-1])
            focus = (f"{orig['target'].upper()} (cites no item)\n{r['answer']['limitations'][n]['text']}\n\n"
                     + packet_text(packet, questions[r["question_id"]]))
        elif orig["kind"] == "context_sufficiency":
            focus = packet_text(packet, questions[r["question_id"]])
        else:  # abstention, answer_completeness, regression
            focus = f"{_answer_block(r)}\n\n{packet_text(packet, questions[r['question_id']])}"
        probe = "REGRESSION PROBE (never part of fresh metrics)\n\n" if r.get("role") == "regression_probe" else ""
        tasks.append({"task_id": task_id, "question_id": r["question_id"], "question": r["question"],
                      "kind": orig["kind"], "target": orig["target"],
                      "prompt": f"{orig['prompt']} Judge from the packet only.",
                      "options": orig["options"], "reason": reason,
                      "body": f"{HEADER}\n\n{probe}{meta}\n\n{focus}"})
    return tasks


def _inputs():
    import rag_questions as rq
    from rag_eval import sha256_file
    import exp005_v2 as v2
    records = rv2.load_records()
    with open(v2.SUMMARY2, encoding="utf-8") as f:
        if sha256_file(v2.OUTPUTS2) != json.load(f)["outputs_sha256"]:
            raise RuntimeError("the dev-batch-2 outputs changed")
    return records, {q.question_id: q for q in rq.load_frozen()[0]}


def make_queue(corpus):
    import label_tool
    from rag_eval import sha256_file
    import exp005_v2 as v2
    if not os.path.exists(AMENDMENT):
        raise RuntimeError("the evidence-boundary amendment must exist first")
    records, questions = _inputs()
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": TITLE, "notes": True,
             "outputs_sha256": sha256_file(v2.OUTPUTS2), "amendment_sha256": sha256_file(AMENDMENT),
             "reviews_path": os.path.relpath(LOG, ROOT).replace(os.sep, "/"),
             "tasks": build_tasks(records, questions, corpus), "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue)


def freeze(corpus):
    """Once: the latest judgment per task plus notes, with a manifest. The original review is untouched."""
    from rag_eval import sha256_file
    import exp005_v2 as v2
    if os.path.exists(FROZEN) or os.path.exists(MANIFEST):
        raise RuntimeError("the adjudication is already frozen. A change needs a new adjudication version.")
    records, questions = _inputs()
    expected = {t["task_id"]: t for t in build_tasks(records, questions, corpus)}
    rows = r1.load_reviews(LOG)
    if {r["outputs_sha256"] for r in rows} - {sha256_file(v2.OUTPUTS2)}:
        raise RuntimeError("the adjudication names different outputs")
    judged = [r for r in rows if r["kind"] != "note"]
    notes = [r for r in rows if r["kind"] == "note"]
    by = collections.defaultdict(list)
    for r in judged:
        by[r["task_id"]].append(r)
    if set(by) != set(expected):
        raise RuntimeError(f"missing {sorted(set(expected) - set(by))}, unknown {sorted(set(by) - set(expected))}")
    final = []
    for task_id in TASKS:
        ordered = sorted(by[task_id], key=lambda r: r["reviewed_at"])
        last = ordered[-1]
        if any(r["reviewed_at"] == last["reviewed_at"] and r["value"] != last["value"] for r in ordered):
            raise RuntimeError(f"conflicting answers at the same second for {task_id}")
        if last["value"] not in {o["value"] for o in expected[task_id]["options"]}:
            raise RuntimeError(f"invalid value for {task_id}")
        final.append(last)
    with open(FROZEN, "x", encoding="utf-8", newline="\n") as f:
        for r in final + sorted(notes, key=lambda r: (r["task_id"], r["reviewed_at"])):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    body = {"frozen_at": _now(), "run": "dev-batch-2", "review": TITLE, "judgments": len(final), "notes": len(notes),
            "values": {r["task_id"]: r["value"] for r in final}, "reviewers": sorted({r["reviewer"] for r in rows}),
            "log_sha256": sha256_file(LOG), "frozen_sha256": sha256_file(FROZEN),
            "amendment_sha256": sha256_file(AMENDMENT), "outputs_sha256": sha256_file(v2.OUTPUTS2),
            "original_reviews_sha256": {k: sha256_file(p) for k, p in ORIGINAL.items()},
            "packets_sha256": {r["question_id"]: r["context_sha256"] for r in records
                               if r["question_id"] in {t.split(":")[0] for t in TASKS}}}
    with open(MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def merge(original, adjudicated):
    """The original judgments with each adjudicated task's judgment replaced. Notes are dropped
    (they never enter metrics). Returns (rows, changes)."""
    adj = {r["task_id"]: r for r in adjudicated if r["kind"] != "note"}
    rows, changes = [], []
    for r in original:
        if r["kind"] == "note":
            continue
        if r["task_id"] in adj:
            new = adj[r["task_id"]]
            if new["value"] != r["value"]:
                changes.append({"task_id": r["task_id"], "mixed_boundary": r["value"], "context_only": new["value"]})
            rows.append(dict(r, value=new["value"], reviewed_at=new["reviewed_at"], adjudication="context_only_v2"))
        else:
            rows.append(r)
    missing = set(adj) - {r["task_id"] for r in rows}
    if missing:
        raise RuntimeError(f"adjudicated tasks not in the original review: {sorted(missing)}")
    return rows, changes


def score_context():
    """Prompt-v2 context-grounded metrics: unchanged outputs, prompt and metrics_v2 formulas,
    original judgments with the frozen adjudication applied. The original score file is not touched."""
    import rag_select as rs
    import exp005_score_v2 as s2
    from rag_eval import sha256_file
    if os.path.exists(RESULT):
        raise RuntimeError("the context-grounded score already exists")
    ok, commit = rs.rule_is_committed_and_pushed(FROZEN)
    if not ok:
        raise RuntimeError(f"frozen adjudication: {commit}")
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    if sha256_file(FROZEN) != manifest["frozen_sha256"]:
        raise RuntimeError("the frozen adjudication changed")
    if {k: sha256_file(p) for k, p in ORIGINAL.items()} != manifest["original_reviews_sha256"]:
        raise RuntimeError("an original frozen review changed")
    s2.check_inputs()
    load = lambda p: [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
    adjudicated = load(FROZEN)
    records = rv2.load_records()
    fresh_rows, fresh_changes = merge(load(ORIGINAL["fresh"]), [r for r in adjudicated if r["task_id"] in
                                                                {t for t in TASKS if not t.startswith("q013")}])
    probe_rows, probe_changes = merge(load(ORIGINAL["probe"]), [r for r in adjudicated if r["task_id"].startswith("q013")])
    with open(ORIGINAL_SCORES, encoding="utf-8") as f:
        original = json.load(f)
    probe = {r["task_id"].split(":")[-1]: r["value"] for r in probe_rows if r["kind"] == "regression"}
    body = {"scored_at": _now(), "run": "dev-batch-2", "evidence_boundary": "context_only (amendment 2026-10-01)",
            "metric_code": f"exp005_review_v2.metrics_v2 at {METRIC_CODE_COMMIT}",
            "metric_code_sha256": sha256_file(os.path.join(v1.SRC, "exp005_review_v2.py")),
            "frozen_adjudication_commit": commit, "amendment_sha256": sha256_file(AMENDMENT),
            "original_scores_sha256": sha256_file(ORIGINAL_SCORES),
            "mixed_boundary_fresh_metrics": original["fresh_metrics"],
            "context_grounded_fresh_metrics": rv2.metrics_v2(records, fresh_rows),
            "changed_judgments": fresh_changes,
            "regression_probe": {"question_id": "q013", "outcomes": probe, "changed_judgments": probe_changes,
                                 "verdict": s2.probe_verdict(list(probe.values())), "in_fresh_metrics": False}}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make-queue", "freeze", "score-context"])
    args = ap.parse_args(argv)
    try:
        if args.cmd == "score-context":
            body = score_context()
        else:
            from rag_corpus import open_corpus
            if args.cmd == "make-queue":
                path = make_queue(open_corpus())
                with open(path, encoding="utf-8") as f:
                    q = json.load(f)
                body = {"queue": path, "title": q["title"], "tasks": [t["task_id"] for t in q["tasks"]]}
            else:
                body = freeze(open_corpus())
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
