"""EXP-009: what predicts the editor's report decisions best? (pre-registration:
experiments/exp-009-editor-taste-predictors/PREREGISTRATION.md)

Walk-forward evaluation on the signal cards of weeks 2 to 7 (report dates 2026-10-18 to 2026-11-22). Every
method guesses the editor's decision on a card using only what was known before that card's week:

  M0 always keep        every card is kept
  M1 same as last time  the editor's decision on the same term in the most recent earlier week; a term
                        with no earlier card is kept
  M2 taste model        a logistic regression (pure Python, L2) on fixed card features and the editor's
                        history on the term, trained only on the weeks before the target week
  M3 DeepSeek           EXP-007's sealed thinking-off answers in the app's option order (no new calls)
  M4 DeepSeek + memory  EXP-007's prompt plus the editor's earlier decisions and labels on the same term
                        (decisions and labels only, the owner's choice), app order, one new call per card

usage:
  python src/exp009.py freeze-protocol   # once, before any call or score; then commit and push
  python src/exp009.py estimate-cost
  python src/exp009.py render-example --week W [--card ID]
  python src/exp009.py run               # M4 only, once; needs ARI3_LIVE_LLM=approved
  python src/exp009.py status            # counts only
  python src/exp009.py compare           # after the M4 run is sealed and pushed
"""

import argparse
import functools
import json
import math
import os
import random
import sys
from datetime import datetime, timezone

import exp007 as e7
import exp008 as e8
import report_review as rr
from item_store import ROOT

EXP = os.path.join(ROOT, "experiments", "exp-009-editor-taste-predictors")
PREREG = os.path.join(EXP, "PREREGISTRATION.md")
PROTOCOL_V1 = os.path.join(EXP, "protocol", "protocol_v1.json")
PROTOCOL = os.path.join(EXP, "protocol", "protocol_v2.json")
MANIFEST = os.path.join(EXP, "runs", "sealed_manifest.json")
RESULT = os.path.join(EXP, "runs", "comparison.json")
BLIND = os.path.join(ROOT, "data", "store", "blind", "exp009")
OUT = os.path.join(BLIND, "outputs_memory.jsonl")
DETAIL = os.path.join(BLIND, "predictions_detail.md")
WEEKS = e7.WEEKS
TARGET_WEEKS = WEEKS[1:]
METHODS = ("M0_always_keep", "M1_same_as_last_time", "M2_taste_model", "M3_deepseek", "M4_deepseek_memory")
HYPOTHESES = {"H1": ("M2_taste_model", "M3_deepseek"), "H2": ("M4_deepseek_memory", "M3_deepseek"),
              "H3": ("M2_taste_model", "M1_same_as_last_time")}
COST_CAP_USD = 0.50
BOOTSTRAP = {"resamples": 10000, "seed": 9009, "unit": "signal card", "interval": "percentile 95%"}
MODEL = {"kind": "logistic regression, batch gradient descent on standardized features",
         "l2": 0.1, "learning_rate": 0.5, "iterations": 2000, "threshold": 0.5,
         "target": "keep (1) against drop, watchlist or merge (0)"}
CODE_FILES = e8.CODE_FILES + ("exp009.py",)
MEMORY_HEADING = "THE EDITOR'S EARLIER DECISIONS ON THIS TERM (decisions and labels only, from earlier weeks)"
NO_MEMORY = "None. This term has no card in an earlier week."
OPENING_FROM = "followed by the editor's definitions."
OPENING_TO = "followed by the editor's definitions and the editor's earlier decisions on this term."
CONF_LEVEL = {"low": 0.0, "medium": 1.0, "high": 2.0}
_E7_RENDER = e7.render


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- cards and the editor's history ----------

@functools.lru_cache(maxsize=None)
def signal_cards(week):
    """The week's signal cards (cached; callers must not change them)."""
    return tuple(c for c in e7.required_cards(e7.load_week(week)) if c["kind"] == "signal")


def history(term, week, editor):
    """The editor's decisions on this term in weeks before `week`, oldest first: [(week, payload)]."""
    out = []
    for w in WEEKS:
        if w >= week:
            break
        for c in signal_cards(w):
            if c["signal_id"] == term and c["card_id"] in editor.get(w, {}):
                out.append((w, editor[w][c["card_id"]]))
    return out


