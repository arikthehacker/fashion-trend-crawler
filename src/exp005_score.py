"""EXP-005 dev-batch-1: freeze the owner's review, then score Prompt v1 with the metric
code frozen before generation (exp005_review.metrics, commit c8bf177).

usage:
  python src/exp005_score.py freeze-review    # once; writes the frozen review and its manifest
  python src/exp005_score.py score            # once; needs the frozen review committed and pushed
"""

import argparse
import collections
import json
import os
import sys
from datetime import datetime, timezone

import exp005 as x
import exp005_review as xr
from rag_eval import sha256_file

FROZEN = os.path.join(x.EXP, "reviews", "dev-batch-1_reviews_frozen_v1.jsonl")
MANIFEST = os.path.join(x.EXP, "reviews", "dev-batch-1_reviews_frozen_v1.json")
RESULT = os.path.join(x.BATCH_DIR, "prompt_v1_scores.json")
METRIC_CODE_COMMIT = "c8bf177"


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_inputs():
    """Every frozen input must be unchanged. Returns the protocol and run summary."""
    import hashlib
    with open(x.PROTOCOL_PATH, encoding="utf-8") as f:
        protocol = json.load(f)
    with open(x.SUMMARY_PATH, encoding="utf-8") as f:
        summary = json.load(f)
    checks = {"prompt": protocol["prompt"]["sha256"] == sha256_file(x.PROMPT_PATH),
              "schema": protocol["schema"]["sha256"] == hashlib.sha256(x.schema_json().encode()).hexdigest(),
              "code": protocol["code_sha256"] == {f: sha256_file(os.path.join(x.SRC, f)) for f in x.CODE_FILES},
              "outputs": sha256_file(x.OUTPUTS_PATH) == summary["outputs_sha256"]}
    if not all(checks.values()):
        raise RuntimeError(f"a frozen input changed: {checks}")
    return protocol, summary


def freeze_review(corpus):
    if os.path.exists(FROZEN) or os.path.exists(MANIFEST):
        raise RuntimeError("the review is already frozen. A change needs a new review version.")
    _, summary = check_inputs()
    expected = {t["task_id"]: t for t in xr.build_tasks(xr.load_records(), corpus)}
    rows = xr.load_reviews(xr.REVIEWS)
    if {r["outputs_sha256"] for r in rows} != {summary["outputs_sha256"]}:
        raise RuntimeError("reviews name different generation outputs")
    by = collections.defaultdict(list)
    for r in rows:
        by[r["task_id"]].append(r)
    if set(by) != set(expected):
        raise RuntimeError(f"missing {sorted(set(expected) - set(by))}, unknown {sorted(set(by) - set(expected))}")
    final = []
    for task_id in sorted(expected):
        ordered = sorted(by[task_id], key=lambda r: r["reviewed_at"])
        last = ordered[-1]
        if any(r["reviewed_at"] == last["reviewed_at"] and r["value"] != last["value"] for r in ordered):
            raise RuntimeError(f"conflicting answers at the same second for {task_id}")
        if last["value"] not in {o["value"] for o in expected[task_id]["options"]}:
            raise RuntimeError(f"invalid value for {task_id}")
        final.append(last)
    with open(FROZEN, "x", encoding="utf-8", newline="\n") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    counts = {k: dict(collections.Counter(r["value"] for r in final if r["kind"] == k)) for k in xr.OPTIONS}
    body = {"frozen_at": _now(), "run": "dev-batch-1", "judgments": len(final),
            "by_kind": counts, "unsure": sum(r["value"] == "UNSURE" for r in final),
            "reviewers": sorted({r["reviewer"] for r in final}), "log_lines": len(rows),
            "log_sha256": sha256_file(xr.REVIEWS), "frozen_review_sha256": sha256_file(FROZEN),
            "outputs_sha256": summary["outputs_sha256"], "protocol_sha256": sha256_file(x.PROTOCOL_PATH),
            "prompt_v1_sha256": sha256_file(x.PROMPT_PATH)}
    with open(MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def score():
    import rag_select as rs
    if os.path.exists(RESULT):
        raise RuntimeError("Prompt v1 has already been scored for this batch")
    ok, commit = rs.rule_is_committed_and_pushed(FROZEN)
    if not ok:
        raise RuntimeError(f"frozen review: {commit}")
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    if sha256_file(FROZEN) != manifest["frozen_review_sha256"]:
        raise RuntimeError("the frozen review changed")
    _, summary = check_inputs()
    with open(FROZEN, encoding="utf-8") as f:
        reviews = [json.loads(line) for line in f if line.strip()]
    records = xr.load_records()
    body = {"scored_at": _now(), "run": "dev-batch-1", "metric_code": f"exp005_review.metrics at {METRIC_CODE_COMMIT}",
            "metric_code_sha256": sha256_file(os.path.join(x.SRC, "exp005_review.py")),
            "frozen_review_commit": commit, "frozen_review_sha256": manifest["frozen_review_sha256"],
            "metrics": xr.metrics(records, reviews),
            "deterministic": {k: summary[k] for k in ("schema_valid_rate", "citation_membership_valid_rate",
                                                     "provenance_resolution_rate", "temporal_violations",
                                                     "filter_violations", "nonexistent_citations", "schema_retries",
                                                     "provider_calls", "status_counts")}}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-review", "score"])
    args = ap.parse_args(argv)
    try:
        if args.cmd == "freeze-review":
            from rag_corpus import open_corpus
            print(json.dumps(freeze_review(open_corpus()), indent=1))
        else:
            print(json.dumps(score(), indent=1))
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
