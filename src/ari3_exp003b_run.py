"""Run EXP-003B Forecast Detection once, as pre-registered in commit 2ff1c53
(models/ari3-v0.0.3/PREREGISTRATION.md, sections 4 and 6).

Trains a new is_forecast head on the shared perception architecture, calibrates
it, scores it on the test split, reports both groups together and separately,
and freezes the head to models/ari3-v0.0.3/is_forecast/.

Usage: python src/ari3_exp003b_run.py
"""

import hashlib
import json
import math
import os
import platform
import sys
import time

import numpy as np
from sklearn.linear_model import LogisticRegression

import jev_spike as J
from ari3_freeze import EMBEDDER_REVISION, sha256_file
from item_store import DEFAULT_DB, ROOT, connect, utc_now

TASK = "is_forecast"
OUT = os.path.join(ROOT, "models", "ari3-v0.0.3", "is_forecast")
GROUPS = ("exp003_forecast_random", "exp003_forecast_keyword")


def sig(z):
    return 1 / (1 + np.exp(-z))


def metrics(p, y, q):
    pred = (p >= 0.5).astype(int)
    sets = [[l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok] for pi in p]
    pos, neg = y == 1, y == 0
    tpr = float((pred[pos] == 1).mean()) if pos.any() else None
    tnr = float((pred[neg] == 0).mean()) if neg.any() else None
    bal = (tpr + tnr) / 2 if tpr is not None and tnr is not None else None
    maj = max(y.mean(), 1 - y.mean())
    errs = [(s, t) for s, t, pr in zip(sets, y, pred) if pr != t]
    return {
        "n": int(len(y)), "positives": int(pos.sum()),
        "accuracy": float((pred == y).mean()), "accuracy_95ci": list(J.wilson(int((pred == y).sum()), len(y))),
        "balanced_accuracy": bal, "recall_forecast": tpr, "specificity": tnr,
        "majority_baseline_accuracy": float(maj), "majority_baseline_balanced": 0.5,
        "coverage": float(np.mean([("yes" if t else "no") in s for s, t in zip(sets, y)])),
        "single_share": float(np.mean([len(s) == 1 for s in sets])),
        "n_errors": len(errs), "errors_outside_set": sum(len(s) == 1 for s, _ in errs),
    }