def excluded(week, card, editor):
    """EXP-007's exclusions: undecided, decided before the plan, or looked up."""
    e = editor.get(week, {}).get(card["card_id"])
    return (e is None or (week, card["card_id"]) in e7.PRE_PLAN_CARDS
            or e7.LOOKED_UP in (e.get("thoughts") or "").lower())


# ---------- M1 ----------

def same_as_last_time(term, week, editor):
    h = history(term, week, editor)
    return h[-1][1]["decision"] if h else "keep"


# ---------- M2: features and a small logistic regression ----------

FEATURES = (["log_items", "log_outlets", "sectors", "days", "weaknesses", "baseline_confidence"]
            + [f"type_{t}" for t in rr.SIGNAL_TYPES]
            + ["seen_before", "last_kept", "keep_rate_before", "times_seen_before"])


def features(card, week, editor):
    h = history(card["signal_id"], week, editor)
    kept = [p["decision"] == "keep" for _, p in h]
    row = {"log_items": math.log1p(card["items"]), "log_outlets": math.log1p(card["outlets"]),
           "sectors": float(len(card.get("sectors") or {})), "days": float(len(card.get("dates") or [])),
           "weaknesses": float(len(card.get("weaknesses") or [])),
           "baseline_confidence": CONF_LEVEL.get(card["baseline_confidence"], 1.0),
           "seen_before": 1.0 if h else 0.0, "last_kept": 1.0 if kept and kept[-1] else 0.0,
           "keep_rate_before": sum(kept) / len(kept) if kept else 0.0, "times_seen_before": float(len(h))}
    row.update({f"type_{t}": 1.0 if card["type"] == t else 0.0 for t in rr.SIGNAL_TYPES})
    return [row[f] for f in FEATURES]


def fit(X, y, model=MODEL):
    """Deterministic L2 logistic regression. Returns (means, scales, weights, bias)."""
    n, k = len(X), len(X[0])
    means = [sum(r[j] for r in X) / n for j in range(k)]
    scales = []
    for j in range(k):
        var = sum((r[j] - means[j]) ** 2 for r in X) / n
        scales.append(math.sqrt(var) if var > 1e-12 else 1.0)
    Z = [[(r[j] - means[j]) / scales[j] for j in range(k)] for r in X]
    w, b = [0.0] * k, 0.0
    for _ in range(model["iterations"]):
        gw, gb = [0.0] * k, 0.0
        for z, t in zip(Z, y):
            s = b + sum(wj * zj for wj, zj in zip(w, z))
            p = 1.0 / (1.0 + math.exp(-s)) if s >= 0 else math.exp(s) / (1.0 + math.exp(s))
            d = p - t
            gb += d
            for j in range(k):
                gw[j] += d * z[j]
        b -= model["learning_rate"] * gb / n
        w = [wj - model["learning_rate"] * (gj / n + model["l2"] * wj) for wj, gj in zip(w, gw)]
    return means, scales, w, b


def predict_proba(params, x):
    means, scales, w, b = params
    s = b + sum(wj * (xj - m) / sc for wj, xj, m, sc in zip(w, x, means, scales))
    return 1.0 / (1.0 + math.exp(-s)) if s >= 0 else math.exp(s) / (1.0 + math.exp(s))


def taste_model(editor, model=MODEL):
    """{(week, card_id): probability of keep}, each week predicted from a model fitted on earlier weeks only.
    Also returns the fitted weights per target week (standardized units)."""
    probs, weights = {}, {}
    for target in TARGET_WEEKS:
        X, y = [], []
        for w in WEEKS:
            if w >= target:
                break
            for c in signal_cards(w):
                e = editor.get(w, {}).get(c["card_id"])
                if e is not None:
                    X.append(features(c, w, editor))
                    y.append(1.0 if e["decision"] == "keep" else 0.0)
        params = fit(X, y, model)
        weights[target] = {"trained_on_cards": len(X), "bias": round(params[3], 4),
                           "weights": {f: round(v, 4) for f, v in zip(FEATURES, params[2])}}
        for c in signal_cards(target):
            probs[(target, c["card_id"])] = predict_proba(params, features(c, target, editor))
    return probs, weights


# ---------- M4: prompt ----------

def memory_lines(term, week, editor):
    lines = []
    for w, p in history(term, week, editor):
        parts = [p["decision"]]
        if p.get("volatility"):
            parts.append(f"volatility {p['volatility']}")
        if p.get("confidence"):
            parts.append(f"confidence {p['confidence']}")
        lines.append(f"- week ending {w}: " + ", ".join(parts))
    return "\n".join(lines) or NO_MEMORY


