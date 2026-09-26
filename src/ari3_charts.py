"""Compute the numbers behind the ARI3 notebook charts.

Uses the frozen weights of each version (never refit) on the EXP-002 test set:
the 61 random-queue labels in the test split. Writes numbers only, no article
text, to web/lib/ari3_charts.json.

Charts:
  reliability   5 bins of calibrated probability: mean prediction vs observed rate
  confusion     2x2 counts at the 0.5 threshold
  histogram     10 bins of calibrated probability, split by the editor's label
  coverage      conformal coverage and set size across alpha, recalibrated per alpha
                on the 45 calibration labels
  learning      exploratory: accuracy and confident share vs number of random
                training labels, 20 random subsets per size, fresh models (not
                the frozen releases)

Usage: python src/ari3_charts.py
"""

import json
import math
import os
import platform
import sys
import time

import numpy as np
from sklearn.linear_model import LogisticRegression

import jev_spike as J
from ari3_freeze import EMBEDDER_REVISION
from item_store import DEFAULT_DB, ROOT, connect, utc_now

AL_NOTE = "active_learning_round_1"
OUT = os.path.join(ROOT, "web", "lib", "ari3_charts.json")


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def conformal_q(p_cal, y_cal, alpha):
    s = np.where(y_cal == 1, 1 - p_cal, p_cal)
    n = len(s)
    return float(np.quantile(s, min(1.0, math.ceil((n + 1) * (1 - alpha)) / n), method="higher"))


def sets_for(p, q):
    return [[l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok] for pi in p]


def main() -> int:
    t0 = time.time()
    con = connect(DEFAULT_DB)
    rows = con.execute(
        """SELECT l.item_id, l.label, l.split, COALESCE(l.note,''), i.title, i.text_excerpt
           FROM labels l JOIN items i USING (item_id)
           WHERE l.task=? AND l.source='human' ORDER BY l.item_id""", (J.TASK,)).fetchall()
    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode([J.text(r[4], r[5]) for r in rows], normalize_embeddings=True)
    y = np.array([1 if r[1] == "yes" else 0 for r in rows])
    split = np.array([r[2] for r in rows])
    al = np.array([r[3] == AL_NOTE for r in rows])
    test, cal, tr_rand = (split == "test") & ~al, (split == "calibration") & ~al, (split == "train") & ~al

    out = {"generated_at": utc_now(), "n_test": int(test.sum()), "n_calibration": int(cal.sum()),
           "environment": {"python": platform.python_version(), "numpy": np.__version__,
                           "scikit_learn": __import__("sklearn").__version__},
           "versions": {}}

    for version in ("ari3-v0.0.1", "ari3-v0.0.2"):
        w = np.load(os.path.join(ROOT, "models", version, "weights.npz"))
        T, q = float(w["temperature"][0]), float(w["qhat"][0])
        logit = lambda Xs: Xs @ w["coef"][0] + w["intercept"][0]
        p = sigmoid(logit(X[test]) / T)
        yt = y[test]
        pred = (p >= 0.5).astype(int)
        s = sets_for(p, q)

        rel = []
        edges = np.linspace(0, 1, 6)
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
            rel.append({"lo": float(lo), "hi": float(hi), "n": int(m.sum()),
                        "mean_p": float(p[m].mean()) if m.any() else None,
                        "observed": float(yt[m].mean()) if m.any() else None})

        hist = []
        hedges = np.linspace(0, 1, 11)
        for lo, hi in zip(hedges[:-1], hedges[1:]):
            m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
            hist.append({"lo": float(lo), "yes": int((m & (yt == 1)).sum()), "no": int((m & (yt == 0)).sum())})

        cov = []
        p_cal = sigmoid(logit(X[cal]) / T)
        for alpha in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
            qa = conformal_q(p_cal, y[cal], alpha)
            sa = sets_for(p, qa)
            cov.append({"alpha": alpha,
                        "coverage": float(np.mean([("yes" if t else "no") in x for x, t in zip(sa, yt)])),
                        "single_share": float(np.mean([len(x) == 1 for x in sa])),
                        "empty_share": float(np.mean([len(x) == 0 for x in sa]))})

        out["versions"][version] = {
            "temperature": T, "qhat": q,
            "confusion": {"tp": int(((pred == 1) & (yt == 1)).sum()), "fp": int(((pred == 1) & (yt == 0)).sum()),
                          "fn": int(((pred == 0) & (yt == 1)).sum()), "tn": int(((pred == 0) & (yt == 0)).sum())},
            "single_answer": {"right": int(sum(len(x) == 1 and (x[0] == "yes") == bool(t) for x, t in zip(s, yt))),
                              "wrong": int(sum(len(x) == 1 and (x[0] == "yes") != bool(t) for x, t in zip(s, yt))),
                              "not_sure": int(sum(len(x) == 2 for x in s)), "empty": int(sum(len(x) == 0 for x in s))},
            "reliability": rel, "histogram": hist, "coverage_vs_alpha": cov,
        }

    # Exploratory learning curve on random labels only.
    idx = np.where(tr_rand)[0]
    curve = []
    for size in (25, 50, 75, 100, 125, 150, 175, len(idx)):
        accs, decs = [], []
        for seed in range(20 if size < len(idx) else 1):
            sub = np.random.default_rng(seed).choice(idx, size, replace=False) if size < len(idx) else idx
            if len(set(y[sub])) < 2:
                continue
            clf = LogisticRegression(C=1.0, max_iter=2000).fit(X[sub], y[sub])
            T = J.fit_temperature(clf.decision_function(X[cal]), y[cal])
            pc = sigmoid(clf.decision_function(X[cal]) / T)
            q = conformal_q(pc, y[cal], J.ALPHA)
            pt = sigmoid(clf.decision_function(X[test]) / T)
            accs.append(float(((pt >= 0.5).astype(int) == y[test]).mean()))
            decs.append(float(np.mean([len(x) == 1 for x in sets_for(pt, q)])))
        curve.append({"n_train": int(size), "runs": len(accs),
                      "accuracy_mean": float(np.mean(accs)), "accuracy_min": float(min(accs)), "accuracy_max": float(max(accs)),
                      "single_mean": float(np.mean(decs)), "single_min": float(min(decs)), "single_max": float(max(decs))})
    out["learning_curve"] = curve
    out["runtime_seconds"] = round(time.time() - t0, 1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out["versions"][k]["confusion"] for k in out["versions"]}))
    print(json.dumps({k: out["versions"][k]["single_answer"] for k in out["versions"]}))
    print(json.dumps(out["learning_curve"], indent=0))
    print("runtime", out["runtime_seconds"], "s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
