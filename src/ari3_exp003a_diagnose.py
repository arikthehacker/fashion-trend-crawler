"""EXP-003A post-hoc diagnostics (directive 037). Descriptive only: no retraining,
recalibration, threshold change, relabeling or rerun of the experiment.

Per-item outputs of the frozen run are re-derived with the frozen v0.0.2 weights and
the same input text. The script refuses to continue unless they reproduce the frozen
result.json exactly. The original v0.0.2 test is described from its frozen records
only: its labels and the append-only prediction ledger written at 2026-09-26 20:40 UTC.

The heuristics below were fixed in this file and committed before any count was computed.

usage:
  python src/ari3_exp003a_diagnose.py analyze   # writes diagnostics.json (no article text)
                                                # and a local table with text (data/store/diagnostics/)
  python src/ari3_exp003a_diagnose.py make-deck # the "EXP-003A confident errors" deck (11 items)
"""

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import statistics
import sys
from datetime import datetime, timezone

from item_store import ROOT

OUT = os.path.join(ROOT, "models", "ari3-v0.0.3", "exp003a", "diagnostics")
RESULT = os.path.join(ROOT, "models", "ari3-v0.0.3", "exp003a", "result.json")
GOLD = os.path.join(ROOT, "models", "ari3-v0.0.3", "exp003a", "gold_v1.jsonl")
DIAG = os.path.join(OUT, "diagnostics.json")
LOCAL_TABLE = os.path.join(ROOT, "data", "store", "diagnostics", "exp003a_items_with_text.csv")
DECK_LOG = os.path.join(OUT, "confident_errors_review.jsonl")
QUEUE_NAME = "exp003a_confident_errors"
DECK_TITLE = "EXP-003A confident errors"

# ---------- heuristics, fixed before computing ----------
SHORT_EXCERPT_CHARS = 80          # a stored excerpt shorter than this (after strip) is "very short"
TIME_BINS = 4                     # equal-width chronological bins over the sample's published_at range
MIN_GROUP_N = 10                  # outlet and sector groups smaller than this are pooled as "other"
FASHION_WORDS = (r"fashion|style[sd]?|styling|stylish|wear|wearing|worn|outfits?|dress(es)?|collections?|runway|"
                 r"catwalk|designers?|couture|ready-to-wear|garments?|clothing|clothes|apparel|menswear|womenswear|"
                 r"shoes?|boots?|sneakers?|heels?|bags?|handbags?|jackets?|coats?|skirts?|trousers|pants|jeans|"
                 r"denim|knit(wear)?|tailoring|tailored|suits?|looks?|trends?|wardrobe|accessories|jewel(le)?ry|"
                 r"nails?|manicure")
BEAUTY_WORDS = (r"make-?up|skin ?care|fragrances?|perfumes?|beauty|hair|haircuts?|hairstyles?|lipsticks?|mascara|"
                r"serums?|cosmetics")
BUSINESS_WORDS = (r"earnings|revenues?|profits?|shares|stocks?|ceo|chief executive|appoint(s|ed|ment)?|acqui(re|res|"
                  r"red|sition)|mergers?|deals?|invest(s|ment|ors?)|funding|ipo|quarter(ly)?|store openings?|"
                  r"opens? (a )?(new )?stores?|layoffs?|sales")
CATEGORIES = [("c", "Clear model error", "CLEAR_MODEL_ERROR"), ("a", "Ambiguous input", "AMBIGUOUS_INPUT"),
              ("l", "Possible label edge case", "POSSIBLE_LABEL_EDGE_CASE"),
              ("v", "Novel language or concept", "NOVEL_LANGUAGE_OR_CONCEPT"),
              ("i", "Insufficient text", "INSUFFICIENT_TEXT"), ("o", "Other", "OTHER")]


def _rx(words):
    return re.compile(r"\b(" + words + r")\b", re.I)


def text_class(title, excerpt):
    """explicit: fashion wording only; mixed: fashion wording plus beauty or business wording
    (likely ambiguous); indirect: no fashion wording."""
    t = f"{title or ''} {excerpt or ''}"
    fashion, beauty, business = (bool(_rx(w).search(t)) for w in (FASHION_WORDS, BEAUTY_WORDS, BUSINESS_WORDS))
    return {"fashion_wording": fashion, "beauty_wording": beauty, "business_wording": business,
            "wording": "indirect" if not fashion else "mixed" if (beauty or business) else "explicit"}


