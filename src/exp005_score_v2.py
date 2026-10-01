"""EXP-005 dev-batch-2: freeze the owner's two Prompt v2 reviews (fresh questions and the
q013 regression probe), then score the fresh questions with metrics v2, frozen at 04ea296
before generation. The probe is reported separately and never enters fresh metrics.

usage:
  python src/exp005_score_v2.py freeze-reviews   # once; both frozen reviews and manifests
  python src/exp005_score_v2.py score            # once; needs both frozen reviews pushed
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
import exp005_v2 as v2
from rag_eval import sha256_file

REVIEWS = os.path.join(v2.v1.EXP, "reviews")
FROZEN = {"fresh": os.path.join(REVIEWS, "dev-batch-2_fresh_reviews_frozen_v1.jsonl"),
          "probe": os.path.join(REVIEWS, "dev-batch-2_regression_reviews_frozen_v1.jsonl")}
MANIFEST = {k: p[:-1] for k, p in FROZEN.items()}  # .jsonl -> .json
LOGS = {"fresh": rv2.FRESH_REVIEWS, "probe": rv2.PROBE_REVIEWS}
RESULT = os.path.join(v2.BATCH2_DIR, "prompt_v2_scores.json")
METRIC_CODE_COMMIT = "04ea296"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_inputs():
    with open(v2.PROTOCOL_V2, encoding="utf-8") as f:
        protocol = json.load(f)
    with open(v2.SUMMARY2, encoding="utf-8") as f:
        summary = json.load(f)
    checks = {"prompt": protocol["prompt"]["sha256"] == sha256_file(v2.PROMPT_V2),
              "schema": protocol["schema"]["sha256"] == hashlib.sha256(v2.schema_json().encode()).hexdigest(),
              "code": protocol["code_sha256"] == {f: sha256_file(os.path.join(v2.v1.SRC, f)) for f in v2.CODE_FILES_V2},
              "outputs": sha256_file(v2.OUTPUTS2) == summary["outputs_sha256"]}
    if not all(checks.values()):
        raise RuntimeError(f"a frozen input changed: {checks}")
    return protocol, summary


def _freeze_one(kind, expected, summary, extra):
    rows = r1.load_reviews(LOGS[kind])
    if {r["outputs_sha256"] for r in rows} != {summary["outputs_sha256"]}:
        raise RuntimeError(f"{kind}: reviews name different outputs")
    judged = [r for r in rows if r["kind"] != "note"]
    notes = [r for r in rows if r["kind"] == "note"]
    by = collections.defaultdict(list)
    for r in judged:
        by[r["task_id"]].append(r)
    if set(by) != set(expected):
        raise RuntimeError(f"{kind}: missing {sorted(set(expected) - set(by))}, unknown {sorted(set(by) - set(expected))}")
    final = []
    for task_id in sorted(expected):
        ordered = sorted(by[task_id], key=lambda r: r["reviewed_at"])
        last = ordered[-1]
        if any(r["reviewed_at"] == last["reviewed_at"] and r["value"] != last["value"] for r in ordered):
            raise RuntimeError(f"{kind}: conflicting answers at the same second for {task_id}")
        if last["value"] not in {o["value"] for o in expected[task_id]["options"]}:
            raise RuntimeError(f"{kind}: invalid value for {task_id}")
        final.append(last)
    with open(FROZEN[kind], "x", encoding="utf-8", newline="\n") as f:
        for r in final + sorted(notes, key=lambda r: (r["task_id"], r["reviewed_at"])):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    body = {"frozen_at": _now(), "run": "dev-batch-2", "review": kind, "judgments": len(final), "notes": len(notes),
            "by_kind": {k: dict(collections.Counter(r["value"] for r in final if r["kind"] == k))
                        for k in sorted({r["kind"] for r in final})},
            "unsure": sum(r["value"] == "UNSURE" for r in final), "reviewers": sorted({r["reviewer"] for r in rows}),
            "log_sha256": sha256_file(LOGS[kind]), "frozen_review_sha256": sha256_file(FROZEN[kind]),
            "outputs_sha256": summary["outputs_sha256"], "prompt_v2_sha256": sha256_file(v2.PROMPT_V2),
            "schema_v2_sha256": hashlib.sha256(v2.schema_json().encode()).hexdigest(),
            "protocol_v2_sha256": sha256_file(v2.PROTOCOL_V2), "batch_sha256": sha256_file(v2.BATCH2), **extra}
    with open(MANIFEST[kind], "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def freeze_reviews(corpus):
    if any(os.path.exists(p) for p in list(FROZEN.values()) + list(MANIFEST.values())):
        raise RuntimeError("the reviews are already frozen. A change needs a new review version.")
    _, summary = check_inputs()
    records = rv2.load_records()
    probe = next(r for r in records if r.get("role") == "regression_probe")
    fresh = _freeze_one("fresh", {t["task_id"]: t for t in rv2.fresh_tasks(records, corpus)}, summary,
                        {"fresh_question_ids": sorted({r["question_id"] for r in records if r.get("role") == "fresh"})})
    probe_body = _freeze_one("probe", {t["task_id"]: t for t in rv2.probe_tasks(records, corpus)}, summary, {
        "probe_question_id": probe["question_id"],
        "probe_output_sha256": hashlib.sha256(json.dumps(probe, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "v1_failure_record": "runs/dev-batch-1/prompt_v1_evaluation.json",
        "v1_failure_record_sha256": sha256_file(os.path.join(v2.v1.BATCH_DIR, "prompt_v1_evaluation.json")),
        "in_fresh_metrics": False})
    return {"fresh": fresh, "probe": probe_body}


def probe_verdict(values):
    """FULLY_FIXED if all three are FIXED, NOT_FIXED if none are, INCONCLUSIVE if any is UNSURE,
    otherwise PARTIALLY_FIXED."""
    if "UNSURE" in values:
        return "INCONCLUSIVE"
    if all(v == "FIXED" for v in values):
        return "FULLY_FIXED"
    if not any(v == "FIXED" for v in values):
        return "NOT_FIXED"
    return "PARTIALLY_FIXED"


def score():
    import rag_select as rs
    if os.path.exists(RESULT):
        raise RuntimeError("Prompt v2 has already been scored for this batch")
    commits = {}
    for kind in FROZEN:
        ok, commit = rs.rule_is_committed_and_pushed(FROZEN[kind])
        if not ok:
            raise RuntimeError(f"frozen {kind} review: {commit}")
        with open(MANIFEST[kind], encoding="utf-8") as f:
            if sha256_file(FROZEN[kind]) != json.load(f)["frozen_review_sha256"]:
                raise RuntimeError(f"the frozen {kind} review changed")
        commits[kind] = commit
    _, summary = check_inputs()
    load = lambda p: [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]
    fresh_reviews, probe_reviews = load(FROZEN["fresh"]), load(FROZEN["probe"])
    records = rv2.load_records()
    probe = {r["task_id"].split(":")[-1]: r["value"] for r in probe_reviews if r["kind"] == "regression"}
    first_attempts = [r["attempts"][0] for r in records if r["attempts"]]
    fresh_first = [r["attempts"][0] for r in records if r["attempts"] and r.get("role") == "fresh"]
    body = {"scored_at": _now(), "run": "dev-batch-2", "metric_code": f"exp005_review_v2.metrics_v2 at {METRIC_CODE_COMMIT}",
            "metric_code_sha256": sha256_file(os.path.join(v2.v1.SRC, "exp005_review_v2.py")),
            "frozen_review_commits": commits,
            "fresh_metrics": rv2.metrics_v2(records, fresh_reviews),
            "format": {"first_attempt_schema_valid": f"{sum(a['schema_valid'] for a in first_attempts)}/{len(first_attempts)}",
                       "first_attempt_schema_valid_fresh": f"{sum(a['schema_valid'] for a in fresh_first)}/{len(fresh_first)}",
                       "retries": {r["question_id"]: r["attempts"][0]["schema_error"] for r in records
                                   if len(r["attempts"]) > 1},
                       "final_schema_valid": summary["all_calls"]["schema_valid_rate"]},
            "deterministic_fresh": {k: summary["fresh_only"][k] for k in (
                "citation_membership_valid_rate", "provenance_resolution_rate", "temporal_violations",
                "filter_violations", "nonexistent_citations", "provider_calls", "schema_retries", "status_counts")},
            "regression_probe": {"question_id": "q013", "outcomes": probe, "verdict": probe_verdict(list(probe.values())),
                                 "in_fresh_metrics": False}}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-reviews", "score"])
    args = ap.parse_args(argv)
    try:
        if args.cmd == "freeze-reviews":
            from rag_corpus import open_corpus
            body = freeze_reviews(open_corpus())
        else:
            body = score()
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