def render(queue, card, definitions, memory, order="original"):
    """EXP-007's prompt with one change: the term's memory after the definitions."""
    system, user = _E7_RENDER(queue, card, definitions, order)
    anchor = f"DEFINITIONS (your words)\n\n{definitions}"
    if system.count(OPENING_FROM) != 1 or user.count(anchor) != 1:
        raise RuntimeError("the EXP-007 prompt no longer has the expected anchors")
    return (system.replace(OPENING_FROM, OPENING_TO),
            user.replace(anchor, f"{anchor}\n\n{MEMORY_HEADING}\n\n{memory}"))


def _decide(queue, card, definitions, memory, provider, cost_fn):
    e7.render = lambda q, c, d, o="original": render(q, c, d, memory, o)
    try:
        return e7.decide(queue, card, definitions, "original", provider, cost_fn)
    finally:
        e7.render = _E7_RENDER


# ---------- protocol ----------

def code_sha():
    return {f: e7.sha_file(os.path.join(e7.SRC, f)) for f in CODE_FILES}


def protocol_body():
    return {"experiment": "EXP-009 editor-taste predictors, walk-forward", "version": "exp009-protocol-v2",
            "decided_by": "the owner, 2026-11-25",
            "supersedes": "protocol/protocol_v1.json. No call or score ever ran under it: its freeze check compared "
                          "the hypotheses as tuples against the same values read back from JSON as lists, and refused "
                          "the run. v2 fixes only that comparison; every method, feature and setting is unchanged.",
            "protocol_v1_sha256": e7.sha_file(PROTOCOL_V1), "preregistration_sha256": e7.sha_file(PREREG),
            "target_weeks": list(TARGET_WEEKS), "methods": list(METHODS), "hypotheses": HYPOTHESES,
            "model": MODEL, "features": FEATURES, "m1_fallback": "keep",
            "memory": "the editor's decision, volatility and confidence on the same term in earlier weeks",
            "definitions": {"sha256": e7.rd.sha256(), "panel_text_sha256": e7.sha_text(e7.definitions_text())},
            "weeks": e7.deck_fingerprints(), "editor_logs_manifest_sha256": e7.sha_file(e7.EDITOR_MANIFEST),
            "exp007_thinking_off_outputs_sha256": e8._exp007_manifest()["outputs_sha256"],
            "reader": {"orders": ["original"], "settings": e7.arm_settings("thinking_off")},
            "running_cost_cap_usd": COST_CAP_USD, "bootstrap": BOOTSTRAP, "code_sha256": code_sha(),
            "frozen_at": _now()}


def check_frozen():
    with open(PROTOCOL, encoding="utf-8") as f:
        p = json.load(f)
    now = json.loads(json.dumps(protocol_body()))  # compare as stored: tuples become lists
    changed = [k for k in p if k != "frozen_at" and p[k] != now.get(k)]
    if changed:
        raise RuntimeError(f"a frozen input changed: {changed}")
    return p


def max_cost(definitions, editor):
    import exp005 as v1
    from llm_deepseek import PRICING
    price = PRICING[v1.PROVIDER_SETTINGS["model"]]
    total, calls = 0.0, 0
    for w in TARGET_WEEKS:
        q = e7.load_week(w)
        for c in signal_cards(w):
            system, user = render(q, c, definitions, memory_lines(c["signal_id"], w, editor))
            total += e7.MAX_ATTEMPTS * ((len(system) + len(user) + 600) * price["input_cache_miss"][1]
                                        + e7.ARMS["thinking_off"]["max_tokens"] * price["output"][1]) / 1_000_000
            calls += 1
    return {"max_total_usd": round(total, 4), "first_calls": calls, "running_cap_usd": COST_CAP_USD,
            "assumptions": "1 token per character, 2 attempts, full max_tokens output, peak prices"}


# ---------- run (M4) ----------

