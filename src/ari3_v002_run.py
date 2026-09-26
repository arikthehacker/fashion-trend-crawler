"""Run the pre-registered ARI3 v0.0.2 experiment (models/ari3-v0.0.2/PREREGISTRATION.md).

Arms, all with the frozen v0.0.1 architecture (same embedder revision, logistic
regression C = 1.0, temperature scaling, split conformal alpha = 0.10):
  v0.0.1   frozen weights from models/ari3-v0.0.1, not refit
  v0.0.2   trained on every train-split label (random + active learning)
  H5 arms  equal-size comparison, averaged over 20 random subsets:
           AL arm      = (n_random_train - k) random + k active-learning labels
           random arm  = n_random_train random labels
Test set: random-queue labels in the test split only. Active-learning labels are
excluded from testing and from calibration (conformal calibration must look like
the test distribution). Both choices are written to the results file.

Usage: python src/ari3_v002_run.py
"""

import hashlib
import json
import math
import os
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

import jev_spike as J
from ari3_freeze import EMBEDDER_REVISION, sha256_file
from item_store import DEFAULT_DB, ROOT, connect, utc_now

AL_NOTE = "active_learning_round_1"
OUT = os.path.join(ROOT, "models", "ari3-v0.0.2")


def fit_arm(X, y):
    clf = LogisticRegression(C=1.0, max_iter=2000).fit(X, y)
    return clf


def calibrate(clf, Xc, yc):
    T = J.fit_temperature(clf.decision_function(Xc), yc)
    p = 1 / (1 + np.exp(-clf.decision_function(Xc) / T))
    s = np.where(yc == 1, 1 - p, p)
    n = len(s)
    q = float(np.quantile(s, min(1.0, math.ceil((n + 1) * (1 - J.ALPHA)) / n), method="higher"))
    return T, q


def evaluate(logits, T, q, y):
    p_raw = 1 / (1 + np.exp(-logits))
    p = 1 / (1 + np.exp(-logits / T))
    pred = (p >= 0.5).astype(int)
    sets = [[l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok] for pi in p]
    correct = int((pred == y).sum())
    n = len(y)
    errs = [(s, t) for s, t, pr in zip(sets, y, pred) if pr != t]
    tp = int(((pred == 1) & (y == 1)).sum())
    return {
        "n": n, "accuracy": correct / n, "accuracy_95ci": list(J.wilson(correct, n)),
        "precision": tp / max(1, int((pred == 1).sum())), "recall": tp / max(1, int((y == 1).sum())),
        "ece_before_scaling": float(J.ece(p_raw, y)), "ece_after_scaling": float(J.ece(p, y)),
        "coverage": float(np.mean([("yes" if t else "no") in s for s, t in zip(sets, y)])),
        "decisive_share": float(np.mean([len(s) == 1 for s in sets])),
        "n_errors": len(errs), "errors_outside_set": sum(len(s) == 1 for s, _ in errs),
        "temperature": float(T), "qhat": q,
    }