def excerpt_class(excerpt):
    n = len((excerpt or "").strip())
    return "empty" if n == 0 else "very_short" if n < SHORT_EXCERPT_CHARS else "normal"


# ---------- analysis ----------

def _items(con, ids):
    from rag_corpus import get_items
    return {e.item_id: e for e in get_items(con, ids)}


def _terms(con, rows):
    """Lexicon v1 matches by the existing deterministic matcher, in memory. Nothing is written."""
    import lexicon
    lex = lexicon.compile_lexicon(con)
    sense = {r[0] for r in con.execute("SELECT term_id FROM term_rules WHERE needs_sense_check=1")}
    out = {}
    for item_id, title, excerpt in rows:
        found = sorted({t for t, _ in lexicon.find_mentions(lexicon.item_text(title, excerpt), lex)})
        out[item_id] = {"terms": found, "countable_terms": [t for t in found if t not in sense]}
    return out


def _rate(xs):
    return {"n": len(xs), "errors": sum(not x for x in xs), "error_rate": round(1 - sum(xs) / len(xs), 4) if xs else None}


def _group(rows, key, min_n=MIN_GROUP_N):
    by = collections.defaultdict(list)
    for r in rows:
        by[key(r)].append(r)
    out, pooled = {}, []
    for k, rs in sorted(by.items(), key=lambda kv: (-len(kv[1]), str(kv[0]))):
        if len(rs) >= min_n:
            out[str(k)] = dict(_rate([r["correct"] for r in rs]), fp=sum(r["error"] == "FP" for r in rs),
                               fn=sum(r["error"] == "FN" for r in rs))
        else:
            pooled += rs
    if pooled:
        out[f"pooled (groups under {min_n})"] = dict(_rate([r["correct"] for r in pooled]),
                                                     groups=len({key(r) for r in pooled}))
    return out


def reproduce(con):
    """Per-item outputs of the frozen EXP-003A run; refuses to continue unless they match result.json."""
    import numpy as np
    import jev_spike as J
    from ari3_freeze import EMBEDDER_REVISION
    from sentence_transformers import SentenceTransformer
    gold = [json.loads(line) for line in open(GOLD, encoding="utf-8") if line.strip()]
    with open(RESULT, encoding="utf-8") as f:
        result = json.load(f)
    ids = [g["item_id"] for g in gold]
    rows = {r[0]: r for r in con.execute(
        f"SELECT item_id, title, text_excerpt FROM items WHERE item_id IN ({','.join('?' * len(ids))})", ids)}
    texts = [J.text(rows[i][1], rows[i][2]) for i in ids]
    if hashlib.sha256("\n".join(texts).encode("utf-8")).hexdigest() != result["inputs_text_sha256"]:
        raise RuntimeError("the stored text differs from the text the frozen run used")
    w = np.load(os.path.join(ROOT, "models", "ari3-v0.0.2", "weights.npz"))
    T, q = float(w["temperature"][0]), float(w["qhat"][0])
    X = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION).encode(texts, normalize_embeddings=True)
    p = 1 / (1 + np.exp(-(X @ w["coef"][0] + w["intercept"][0]) / T))
    out = []
    for g, pi in zip(gold, p):
        s = [l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok]
        out.append({"item_id": g["item_id"], "gold": g["label"], "pred": "yes" if pi >= 0.5 else "no",
                    "p_yes": round(float(pi), 4), "set": s})
    m = result["metrics"]
    acc = sum(r["gold"] == r["pred"] for r in out) / len(out)
    cov = sum(r["gold"] in r["set"] for r in out) / len(out)
    unsure = sum(len(r["set"]) == 2 for r in out) / len(out)
    if (round(acc, 10), round(cov, 10), round(unsure, 10)) != \
            (round(m["accuracy"], 10), round(m["coverage"], 10), round(m["not_sure_share"], 10)):
        raise RuntimeError("re-derived outputs do not reproduce the frozen result")
    return out, rows