def run(provider=None, out_path=OUT, manifest_path=MANIFEST):
    if os.path.exists(out_path) or os.path.exists(manifest_path):
        raise RuntimeError("EXP-009 has already run. It runs once.")
    live = provider is None
    if live:
        import rag_select as rs
        ok, info = rs.rule_is_committed_and_pushed(PROTOCOL)
        if not ok:
            raise RuntimeError(f"protocol: {info}")
        check_frozen()
    definitions, editor = e7.definitions_text(), e8.editor_decisions()
    cost = max_cost(definitions, editor)
    cost_fn = None
    if live:
        import exp005 as v1
        import llm_deepseek
        try:
            from dotenv import find_dotenv, load_dotenv
            load_dotenv(find_dotenv(usecwd=True))  # the key stays in the process; never printed
        except ImportError:
            pass
        p = v1.PROVIDER_SETTINGS
        provider = llm_deepseek.DeepSeekProvider(
            thinking=p["thinking"], model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
            max_tokens=e7.ARMS["thinking_off"]["max_tokens"], timeout=p["timeout_s"],
            max_retries=p["transport_retries"], allow_live=True)
        cost_fn = llm_deepseek.estimate_cost
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    started, records, spent, stopped = _now(), [], 0.0, False
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        for w in TARGET_WEEKS:
            q = e7.load_week(w)
            for c in signal_cards(w):
                if spent >= COST_CAP_USD:
                    stopped = True
                    break
                r = _decide(q, c, definitions, memory_lines(c["signal_id"], w, editor), provider, cost_fn)
                r["arm"] = "exp009_memory"
                if r.get("status") == "provider_error" and any(
                        s in r.get("error", "") for s in ("not set", "HTTP 401", "HTTP 402")):
                    raise RuntimeError(f"stopped: {r['error'][:80]}")
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                records.append(r)
                spent += sum(x.get("estimated_cost_usd") or 0 for x in r["attempts"])
    body = dict(e7.seal_counts(records), started_at=started, finished_at=_now(), stopped_by_cost_cap=stopped,
                outputs_sha256=e7.sha_file(out_path), max_cost_estimate=cost,
                provider=provider.config() if hasattr(provider, "config") else "scripted",
                note="counts only; the decisions stay sealed in data/store/blind/exp009/ until compare")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def status():
    if not os.path.exists(OUT):
        return {"records": 0, "sealed": False}
    return {"sealed": os.path.exists(MANIFEST), **e7.seal_counts(e7.load_records(OUT))}


# ---------- compare ----------

def predictions(editor, m3_records, m4_records):
    """[(week, card_id, editor decision, {method: four-way decision or None}, {method: keep bool})]."""
    probs, weights = taste_model(editor)
    m3 = {(r["week"], r["card_id"]): r for r in m3_records if r["order"] == "original" and r["status"] == "decided"}
    m4 = {(r["week"], r["card_id"]): r for r in m4_records if r["status"] == "decided"}
    rows, skipped = [], {"excluded": 0, "ai_invalid_or_missing": 0}
    for w in TARGET_WEEKS:
        for c in signal_cards(w):
            if excluded(w, c, editor):
                skipped["excluded"] += 1
                continue
            k = (w, c["card_id"])
            if k not in m3 or k not in m4:
                skipped["ai_invalid_or_missing"] += 1
                continue
            four = {"M0_always_keep": "keep", "M1_same_as_last_time": same_as_last_time(c["signal_id"], w, editor),
                    "M2_taste_model": None, "M3_deepseek": m3[k]["payload"]["decision"],
                    "M4_deepseek_memory": m4[k]["payload"]["decision"]}
            keep = {m: d == "keep" for m, d in four.items() if d is not None}
            keep["M2_taste_model"] = probs[k] >= MODEL["threshold"]
            rows.append({"week": w, "card_id": c["card_id"], "name": c["name"], "editor": editor[w][c["card_id"]],
                         "four": four, "keep": keep, "p_keep": round(probs[k], 4),
                         "seen_before": bool(history(c["signal_id"], w, editor))})
    return rows, skipped, weights


def delta_ci(rows, a, b, bootstrap=BOOTSTRAP):
    """Paired bootstrap of kappa(a) - kappa(b) on keep against not-keep."""
    def k(rs, m):
        return e7.kappa([(r["editor"]["decision"] == "keep", r["keep"][m]) for r in rs])
    rng = random.Random(bootstrap["seed"])
    ds = []
    for _ in range(bootstrap["resamples"]):
        s = [rows[rng.randrange(len(rows))] for _ in rows]
        ka, kb = k(s, a), k(s, b)
        if None not in (ka, kb):
            ds.append(ka - kb)
    ds.sort()
    ka, kb = k(rows, a), k(rows, b)
    ci = ([round(ds[int(0.025 * len(ds))], 4), round(ds[min(len(ds) - 1, int(0.975 * len(ds)))], 4)]
          if ds else None)
    verdict = ("not computable" if ci is None else "supported" if ci[0] > 0
               else "reversed" if ci[1] < 0 else "not supported")
    return {"kappa_a": ka, "kappa_b": kb, "delta": round(ka - kb, 4) if None not in (ka, kb) else None,
            "ci": ci, "verdict": verdict, "resampled_with_kappa": len(ds)}


