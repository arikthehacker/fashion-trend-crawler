"""EXP-003A Temporal Generalization (models/ari3-v0.0.3/PREREGISTRATION.md section 5, as
amended by AMENDMENT_2026-09-30_holdout_eligibility.md).

Frozen ARI3 v0.0.2 (is_style_signal, not refit, recalibrated or retuned) on the 150
time-holdout items the editor labeled. Metric definitions are those of v0.0.2's own
evaluation (`evaluate` in src/ari3_v002_run.py): accuracy of the 0.5 decision,
coverage = the true label is in the conformal set, not-sure share = sets equal to
{yes, no}.

usage:
  python src/ari3_exp003a_run.py verify        # read-only checks on the labels and the deck
  python src/ari3_exp003a_run.py freeze-gold   # once; writes the frozen gold and its manifest
  python src/ari3_exp003a_run.py run           # once; needs the frozen gold committed and pushed
"""

import argparse
import collections
import glob
import hashlib
import json
import os
import platform
import sys
import time

from ari3_freeze import EMBEDDER_REVISION, sha256_file
from item_store import DEFAULT_DB, ROOT, connect, utc_now

FREEZE = "2026-09-26T19:25:40Z"
V3 = os.path.join(ROOT, "models", "ari3-v0.0.3")
V2 = os.path.join(ROOT, "models", "ari3-v0.0.2")
OUT = os.path.join(V3, "exp003a")
GOLD = os.path.join(OUT, "gold_v1.jsonl")
GOLD_MANIFEST = os.path.join(OUT, "gold_v1.manifest.json")
RESULT = os.path.join(OUT, "result.json")
QUEUE = os.path.join(ROOT, "data", "store", "queues", "is_style_signal_holdout_exp003.json")
PREREG = os.path.join(V3, "PREREGISTRATION.md")
PREREG_SHA = "fa65367d3166cba52903229bfd849ce34022b536e93ae6c62341325e7911aff1"
AMENDMENT = os.path.join(V3, "AMENDMENT_2026-09-30_holdout_eligibility.md")
DECK_SHA = "192a050a3225559ee9fb37b95d0c0724c73c7337a4a209b4db97c447c8cd67ce"
NOTE = "exp003_time_holdout"
TASK = "is_style_signal"