def main() -> int:
    if os.path.exists(os.path.join(OUT, "manifest.json")):
        print("EXP-003B has already run. It runs once.")
        return 1
    t0 = time.time()
    con = connect(DEFAULT_DB)
    rows = con.execute(
        """SELECT l.item_id, l.label, l.split, l.note, i.title, i.text_excerpt, l.created_at
           FROM labels l JOIN items i USING (item_id)
           WHERE l.task=? AND l.source='human' ORDER BY l.item_id""", (TASK,)).fetchall()
    snapshot = "\n".join(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}" for r in rows)
    label_hash = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
    queue = os.path.join(ROOT, "data", "store", "queues", "is_forecast_exp003.json")
    queue_hash = sha256_file(queue)

    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode([J.text(r[4], r[5]) for r in rows], normalize_embeddings=True)
    y = np.array([1 if r[1] == "yes" else 0 for r in rows])
    split = np.array([r[2] for r in rows])
    group = np.array([r[3] for r in rows])
    tr, ca, te = split == "train", split == "calibration", split == "test"

    clf = LogisticRegression(C=1.0, max_iter=2000).fit(X[tr], y[tr])
    T = J.fit_temperature(clf.decision_function(X[ca]), y[ca])
    pc = sig(clf.decision_function(X[ca]) / T)
    s = np.where(y[ca] == 1, 1 - pc, pc)
    n = len(s)
    q = float(np.quantile(s, min(1.0, math.ceil((n + 1) * (1 - J.ALPHA)) / n), method="higher"))

    p_all = sig(clf.decision_function(X) / T)
    results = {"both_groups": metrics(p_all[te], y[te], q)}
    for g in GROUPS:
        m = te & (group == g)
        results[g] = metrics(p_all[m], y[m], q)
    both = results["both_groups"]
    hyps = {
        "H4": {"test": "balanced accuracy >= 0.75 and above the majority baseline (both groups)",
               "value": both["balanced_accuracy"],
               "supported": bool(both["balanced_accuracy"] is not None and both["balanced_accuracy"] >= 0.75
                                 and both["balanced_accuracy"] > 0.5)},
        "H5": {"test": "conformal coverage >= 0.90 (both groups)", "value": both["coverage"],
               "supported": both["coverage"] >= 0.90},
    }

    # Finding without a pass criterion: style-filtered mentions in items this head marks as forecasts.
    items = con.execute(
        "SELECT DISTINCT e.item_id FROM v_events_style e WHERE e.model_version='ari3-v0.0.2'").fetchall()
    ids = [r[0] for r in items]
    finding = None
    if ids:
        txt = {r[0]: J.text(r[1], r[2]) for r in con.execute(
            f"SELECT item_id, title, text_excerpt FROM items WHERE item_id IN ({','.join('?' * len(ids))})", ids)}
        Xi = emb.encode([txt[i] for i in ids], normalize_embeddings=True)
        pi = sig(clf.decision_function(Xi) / T)
        yes_only = [1 - v <= q and not v <= q for v in pi]
        ment = dict(con.execute(
            "SELECT item_id, count(*) FROM v_events_style WHERE model_version='ari3-v0.0.2' GROUP BY item_id"))
        total = sum(ment.values())
        fc = sum(ment[i] for i, f in zip(ids, yes_only) if f)
        finding = {"style_filtered_mentions": total, "in_items_marked_forecast": fc,
                   "share": fc / total if total else None, "items_marked_forecast": int(sum(yes_only)),
                   "items": len(ids), "rule": "conformal set is {yes} (confident forecast)"}

    os.makedirs(OUT, exist_ok=True)
    wpath = os.path.join(OUT, "weights.npz")
    np.savez(wpath, coef=clf.coef_, intercept=clf.intercept_, temperature=np.array([T]), qhat=np.array([q]))
    manifest = {
        "model": "ARI3", "version": "ari3-v0.0.3", "head": TASK, "experiment": "EXP-003B",
        "frozen_at": utc_now(),
        "preregistration": {"path": "models/ari3-v0.0.3/PREREGISTRATION.md", "commit": "2ff1c53",
                            "sha256_committed": "fa65367d3166cba52903229bfd849ce34022b536e93ae6c62341325e7911aff1"},
        "embedder": {"name": J.EMBEDDER, "revision": EMBEDDER_REVISION, "dim": int(X.shape[1])},
        "classifier": {"type": "LogisticRegression", "C": 1.0},
        "calibration": {"temperature": float(T)}, "conformal": {"alpha": J.ALPHA, "qhat": q},
        "labels": {"count": len(rows), "positives": int(y.sum()), "sha256": label_hash,
                   "train": int(tr.sum()), "calibration": int(ca.sum()), "test": int(te.sum()),
                   "first_label_at": min(r[6] for r in rows), "last_label_at": max(r[6] for r in rows)},
        "queue": {"path": "data/store/queues/is_forecast_exp003.json", "sha256": queue_hash, "seed": 11},
        "results_test": results, "hypotheses": hyps, "finding_forecast_share_of_counts": finding,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scikit_learn": __import__("sklearn").__version__,
                        "sentence_transformers": __import__("sentence_transformers").__version__,
                        "os": platform.platform()},
        "runtime_seconds": round(time.time() - t0, 1),
        "sha256": {"weights.npz": sha256_file(wpath), "src/ari3_exp003b_run.py": sha256_file(os.path.abspath(__file__))},
    }
    body = json.dumps(manifest, indent=2, sort_keys=True)
    manifest["manifest_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(json.dumps({k: manifest[k] for k in ("labels", "results_test", "hypotheses",
                                               "finding_forecast_share_of_counts", "runtime_seconds", "manifest_sha256")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