def score(rows):
    out = {}
    for m in METHODS:
        out[m] = {"keep_vs_not": e7.agreement([(r["editor"]["decision"] == "keep", r["keep"][m]) for r in rows]),
                  "kept": sum(r["keep"][m] for r in rows)}
        if m != "M2_taste_model":
            out[m]["four_way"] = e7.agreement([(r["editor"]["decision"], r["four"][m]) for r in rows])
        out[m]["per_week"] = {w: e7.agreement([(r["editor"]["decision"] == "keep", r["keep"][m])
                                               for r in rows if r["week"] == w]) for w in TARGET_WEEKS}
        for label, sel in (("terms_seen_before", True), ("new_terms", False)):
            out[m][label] = e7.agreement([(r["editor"]["decision"] == "keep", r["keep"][m])
                                          for r in rows if r["seen_before"] is sel])
    return out


def run_compare():
    import rag_select as rs
    if os.path.exists(RESULT):
        raise RuntimeError("the comparison already exists")
    for path in (PROTOCOL, MANIFEST):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    with open(MANIFEST, encoding="utf-8") as f:
        if e7.sha_file(OUT) != json.load(f)["outputs_sha256"]:
            raise RuntimeError("the sealed EXP-009 outputs changed")
    out7 = e7.ARMS["thinking_off"]["out"]
    if e7.sha_file(out7) != e8._exp007_manifest()["outputs_sha256"]:
        raise RuntimeError("the sealed EXP-007 outputs changed")
    editor = e8.editor_decisions()
    rows, skipped, weights = predictions(editor, e7.load_records(out7), e7.load_records(OUT))
    body = {"n_cards": len(rows), "skipped": skipped, "editor_kept": sum(r["editor"]["decision"] == "keep" for r in rows),
            "methods": score(rows), "hypotheses": {h: dict(delta_ci(rows, a, b), a=a, b=b)
                                                    for h, (a, b) in HYPOTHESES.items()},
            "all_pairs_descriptive": {f"{a} - {b}": delta_ci(rows, a, b) for i, a in enumerate(METHODS)
                                      for b in METHODS[i + 1:] if a != "M0_always_keep"},
            "taste_model_weights": weights, "compared_at": _now(), "code_sha256": code_sha()}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    write_detail(rows)
    return body


def write_detail(rows):
    lines = ["# EXP-009 predictions (local only)", "",
             "| Week | Card | Editor | M1 | M2 p(keep) | M3 | M4 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        f = r["four"]
        lines.append(f"| {r['week']} | {r['name']} | {r['editor']['decision']} | {f['M1_same_as_last_time']} | "
                     f"{r['p_keep']} | {f['M3_deepseek']} | {f['M4_deepseek_memory']} |")
    with open(DETAIL, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-protocol", "estimate-cost", "render-example", "run", "status", "compare"])
    ap.add_argument("--week", default=TARGET_WEEKS[-1])
    ap.add_argument("--card", default=None)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "freeze-protocol":
            os.makedirs(os.path.dirname(PROTOCOL), exist_ok=True)
            with open(PROTOCOL, "x", encoding="utf-8", newline="\n") as f:
                json.dump(protocol_body(), f, indent=1, ensure_ascii=False)
            body = {"protocol_sha256": e7.sha_file(PROTOCOL)}
        elif args.cmd == "estimate-cost":
            body = max_cost(e7.definitions_text(), e8.editor_decisions())
        elif args.cmd == "render-example":
            q, editor = e7.load_week(args.week), e8.editor_decisions()
            card = next(c for c in signal_cards(args.week) if args.card in (None, c["card_id"]))
            system, user = render(q, card, e7.definitions_text(), memory_lines(card["signal_id"], args.week, editor))
            print(f"--- system ---\n{system}\n\n--- user ---\n{user}")
            return 0
        elif args.cmd == "run":
            body = run()
        elif args.cmd == "status":
            body = status()
        else:
            body = run_compare()
    except (RuntimeError, FileExistsError) as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