def _text_sha(path):
    """Line-ending-independent SHA-256 of a committed text file."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def model_fingerprints():
    with open(os.path.join(V2, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    weights = sha256_file(os.path.join(V2, "weights.npz"))
    if weights != m["sha256"]["weights.npz"]:
        raise RuntimeError("ARI3 v0.0.2 weights differ from the frozen manifest")
    return {"version": m["version"], "weights_sha256": weights, "manifest_sha256_recorded": m["manifest_sha256"],
            "manifest_file_sha256": _text_sha(os.path.join(V2, "manifest.json")), "frozen_at": m["frozen_at"],
            "embedder": m["embedder"]}


def verify(con, backup_paths=None):
    """Every check Phase 1A asks for. Returns a report; raises nothing, so every failure is listed."""
    with open(QUEUE, encoding="utf-8") as f:
        deck = json.load(f)
    ids = deck["item_ids"]
    problems = []
    deck_sha = hashlib.sha256(json.dumps(ids).encode()).hexdigest()
    if deck_sha != DECK_SHA or deck.get("item_ids_sha256") != DECK_SHA:
        problems.append("deck fingerprint changed")
    if len(ids) != 150 or len(set(ids)) != 150:
        problems.append("deck is not 150 unique items")
    rows = con.execute("SELECT label_id, item_id, label, source, labeler, split, note, created_at FROM labels "
                       "WHERE task=? AND (split='time_holdout' OR note=?)", (TASK, NOTE)).fetchall()
    by = collections.defaultdict(list)
    for r in rows:
        by[r[1]].append(r)
    unknown = sorted(set(by) - set(ids))
    missing = sorted(set(ids) - set(by))
    multiple = sorted(i for i, rs in by.items() if len(rs) > 1)
    conflicting = sorted(i for i in multiple if len({r[2] for r in by[i]}) > 1)
    invalid = sorted(r[1] for r in rows if r[2] not in ("yes", "no") or r[3] != "human" or r[5] != "time_holdout"
                     or r[6] != NOTE)
    other = con.execute(f"SELECT item_id, split FROM labels WHERE task=? AND split<>'time_holdout' AND item_id IN "
                        f"({','.join('?' * len(ids))})", (TASK, *ids)).fetchall()
    for name, xs in (("unknown item IDs", unknown), ("deck items with no label", missing),
                     ("conflicting labels", conflicting), ("invalid label rows", invalid),
                     ("deck items with labels in other splits", other)):
        if xs:
            problems.append(f"{name}: {xs[:20]}")
    marks = ",".join("?" * len(ids))
    items = {r[0]: r for r in con.execute(
        f"SELECT item_id, published_at, first_seen_at, text_excerpt IS NOT NULL, syndicated_of FROM items "
        f"WHERE item_id IN ({marks})", ids)}
    rule = {"published_after_freeze": [i for i in ids if not (i in items and items[i][1] > FREEZE)],
            "first_seen_after_freeze": [i for i in ids if not (i in items and items[i][2] and items[i][2] > FREEZE)],
            "has_stored_summary": [i for i in ids if not (i in items and items[i][3])],
            "not_syndicated": [i for i in ids if not (i in items and items[i][4] is None)]}
    for k, xs in rule.items():
        if xs:
            problems.append(f"eligibility rule '{k}' fails for {xs[:20]}")
    if backup_paths is None:
        backup_paths = sorted(glob.glob(os.path.join(ROOT, "data", "store", "backups", "**", "*.db"), recursive=True))
    import label_tool
    evidence = label_tool.pre_freeze_evidence(con, ids, FREEZE, backup_paths)
    if evidence:
        problems.append(f"pre-freeze evidence for {len(evidence)} items: {dict(list(evidence.items())[:10])}")
    final = {i: by[i][-1] for i in ids if i in by}
    return {"deck_sha256": deck_sha, "deck_items": len(ids), "label_rows": len(rows), "labeled_items": len(final),
            "distribution": dict(collections.Counter(r[2] for r in final.values())),
            "revised_or_duplicate_rows": len(rows) - len(by), "unresolved": len(missing) + len(conflicting),
            "labelers": sorted({r[4] for r in rows}), "first_label_at": min((r[7] for r in rows), default=None),
            "last_label_at": max((r[7] for r in rows), default=None),
            "eligibility_failures": {k: len(v) for k, v in rule.items()},
            "backups_checked": len(backup_paths), "pre_freeze_evidence": len(evidence),
            "problems": problems, "ok": not problems, "_final": final}


def freeze_gold(con):
    if os.path.exists(GOLD) or os.path.exists(GOLD_MANIFEST):
        raise RuntimeError("the EXP-003A gold is already frozen. A label change needs a new gold version.")
    report = verify(con)
    if not report["ok"]:
        raise RuntimeError(f"verification failed: {report['problems']}")
    final = report.pop("_final")
    os.makedirs(OUT, exist_ok=True)
    with open(GOLD, "x", encoding="utf-8", newline="\n") as f:
        for i in sorted(final):
            r = final[i]
            f.write(json.dumps({"item_id": r[1], "label": r[2], "label_id": r[0], "labeler": r[4], "split": r[5],
                                "note": r[6], "created_at": r[7]}, sort_keys=True) + "\n")
    body = {"experiment": "EXP-003A", "frozen_at": utc_now(), "gold": "models/ari3-v0.0.3/exp003a/gold_v1.jsonl",
            "gold_sha256": _text_sha(GOLD), "label_source": "data/store/ari3lla.db labels (task is_style_signal, "
                                                             "split time_holdout, source human)",
            "verification": {k: v for k, v in report.items() if k != "problems"},
            "deck": {"path": "data/store/queues/is_style_signal_holdout_exp003.json", "item_ids_sha256": DECK_SHA,
                     "file_sha256": sha256_file(QUEUE), "seed": 13},
            "model": model_fingerprints(),
            "preregistration": {"path": "models/ari3-v0.0.3/PREREGISTRATION.md", "commit": "2ff1c53",
                                "sha256": _text_sha(PREREG)},
            "amendment": {"path": "models/ari3-v0.0.3/AMENDMENT_2026-09-30_holdout_eligibility.md",
                          "sha256": _text_sha(AMENDMENT)}}
    if body["preregistration"]["sha256"] != PREREG_SHA:
        raise RuntimeError("the pre-registration differs from its committed text")
    with open(GOLD_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, sort_keys=True)
    return body


def load_gold():
    with open(GOLD_MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    if _text_sha(GOLD) != manifest["gold_sha256"]:
        raise RuntimeError("the frozen gold changed")
    with open(GOLD, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()], manifest


def hypotheses(r):
    return {"H1": {"test": "conformal coverage on the time holdout >= 0.90", "value": r["coverage"],
                   "verdict": "SUPPORTED" if r["coverage"] >= 0.90 else "NOT SUPPORTED"},
            "H2": {"test": "accuracy on the time holdout >= 0.85", "value": r["accuracy"],
                   "verdict": "SUPPORTED" if r["accuracy"] >= 0.85 else "NOT SUPPORTED"},
            "H3": {"test": "share of {yes, no} sets on the time holdout <= 0.35", "value": r["not_sure_share"],
                   "verdict": "SUPPORTED" if r["not_sure_share"] <= 0.35 else "NOT SUPPORTED"}}


def run(con):
    import numpy as np
    import rag_select as rs
    import jev_spike as J
    from ari3_v002_run import evaluate
    if os.path.exists(RESULT):
        raise RuntimeError("EXP-003A has already run. It runs once.")
    for path in (GOLD, GOLD_MANIFEST):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    gold, manifest = load_gold()
    model = model_fingerprints()
    if model != manifest["model"]:
        raise RuntimeError("the model fingerprints differ from those bound to the gold")
    t0 = time.time()
    ids = [g["item_id"] for g in gold]
    text = {r[0]: J.text(r[1], r[2]) for r in con.execute(
        f"SELECT item_id, title, text_excerpt FROM items WHERE item_id IN ({','.join('?' * len(ids))})", ids)}
    texts = [text[i] for i in ids]
    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode(texts, normalize_embeddings=True)
    w = np.load(os.path.join(V2, "weights.npz"))
    T, q = float(w["temperature"][0]), float(w["qhat"][0])
    logits = X @ w["coef"][0] + w["intercept"][0]
    y = np.array([1 if g["label"] == "yes" else 0 for g in gold])
    r = evaluate(logits, T, q, y)
    p = 1 / (1 + np.exp(-logits / T))
    sets = [[l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok] for pi in p]
    r["not_sure_share"] = float(np.mean([len(s) == 2 for s in sets]))
    r["empty_set_share"] = float(np.mean([len(s) == 0 for s in sets]))
    r["set_counts"] = dict(collections.Counter(json.dumps(s) for s in sets))
    # Integrity: the append-only prediction ledger scored these items with the same model.
    ledger = dict(con.execute(
        f"SELECT item_id, conformal_set FROM label_predictions WHERE task=? AND model_version=? AND item_id IN "
        f"({','.join('?' * len(ids))})", (TASK, model["version"], *ids)))
    agree = sum(1 for i, s in zip(ids, sets) if i in ledger and json.loads(ledger[i]) == s)
    body = {"experiment": "EXP-003A Temporal Generalization", "ran_at": utc_now(), "runs": 1,
            "model": model, "refit": False, "recalibrated": False, "threshold_changed": False,
            "gold": {"path": manifest["gold"], "sha256": manifest["gold_sha256"],
                     "manifest_sha256": _text_sha(GOLD_MANIFEST), "n": len(gold),
                     "distribution": dict(collections.Counter(g["label"] for g in gold))},
            "deck_item_ids_sha256": manifest["deck"]["item_ids_sha256"],
            "preregistration": manifest["preregistration"], "amendment": manifest["amendment"],
            "inputs_text_sha256": hashlib.sha256("\n".join(texts).encode("utf-8")).hexdigest(),
            "metrics": r, "hypotheses": hypotheses(r),
            "metric_definitions": "evaluate() in src/ari3_v002_run.py, the function that produced v0.0.2's own "
                                  "results; not_sure_share is the share of sets equal to {yes, no}",
            "reported_without_a_pass_criterion": ["accuracy_95ci", "precision", "recall", "ece_before_scaling",
                                                  "ece_after_scaling", "decisive_share", "n_errors",
                                                  "errors_outside_set", "empty_set_share", "set_counts"],
            "integrity": {"ledger_predictions_found": len(ledger), "ledger_sets_equal": agree},
            "code_sha256": {"src/ari3_exp003a_run.py": _text_sha(os.path.abspath(__file__)),
                            "src/ari3_v002_run.py": _text_sha(os.path.join(ROOT, "src", "ari3_v002_run.py"))},
            "environment": {"python": platform.python_version(), "numpy": np.__version__,
                            "scikit_learn": __import__("sklearn").__version__,
                            "sentence_transformers": __import__("sentence_transformers").__version__},
            "runtime_seconds": round(time.time() - t0, 1)}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, sort_keys=True)
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["verify", "freeze-gold", "run"])
    args = ap.parse_args(argv)
    con = connect(DEFAULT_DB)
    try:
        if args.cmd == "verify":
            body = verify(con)
            body.pop("_final")
        elif args.cmd == "freeze-gold":
            body = freeze_gold(con)
        else:
            body = run(con)
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, sort_keys=True))
    return 0 if body.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
