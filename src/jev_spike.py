"""ARI3LLA-Jev spike: is_style_signal from human gold labels.

Pipeline: multilingual sentence embeddings -> logistic regression (train split)
-> temperature scaling (calibration split) -> split conformal sets (calibration
split) -> scores on the untouched test split. Every test and unlabeled
prediction is written to the append-only label_predictions table.

Usage:
    python src/jev_spike.py            # train, evaluate, write predictions
    python src/jev_spike.py --dry-run  # evaluate only, write nothing
"""

import argparse
import json
import math
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression

from item_store import DEFAULT_DB, connect, utc_now

TASK = "is_style_signal"
MODEL_VERSION = "jev-v0.0.1-spike"
EMBEDDER = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ALPHA = 0.10  # conformal target: 90% coverage


def text(title, excerpt):
    return f"{title or ''}. {excerpt or ''}"[:1000]


def fit_temperature(logits, y):
    """Grid search the temperature that minimizes calibration-split log loss."""
    best_t, best_nll = 1.0, float("inf")
    for t in np.exp(np.linspace(math.log(0.05), math.log(20), 400)):
        p = 1 / (1 + np.exp(-logits / t))
        p = np.clip(p, 1e-9, 1 - 1e-9)
        nll = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
        if nll < best_nll:
            best_t, best_nll = t, nll
    return best_t


def ece(p, y, bins=5):
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi) if hi < 1 else (p >= lo) & (p <= hi)
        if m.any():
            total += m.mean() * abs(p[m].mean() - y[m].mean())
    return total


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    con = connect(args.db)

    rows = con.execute(
        """SELECT l.item_id, l.label, l.split, i.title, i.text_excerpt
           FROM labels l JOIN items i USING (item_id)
           WHERE l.task=? AND l.source='human'""", (TASK,)).fetchall()
    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer(EMBEDDER)

    X = emb.encode([text(r[3], r[4]) for r in rows], normalize_embeddings=True)
    y = np.array([1 if r[1] == "yes" else 0 for r in rows])
    split = np.array([r[2] for r in rows])
    tr, ca, te = split == "train", split == "calibration", split == "test"

    clf = LogisticRegression(C=1.0, max_iter=2000).fit(X[tr], y[tr])
    T = fit_temperature(clf.decision_function(X[ca]), y[ca])

    def prob(Xs):
        return 1 / (1 + np.exp(-clf.decision_function(Xs) / T))

    # Split conformal: nonconformity = 1 - p(true label) on calibration.
    pc = prob(X[ca])
    scores = np.where(y[ca] == 1, 1 - pc, pc)
    n = len(scores)
    q_level = min(1.0, math.ceil((n + 1) * (1 - ALPHA)) / n)
    qhat = float(np.quantile(scores, q_level, method="higher"))

    def conformal(p):
        s = []
        if 1 - p <= qhat:
            s.append("yes")
        if p <= qhat:
            s.append("no")
        return s

    pt_raw = 1 / (1 + np.exp(-clf.decision_function(X[te])))
    pt = prob(X[te])
    yt = y[te]
    pred = (pt >= 0.5).astype(int)
    correct = int((pred == yt).sum())
    nt = len(yt)
    tp = int(((pred == 1) & (yt == 1)).sum())
    fp = int(((pred == 1) & (yt == 0)).sum())
    fn = int(((pred == 0) & (yt == 1)).sum())
    sets = [conformal(p) for p in pt]
    covered = sum(("yes" if t else "no") in s for s, t in zip(sets, yt))
    singletons = sum(len(s) == 1 for s in sets)
    majority = max(yt.mean(), 1 - yt.mean())

    report = {
        "model_version": MODEL_VERSION, "embedder": EMBEDDER, "task": TASK,
        "n_train": int(tr.sum()), "n_calibration": int(ca.sum()), "n_test": nt,
        "test_accuracy": correct / nt, "test_accuracy_95ci": wilson(correct, nt),
        "majority_baseline": float(majority),
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "temperature": float(T),
        "ece_before_scaling": float(ece(pt_raw, yt)), "ece_after_scaling": float(ece(pt, yt)),
        "conformal_target_coverage": 1 - ALPHA, "conformal_qhat": qhat,
        "conformal_test_coverage": covered / nt,
        "conformal_singleton_share": singletons / nt,
        "created_at": utc_now(),
    }
    print(json.dumps(report, indent=2))

    if not args.dry_run:
        unl = con.execute(
            """SELECT item_id, title, text_excerpt FROM items
               WHERE text_excerpt IS NOT NULL AND item_id NOT IN
                 (SELECT item_id FROM labels WHERE task=? AND source='human')""", (TASK,)).fetchall()
        ids = [r[0] for r in unl]
        pu = prob(emb.encode([text(r[1], r[2]) for r in unl], normalize_embeddings=True)) if unl else []
        test_ids = [r[0] for r, m in zip(rows, te) if m]
        now = utc_now()
        batch = [(i, float(p)) for i, p in zip(test_ids + ids, list(pt) + list(pu))]
        con.executemany(
            """INSERT INTO label_predictions (item_id, task, model_version, predicted_label,
                 probability, calibrated_probability, conformal_set, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            [(i, TASK, MODEL_VERSION, "yes" if p >= 0.5 else "no", None, p,
              json.dumps(conformal(p)), now) for i, p in batch])
        con.commit()
        uncertain = sum(len(conformal(p)) != 1 for _, p in batch[len(test_ids):])
        print(f"Wrote {len(batch)} predictions. Unlabeled items with an uncertain set: {uncertain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
