"""EXP-005 SC-1: freeze the owner's blind review, then unblind once and score both
conditions with the metrics and comparison rule frozen in protocol_sc1.json.

The freeze reads only the review log, the deck it was made from and the frozen run. It
fingerprints the blind key without reading its contents. Scoring refuses to run until the
frozen review is committed and on a remote branch.

Metrics: exp005_review_v2.metrics_v2 per condition (as frozen at 04ea296). Comparison:
exp005_schema.classify (frozen in protocol_sc1.json, code fingerprint checked).

usage:
  python src/exp005_sc1_score.py freeze   # once, after the blind review is complete
  python src/exp005_sc1_score.py score    # once, after the frozen review is pushed
"""

import argparse
import collections
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import exp005_review as r1
import exp005_review_v2 as rv2
import exp005_schema as sc
from rag_eval import sha256_file

FROZEN = os.path.join(sc.SC, "reviews", "sc-batch-1_blind_reviews_frozen_v1.jsonl")
MANIFEST = FROZEN[:-1]  # .jsonl -> .json
UNBLINDED = os.path.join(sc.RUN, "unblinded_reviews.jsonl")
RESULT = os.path.join(sc.RUN, "sc1_scores.json")
METRIC_CODE_COMMIT = "04ea296"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def final_judgments(rows, expected):
    """Latest judgment per expected task. Raises on a missing, unknown, conflicting or invalid answer."""
    judged = [r for r in rows if r["kind"] != "note"]
    by = collections.defaultdict(list)
    for r in judged:
        by[r["task_id"]].append(r)
    if set(by) != set(expected):
        raise RuntimeError(f"missing {sorted(set(expected) - set(by))[:10]}, unknown {sorted(set(by) - set(expected))[:10]}")
    final = []
    for task_id in sorted(expected):
        ordered = sorted(by[task_id], key=lambda r: r["reviewed_at"])
        last = ordered[-1]
        if any(r["reviewed_at"] == last["reviewed_at"] and r["value"] != last["value"] for r in ordered):
            raise RuntimeError(f"conflicting answers at the same second for {task_id}")
        if last["value"] not in {o["value"] for o in expected[task_id]["options"]}:
            raise RuntimeError(f"invalid value for {task_id}")
        final.append(last)
    return final, [r for r in rows if r["kind"] == "note"], sum(len(v) > 1 for v in by.values())


def fingerprints(protocol):
    return {"protocol_sha256": sha256_file(sc.PROTOCOL),
            "prompt_v2_sha256": protocol["conditions"]["A"]["sha256"],
            "prompt_v2_1_sha256": protocol["conditions"]["B"]["sha256"],
            "schema_v2_sha256": protocol["schema"]["sha256"],
            "batch_sha256": sha256_file(sc.BATCH),
            "outputs_sha256": sha256_file(sc.OUTPUTS),
            "blind_key_sha256": sha256_file(sc.BLIND_KEY),
            "comparison_rule_sha256": _json_sha(protocol["comparison_rule"]),
            "metrics_definition_sha256": _json_sha(protocol["metrics"]),
            "metric_code_sha256": {f: sha256_file(os.path.join(sc.v1.SRC, f))
                                   for f in ("exp005_review_v2.py", "exp005_schema.py")}}


def freeze(corpus=None, questions=None):
    if os.path.exists(FROZEN) or os.path.exists(MANIFEST):
        raise RuntimeError("the SC-1 review is already frozen. A change needs a new review version.")
    protocol = sc.check_frozen()
    with open(sc.SUMMARY, encoding="utf-8") as f:
        summary = json.load(f)
    if sha256_file(sc.OUTPUTS) != summary["outputs_sha256"]:
        raise RuntimeError("the SC-1 outputs changed")
    if corpus is None:
        from rag_corpus import open_corpus
        import rag_questions as rq
        corpus = open_corpus()
        questions = {q.question_id: q for q in rq.load_frozen()[0]}
    records = sc.v1_load(sc.OUTPUTS)
    tasks = sc.build_blind_tasks(records, questions, corpus)  # rebuilds and verifies every packet hash
    expected = {t["task_id"]: t for t in tasks}
    rows = r1.load_reviews(sc.REVIEWS)
    if {r["outputs_sha256"] for r in rows} != {summary["outputs_sha256"]}:
        raise RuntimeError("the review names different outputs")
    final, notes, repeated = final_judgments(rows, expected)
    os.makedirs(os.path.dirname(FROZEN), exist_ok=True)
    with open(FROZEN, "x", encoding="utf-8", newline="\n") as f:
        for r in final + sorted(notes, key=lambda r: (r["task_id"], r["reviewed_at"])):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    body = {"frozen_at": _now(), "run": "sc-batch-1", "review": sc.TITLE, "tasks": len(expected),
            "judgments": len(final), "notes": len(notes), "log_rows": len(rows),
            "tasks_answered_more_than_once": repeated, "unresolved": 0,
            "by_kind": dict(collections.Counter(r["kind"] for r in final)),
            "reviewers": sorted({r["reviewer"] for r in rows}),
            "first_judgment_at": min(r["reviewed_at"] for r in rows), "last_judgment_at": max(r["reviewed_at"] for r in rows),
            "log_sha256": sha256_file(sc.REVIEWS), "frozen_review_sha256": sha256_file(FROZEN),
            "packets_verified": len({t["question_id"] for t in tasks}), "blind_key_opened": False,
            **fingerprints(protocol)}
    with open(MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False, sort_keys=True)
    return body


