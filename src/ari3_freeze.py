"""Freeze an ARI3 perception model version: refit, verify, save, hash.

Refits the is_style_signal classifier exactly as jev_spike.py does, on a fixed
snapshot of human labels, then writes to models/<version>/:
    weights.npz     logistic regression coefficients, temperature, conformal threshold
    manifest.json   configuration, environment, metrics and SHA-256 hashes of the
                    code, the label snapshot and the weights
A frozen version is never refit. Later labels train a later version.

Usage:
    python src/ari3_freeze.py ari3-v0.0.1
"""

import hashlib
import json
import os
import platform
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

import jev_spike as J
from item_store import DEFAULT_DB, ROOT, connect, utc_now

EMBEDDER_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    version = argv[0]
    out = os.path.join(ROOT, "models", version)
    if os.path.exists(os.path.join(out, "manifest.json")):
        print(f"{version} is already frozen. Frozen versions are never refit.")
        return 1
    con = connect(DEFAULT_DB)

    rows = con.execute(
        """SELECT l.label_id, l.item_id, l.label, l.split, i.title, i.text_excerpt
           FROM labels l JOIN items i USING (item_id)
           WHERE l.task=? AND l.source='human' ORDER BY l.label_id""", (J.TASK,)).fetchall()
    snapshot = "\n".join(f"{r[1]}\t{r[2]}\t{r[3]}" for r in sorted(rows, key=lambda r: r[1]))
    label_hash = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()

    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode([J.text(r[4], r[5]) for r in rows], normalize_embeddings=True)
    y = np.array([1 if r[2] == "yes" else 0 for r in rows])
    split = np.array([r[3] for r in rows])
    tr, ca, te = split == "train", split == "calibration", split == "test"

    clf = LogisticRegression(C=1.0, max_iter=2000).fit(X[tr], y[tr])
    T = J.fit_temperature(clf.decision_function(X[ca]), y[ca])

    def prob(Xs):
        return 1 / (1 + np.exp(-clf.decision_function(Xs) / T))

    pc = prob(X[ca])
    scores = np.where(y[ca] == 1, 1 - pc, pc)
    n = len(scores)
    qhat = float(np.quantile(scores, min(1.0, np.ceil((n + 1) * (1 - J.ALPHA)) / n), method="higher"))

    pt, yt = prob(X[te]), y[te]
    pred = (pt >= 0.5).astype(int)
    sets = [[l for l, ok in (("yes", 1 - p <= qhat), ("no", p <= qhat)) if ok] for p in pt]
    errors = [(s, t) for s, t, pr in zip(sets, yt, pred) if pr != t]
    metrics = {
        "n_train": int(tr.sum()), "n_calibration": int(ca.sum()), "n_test": int(te.sum()),
        "test_accuracy": float((pred == yt).mean()),
        "precision": float(((pred == 1) & (yt == 1)).sum() / max(1, (pred == 1).sum())),
        "recall": float(((pred == 1) & (yt == 1)).sum() / max(1, (yt == 1).sum())),
        "ece_before_scaling": float(J.ece(1 / (1 + np.exp(-clf.decision_function(X[te]))), yt)),
        "ece_after_scaling": float(J.ece(pt, yt)),
        "conformal_test_coverage": float(np.mean([("yes" if t else "no") in s for s, t in zip(sets, yt)])),
        "singleton_share": float(np.mean([len(s) == 1 for s in sets])),
        "errors_outside_set": int(sum(len(s) == 1 for s, _ in errors)),
        "n_errors": len(errors),
    }

    os.makedirs(out, exist_ok=True)
    wpath = os.path.join(out, "weights.npz")
    np.savez(wpath, coef=clf.coef_, intercept=clf.intercept_,
             temperature=np.array([T]), qhat=np.array([qhat]))
    src = os.path.dirname(os.path.abspath(__file__))
    manifest = {
        "model": "ARI3", "version": version, "component": "perception",
        "task": J.TASK, "frozen_at": utc_now(),
        "predictions_logged_as": J.MODEL_VERSION,
        "embedder": {"name": J.EMBEDDER, "revision": EMBEDDER_REVISION, "dim": int(X.shape[1]),
                     "normalized": True, "frozen": True},
        "classifier": {"type": "LogisticRegression", "C": 1.0, "penalty": "l2", "solver": "lbfgs"},
        "calibration": {"method": "temperature_scaling", "temperature": float(T)},
        "conformal": {"method": "split_conformal", "alpha": J.ALPHA,
                      "score": "1 - p(true label)", "qhat": qhat},
        "split_rule": "sha256(item_id, task): 65% train, 15% calibration, 20% test",
        "labels": {"count": len(rows), "max_label_id": int(rows[-1][0]),
                   "positives": int(y.sum()), "sha256": label_hash},
        "metrics_test": metrics,
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__,
                        "scikit_learn": __import__("sklearn").__version__,
                        "sentence_transformers": __import__("sentence_transformers").__version__},
        "sha256": {"weights.npz": sha256_file(wpath),
                   "src/jev_spike.py": sha256_file(os.path.join(src, "jev_spike.py")),
                   "src/ari3_freeze.py": sha256_file(os.path.abspath(__file__))},
    }
    body = json.dumps(manifest, indent=2, sort_keys=True)
    manifest["manifest_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(json.dumps({"version": version, "labels_sha256": label_hash,
                      "manifest_sha256": manifest["manifest_sha256"], **metrics}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