def analyze(con):
    preds, text_rows = reproduce(con)
    ids = [r["item_id"] for r in preds]
    ev = _items(con, ids)
    terms = _terms(con, [text_rows[i] for i in ids])
    pubs = sorted(ev[i].published_at for i in ids)
    lo = datetime.fromisoformat(pubs[0].replace("Z", "+00:00"))
    hi = datetime.fromisoformat(pubs[-1].replace("Z", "+00:00"))
    width = (hi - lo) / TIME_BINS
    table = []
    for r in preds:
        e = ev[r["item_id"]]
        t = datetime.fromisoformat(e.published_at.replace("Z", "+00:00"))
        b = min(TIME_BINS - 1, int((t - lo) / width)) if width.total_seconds() else 0
        correct = r["gold"] == r["pred"]
        confident = len(r["set"]) == 1
        table.append({**r, "correct": correct, "confident": confident, "not_sure": len(r["set"]) == 2,
                      "error": None if correct else ("FP" if r["pred"] == "yes" else "FN"),
                      "confident_error": confident and not correct, "outlet": e.outlet,
                      "sector_group": e.coarse_group or "unknown", "lang": e.lang or "unknown",
                      "published_at": e.published_at, "time_bin": b,
                      "headline_chars": len(e.title or ""), "excerpt_chars": len((e.excerpt or "").strip()),
                      "excerpt_class": excerpt_class(e.excerpt), **text_class(e.title, e.excerpt),
                      **terms[r["item_id"]]})
    errors = [r for r in table if not r["correct"]]
    term_counts = collections.Counter(t for r in table for t in r["terms"])
    term_err = collections.Counter(t for r in errors for t in r["terms"])
    bins = [{"bin": k, "from": (lo + width * k).strftime("%Y-%m-%dT%H:%MZ"),
             "to": (lo + width * (k + 1)).strftime("%Y-%m-%dT%H:%MZ"),
             **_rate([r["correct"] for r in table if r["time_bin"] == k])} for k in range(TIME_BINS)]
    breakdown = {
        "overall": dict(_rate([r["correct"] for r in table]), fp=sum(r["error"] == "FP" for r in table),
                        fn=sum(r["error"] == "FN" for r in table)),
        "direction": {"false_positive": sum(r["error"] == "FP" for r in table),
                      "false_negative": sum(r["error"] == "FN" for r in table),
                      "fp_rate_among_gold_no": round(sum(r["error"] == "FP" for r in table)
                                                     / sum(r["gold"] == "no" for r in table), 4),
                      "fn_rate_among_gold_yes": round(sum(r["error"] == "FN" for r in table)
                                                      / sum(r["gold"] == "yes" for r in table), 4)},
        "confidence": {"confident_correct": sum(r["confident"] and r["correct"] for r in table),
                       "confident_wrong": sum(r["confident_error"] for r in table),
                       "uncertain_correct": sum(r["not_sure"] and r["correct"] for r in table),
                       "uncertain_wrong": sum(r["not_sure"] and not r["correct"] for r in table),
                       "confident_wrong_direction": dict(collections.Counter(r["error"] for r in table
                                                                            if r["confident_error"]))},
        "sector_group": _group(table, lambda r: r["sector_group"]),
        "outlet": _group(table, lambda r: r["outlet"]),
        "language": _group(table, lambda r: r["lang"]),
        "time_bins": bins,
        "lexicon": {"items_with_any_term": _rate([r["correct"] for r in table if r["terms"]]),
                    "items_without_terms": _rate([r["correct"] for r in table if not r["terms"]]),
                    "terms_in_errors": {t: {"in_errors": term_err[t], "in_sample": term_counts[t]}
                                        for t in sorted(term_err, key=lambda t: (-term_err[t], t))}},
        "excerpt_class": {k: _rate([r["correct"] for r in table if r["excerpt_class"] == k])
                          for k in ("empty", "very_short", "normal")},
        "wording": {k: dict(_rate([r["correct"] for r in table if r["wording"] == k]),
                            fp=sum(r["error"] == "FP" for r in table if r["wording"] == k),
                            fn=sum(r["error"] == "FN" for r in table if r["wording"] == k))
                    for k in ("explicit", "mixed", "indirect")},
        "wording_by_gold": {g: dict(collections.Counter(r["wording"] for r in table if r["gold"] == g))
                            for g in ("yes", "no")}}
    body = {"analysis": "EXP-003A post-hoc diagnostics, descriptive only (directive 037)",
            "post_hoc": True, "changes_exp003a": False,
            "heuristics_fixed_before_counting": {
                "short_excerpt_chars": SHORT_EXCERPT_CHARS, "time_bins": f"{TIME_BINS} equal-width bins",
                "min_group_n": MIN_GROUP_N, "fashion_words": FASHION_WORDS, "beauty_words": BEAUTY_WORDS,
                "business_words": BUSINESS_WORDS,
                "wording": "explicit = fashion words only; mixed = fashion words plus beauty or business words "
                           "(likely ambiguous); indirect = no fashion word",
                "confident": "a single-label conformal set", "lexicon": "Lexicon v1 matcher in memory, all 73 terms; "
                                                                        "countable = terms without a sense check"},
            "reproduction": "per-item outputs re-derived from the frozen weights reproduce result.json exactly",
            "breakdown": breakdown, "test_comparison": compare_test(con, table),
            "items": [{k: v for k, v in r.items()} for r in table]}
    os.makedirs(OUT, exist_ok=True)
    with open(DIAG, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    os.makedirs(os.path.dirname(LOCAL_TABLE), exist_ok=True)
    with open(LOCAL_TABLE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        cols = list(table[0])
        w.writerow(cols + ["headline", "excerpt"])
        for r in table:
            w.writerow([r[c] for c in cols] + [text_rows[r["item_id"]][1], text_rows[r["item_id"]][2]])
    return body


def compare_test(con, holdout):
    """The original v0.0.2 test (61 random-queue items), from its labels and the append-only
    prediction ledger only. Nothing is recomputed."""
    rows = con.execute(
        """SELECT l.item_id, l.label, p.predicted_label, p.calibrated_probability, p.conformal_set, i.title,
                  i.text_excerpt
           FROM labels l JOIN items i USING (item_id)
           JOIN label_predictions p ON p.item_id=l.item_id AND p.task=l.task AND p.model_version='ari3-v0.0.2'
           WHERE l.task='is_style_signal' AND l.source='human' AND l.split='test'
             AND COALESCE(l.note,'')<>'active_learning_round_1'""").fetchall()
    ev = _items(con, [r[0] for r in rows])
    terms = _terms(con, [(r[0], r[5], r[6]) for r in rows])
    test = []
    for r in rows:
        s = json.loads(r[4])
        test.append({"gold": r[1], "pred": r[2], "correct": r[1] == r[2], "set": s, "confident": len(s) == 1,
                     "sector_group": ev[r[0]].coarse_group or "unknown", "outlet": ev[r[0]].outlet,
                     "lang": ev[r[0]].lang or "unknown", "excerpt_chars": len((r[6] or "").strip()),
                     "excerpt_class": excerpt_class(r[6]), **text_class(r[5], r[6]), **terms[r[0]],
                     "error": None if r[1] == r[2] else ("FP" if r[2] == "yes" else "FN")})

    def describe(xs):
        n = len(xs)
        share = lambda f: round(sum(1 for x in xs if f(x)) / n, 4)
        lens = [x["excerpt_chars"] for x in xs]
        return {"n": n, "gold_yes_share": share(lambda x: x["gold"] == "yes"),
                "accuracy": share(lambda x: x["correct"]),
                "decisive_share": share(lambda x: x["confident"]),
                "not_sure_share": share(lambda x: len(x["set"]) == 2),
                "coverage": share(lambda x: x["gold"] in x["set"]),
                "errors": {"FP": sum(x["error"] == "FP" for x in xs), "FN": sum(x["error"] == "FN" for x in xs)},
                "confident_errors": sum(x["confident"] and not x["correct"] for x in xs),
                "sector_group_share": {k: round(v / n, 4) for k, v in
                                       collections.Counter(x["sector_group"] for x in xs).most_common()},
                "distinct_outlets": len({x["outlet"] for x in xs}),
                "top_outlets": collections.Counter(x["outlet"] for x in xs).most_common(5),
                "language_share": {k: round(v / n, 4) for k, v in collections.Counter(x["lang"] for x in xs).most_common()},
                "excerpt_chars": {"median": statistics.median(lens), "quartiles": statistics.quantiles(lens, n=4)},
                "excerpt_class_share": {k: share(lambda x, k=k: x["excerpt_class"] == k)
                                        for k in ("empty", "very_short", "normal")},
                "wording_share": {k: share(lambda x, k=k: x["wording"] == k) for k in ("explicit", "mixed", "indirect")},
                "errors_by_sector_group": {k: [sum(not x["correct"] for x in xs if x["sector_group"] == k),
                                               sum(x["sector_group"] == k for x in xs)]
                                           for k in sorted({x["sector_group"] for x in xs})},
                "errors_by_language": {k: [sum(not x["correct"] for x in xs if x["lang"] == k),
                                           sum(x["lang"] == k for x in xs)] for k in sorted({x["lang"] for x in xs})},
                "errors_by_wording": {k: [sum(not x["correct"] for x in xs if x["wording"] == k),
                                          sum(x["wording"] == k for x in xs)] for k in ("explicit", "mixed", "indirect")},
                "any_term_share": share(lambda x: bool(x["terms"])),
                "countable_term_share": share(lambda x: bool(x["countable_terms"]))}
    with open(os.path.join(ROOT, "models", "ari3-v0.0.2", "manifest.json"), encoding="utf-8") as f:
        frozen = json.load(f)["results_test"]["ari3-v0.0.2"]
    t = describe(test)
    return {"source": "v0.0.2 test labels plus the append-only prediction ledger (2026-09-26 20:40 UTC); "
                      "nothing recomputed",
            "ledger_matches_frozen_test": {"accuracy": [t["accuracy"], round(frozen["accuracy"], 4)],
                                           "decisive_share": [t["decisive_share"], round(frozen["decisive_share"], 4)],
                                           "coverage": [t["coverage"], round(frozen["coverage"], 4)]},
            "v002_test": t, "exp003a_holdout": describe(holdout)}


# ---------- confident-error deck ----------

def make_deck(con):
    import label_tool
    import jev_spike as J
    from ari3_freeze import sha256_file
    with open(DIAG, encoding="utf-8") as f:
        diag = json.load(f)
    errs = [r for r in diag["items"] if r["confident_error"]]
    if len(errs) != 11:
        raise RuntimeError(f"expected 11 confident errors, found {len(errs)}")
    text = {r[0]: J.text(r[1], r[2]) for r in con.execute(
        f"SELECT item_id, title, text_excerpt FROM items WHERE item_id IN ({','.join('?' * len(errs))})",
        [r["item_id"] for r in errs])}
    tasks = []
    for r in sorted(errs, key=lambda r: r["item_id"]):
        body = ("DIAGNOSTIC ONLY. This does not change the EXP-003A gold label, and the item is not being relabeled.\n\n"
                f"item {r['item_id']}  |  {r['outlet']}  |  {r['published_at'][:10]}  |  {r['lang']}\n\n"
                f"FROZEN MODEL INPUT (headline + stored excerpt, as the model read it)\n{text[r['item_id']]}\n\n"
                f"Owner gold label: {r['gold'].upper()}\n"
                f"Frozen v0.0.2 prediction: {r['pred'].upper()} (confident: prediction set {{{r['pred']}}})\n"
                f"Calibrated probability of style: {r['p_yes']:.3f}\n"
                f"Lexicon v1 terms found: {', '.join(r['terms']) or 'none'}")
        tasks.append({"task_id": f"exp003a:{r['item_id']}", "question_id": "exp003a", "kind": "exp003a_error_category",
                      "target": f"item {r['item_id']}",
                      "question": "Why might frozen v0.0.2 have been confidently wrong here? (diagnostic only)",
                      "prompt": "Pick the best description. The gold label stays as it is.",
                      "options": [{"key": k, "label": label, "value": v} for k, label, v in CATEGORIES],
                      "body": body})
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": DECK_TITLE, "notes": True,
             "outputs_sha256": sha256_file(RESULT),
             "reviews_path": os.path.relpath(DECK_LOG, ROOT).replace(os.sep, "/"), "tasks": tasks, "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue), tasks


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["analyze", "make-deck"])
    args = ap.parse_args(argv)
    from rag_corpus import open_corpus
    con = open_corpus()  # read-only: the diagnostics never write to the store
    try:
        if args.cmd == "analyze":
            body = analyze(con)
            body = {k: v for k, v in body.items() if k != "items"}
        else:
            path, tasks = make_deck(con)
            body = {"queue": path, "title": DECK_TITLE, "tasks": len(tasks)}
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