def unblind(final, key):
    """Each frozen judgment with its condition. Sufficiency is judged once per question and
    applies to both conditions. Task IDs lose the blind code, so metrics_v2 can read them."""
    out = []
    for r in final:
        parts = r["task_id"].split(":")
        if len(parts) == 2 and parts[1] == "sufficiency":
            for cond in ("A", "B"):
                out.append(dict(r, condition=cond, blind_task_id=r["task_id"], shared=True))
            continue
        qid, blind, target = parts[0], parts[1], ":".join(parts[2:])
        mapped = key.get(blind)
        if mapped is None or mapped["question_id"] != qid:
            raise RuntimeError(f"{r['task_id']}: not in the blind key")
        out.append(dict(r, task_id=f"{qid}:{target}", condition=mapped["condition"], blind_task_id=r["task_id"],
                        shared=False))
    return out


def per_question(records, rows):
    out = {}
    for r in records:
        q, c = r["question_id"], r["condition"]
        mine = {x["task_id"]: x["value"] for x in rows if x["condition"] == c and x["task_id"].startswith(f"{q}:")}
        stmts = [v for k, v in mine.items() if k.split(":")[1].startswith(("claim", "limitation"))
                 and v in ("SUPPORTED", "UNSUPPORTED", "UNSURE")]
        first = r["attempts"][0] if r["attempts"] else {}
        out.setdefault(q, {})[c] = {
            "status": r["status"], "claims": len((r.get("answer") or {}).get("claims", [])),
            "supported": stmts.count("SUPPORTED"), "unsupported": stmts.count("UNSUPPORTED"), "unsure": stmts.count("UNSURE"),
            "uncited_item_limitations": sum(1 for k, v in mine.items() if ":limitation" in k and v == "YES"),
            "completeness": mine.get(f"{q}:completeness"), "abstention": mine.get(f"{q}:abstention"),
            "sufficiency": mine.get(f"{q}:sufficiency"),
            "first_attempt_valid": first.get("schema_valid"),
            "completion_tokens": (first.get("usage") or {}).get("completion_tokens")}
    return out


def score():
    import rag_select as rs
    if os.path.exists(RESULT) or os.path.exists(UNBLINDED):
        raise RuntimeError("SC-1 has already been scored")
    ok, commit = rs.rule_is_committed_and_pushed(FROZEN)
    if not ok:
        raise RuntimeError(f"frozen review: {commit}")
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    if sha256_file(FROZEN) != manifest["frozen_review_sha256"]:
        raise RuntimeError("the frozen review changed")
    protocol = sc.check_frozen()
    now = fingerprints(protocol)
    changed = [k for k, v in now.items() if manifest.get(k) != v]
    if changed:
        raise RuntimeError(f"inputs changed since the freeze: {changed}")
    with open(sc.BLIND_KEY, encoding="utf-8") as f:
        key = json.load(f)["key"]
    final = [json.loads(l) for l in open(FROZEN, encoding="utf-8") if l.strip()]
    rows = unblind([r for r in final if r["kind"] != "note"], key)
    with open(UNBLINDED, "x", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    records = sc.v1_load(sc.OUTPUTS)
    with open(sc.SUMMARY, encoding="utf-8") as f:
        summary = json.load(f)
    fmt = sc.format_metrics(records)
    human = {c: rv2.metrics_v2([r for r in records if r["condition"] == c],
                               [x for x in rows if x["condition"] == c]) for c in ("A", "B")}
    body = {"scored_at": _now(), "run": "sc-batch-1", "frozen_review_commit": commit,
            "frozen_review_sha256": manifest["frozen_review_sha256"], "unblinded_sha256": sha256_file(UNBLINDED),
            "conditions": {"A": "Prompt v2", "B": "Prompt v2.1"},
            "metric_code": f"exp005_review_v2.metrics_v2 at {METRIC_CODE_COMMIT}; exp005_schema.classify as frozen",
            "evidence_boundary": "context only: each answer judged against the exact packet supplied to the model",
            "format": fmt, "format_matches_run_summary": fmt == summary["format"],
            "deterministic": summary["deterministic"],
            "human": human,
            "per_question": per_question(records, rows),
            "classification": sc.classify(fmt, human),
            "comparison_rule": protocol["comparison_rule"]}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze", "score"])
    args = ap.parse_args(argv)
    try:
        body = freeze() if args.cmd == "freeze" else score()
    except (RuntimeError, FileExistsError) as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