def main() -> int:
    if os.path.exists(os.path.join(OUT, "manifest.json")):
        print("ARI3 v0.0.2 is already frozen. The experiment runs once.")
        return 1
    con = connect(DEFAULT_DB)
    rows = con.execute(
        """SELECT l.label_id, l.item_id, l.label, l.split, COALESCE(l.note,''), i.title, i.text_excerpt
           FROM labels l JOIN items i USING (item_id)
           WHERE l.task=? AND l.source='human' ORDER BY l.item_id""", (J.TASK,)).fetchall()
    snapshot = "\n".join(f"{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}" for r in rows)
    label_hash = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()

    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode([J.text(r[5], r[6]) for r in rows], normalize_embeddings=True)
    y = np.array([1 if r[2] == "yes" else 0 for r in rows])
    split = np.array([r[3] for r in rows])
    al = np.array([r[4] == AL_NOTE for r in rows])

    tr_rand, tr_al = (split == "train") & ~al, (split == "train") & al
    cal = (split == "calibration") & ~al
    test = (split == "test") & ~al

    # v0.0.1, frozen weights
    w = np.load(os.path.join(ROOT, "models", "ari3-v0.0.1", "weights.npz"))
    logit1 = X[test] @ w["coef"][0] + w["intercept"][0]
    r1 = evaluate(logit1, float(w["temperature"][0]), float(w["qhat"][0]), y[test])

    # v0.0.2, all train labels
    tr = tr_rand | tr_al
    clf2 = fit_arm(X[tr], y[tr])
    T2, q2 = calibrate(clf2, X[cal], y[cal])
    r2 = evaluate(clf2.decision_function(X[test]), T2, q2, y[test])

    # H5: equal-size arms, 20 random subsets
    k = int(tr_al.sum())
    idx_rand, idx_al = np.where(tr_rand)[0], np.where(tr_al)[0]
    n_rand = len(idx_rand)
    al_acc, rnd_acc, al_dec, rnd_dec = [], [], [], []
    for seed in range(20):
        rng = np.random.default_rng(seed)
        sub = rng.choice(idx_rand, n_rand - k, replace=False)
        arm_al = np.concatenate([sub, idx_al])
        for arm, acc, dec in ((arm_al, al_acc, al_dec), (idx_rand, rnd_acc, rnd_dec)):
            c = fit_arm(X[arm], y[arm])
            T, q = calibrate(c, X[cal], y[cal])
            r = evaluate(c.decision_function(X[test]), T, q, y[test])
            acc.append(r["accuracy"])
            dec.append(r["decisive_share"])
    h5 = {"k_active_learning_in_train": k, "arm_size": n_rand, "subsets": 20,
          "al_arm_accuracy_mean": float(np.mean(al_acc)), "random_arm_accuracy": float(np.mean(rnd_acc)),
          "al_arm_decisive_mean": float(np.mean(al_dec)), "random_arm_decisive": float(np.mean(rnd_dec)),
          "al_arm_accuracy_min_max": [float(min(al_acc)), float(max(al_acc))]}

    hyps = {
        "H1": {"test": "v0.0.2 decisive share >= 0.70", "value": r2["decisive_share"],
               "supported": r2["decisive_share"] >= 0.70},
        "H2": {"test": "v0.0.2 coverage >= 0.90", "value": r2["coverage"], "supported": r2["coverage"] >= 0.90},
        "H3": {"test": "v0.0.2 accuracy >= v0.0.1 accuracy on the same items",
               "value": [r2["accuracy"], r1["accuracy"]], "supported": r2["accuracy"] >= r1["accuracy"]},
        "H4": {"test": "v0.0.2 ECE after scaling <= 0.10", "value": r2["ece_after_scaling"],
               "supported": r2["ece_after_scaling"] <= 0.10},
        "H5": {"test": "AL arm accuracy > random arm accuracy (equal size, mean of 20 subsets)",
               "value": [h5["al_arm_accuracy_mean"], h5["random_arm_accuracy"]],
               "supported": h5["al_arm_accuracy_mean"] > h5["random_arm_accuracy"]},
    }

    os.makedirs(OUT, exist_ok=True)
    wpath = os.path.join(OUT, "weights.npz")
    np.savez(wpath, coef=clf2.coef_, intercept=clf2.intercept_, temperature=np.array([T2]), qhat=np.array([q2]))
    src = os.path.dirname(os.path.abspath(__file__))
    manifest = {
        "model": "ARI3", "version": "ari3-v0.0.2", "component": "perception", "task": J.TASK,
        "frozen_at": utc_now(),
        "preregistration": {"path": "models/ari3-v0.0.2/PREREGISTRATION.md", "commit": "79e95bc",
                            "sha256_committed": "2ed73c43c80ba38721d97540613aab695049fe2c7401dc30bbf3f513440480b1"},
        "embedder": {"name": J.EMBEDDER, "revision": EMBEDDER_REVISION, "dim": int(X.shape[1])},
        "classifier": {"type": "LogisticRegression", "C": 1.0},
        "labels": {"count": len(rows), "sha256": label_hash,
                   "train_random": int(tr_rand.sum()), "train_active_learning": k,
                   "calibration": int(cal.sum()), "test": int(test.sum()),
                   "active_learning_excluded_from_calibration": int(((split == "calibration") & al).sum()),
                   "active_learning_excluded_from_test": int(((split == "test") & al).sum())},
        "analysis_choices_not_in_preregistration": [
            "Active-learning labels whose hash split is calibration were excluded from calibration, "
            "because split conformal assumes calibration items resemble test items.",
            "H5 was run at equal training size: the active-learning arm replaces k random training labels "
            "with the k active-learning labels, averaged over 20 random subsets.",
        ],
        "results_test": {"ari3-v0.0.1": r1, "ari3-v0.0.2": r2},
        "h5": h5, "hypotheses": hyps,
        "sha256": {"weights.npz": sha256_file(wpath),
                   "src/ari3_v002_run.py": sha256_file(os.path.abspath(__file__))},
    }
    body = json.dumps(manifest, indent=2, sort_keys=True)
    manifest["manifest_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(json.dumps({k2: manifest[k2] for k2 in ("labels", "results_test", "h5", "hypotheses", "manifest_sha256")},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
