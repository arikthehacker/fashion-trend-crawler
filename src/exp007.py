"""EXP-007: AI labeler alignment on the weekly report decisions (pre-registration:
experiments/exp-007-report-labeler-alignment/PREREGISTRATION.md).

A zero-shot LLM decides every required card of the seven prepared weeks from exactly what
ARI3 Review shows the editor (title, card text, form fields and option lists, and her
definitions), twice: in the app's option order and with every option list reversed. Its
answers are sealed in data/store/blind/exp007/ (local, never printed) until the editor has
finished her own decisions. Then her decision logs are fingerprinted and both are compared.

This module never opens the editor's decision logs except in `seal-editor` and `compare`,
which run only after she says the backlog is done.

usage:
  python src/exp007.py render-example     # one rendered prompt (for review; no call)
  python src/exp007.py freeze-protocol    # once, before any call; then commit and push
  python src/exp007.py estimate-cost
  python src/exp007.py run                # once; needs ARI3_LIVE_LLM=approved
  python src/exp007.py status             # counts only, never decisions
  python src/exp007.py seal-editor        # after the editor's backlog is done; then commit and push
  python src/exp007.py compare            # unseal and compare
"""

import argparse
import collections
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import report_definitions as rd
import report_review as rr
from item_store import ROOT
from taxonomy import ORIGIN_CLASSIFICATIONS, VOLATILITY_LABELS

SRC = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(ROOT, "experiments", "exp-007-report-labeler-alignment")
PROTOCOL = os.path.join(EXP, "protocol", "protocol_v1.json")
SEALED_MANIFEST = os.path.join(EXP, "runs", "sealed_manifest.json")
EDITOR_MANIFEST = os.path.join(EXP, "runs", "editor_logs_manifest.json")
RESULT = os.path.join(EXP, "runs", "comparison.json")
BLIND = os.path.join(ROOT, "data", "store", "blind", "exp007")
OUTPUTS = os.path.join(BLIND, "ai_decisions.jsonl")
DETAIL = os.path.join(BLIND, "comparison_detail.md")
QUEUES = os.path.join(ROOT, "data", "store", "queues")
WEEKS = ("2026-10-11", "2026-10-18", "2026-10-25", "2026-11-01", "2026-11-08", "2026-11-15", "2026-11-22")
PRE_PLAN_CARDS = {("2026-10-11", "signal:sneaker"), ("2026-10-11", "signal:denim")}  # decided before this plan
ORDERS = ("original", "swapped")
MAX_ATTEMPTS = 2  # one call, one retry only when the answer cannot be saved by the app's rules
GATE_USD = 5.0
LOOKED_UP = "[looked up]"
CODE_FILES = ("exp007.py", "report_review.py", "report_definitions.py", "llm_deepseek.py", "llm_provider.py")
DUP_OPTIONS = ["one story: count once", "separate pieces: count each"]

OPENING_SIGNAL = (
    "You are filling in one card of the \"Report decisions\" deck in ARI3 Review, for a weekly report of the "
    "ARI3LLA INDEX. Below is exactly what the card shows: its title, its text and its form fields with their "
    "options, followed by the editor's definitions. Use only what is shown. Return one JSON object with the keys "
    "decision, merge_into, type, confidence, volatility, origin, name, remove_item_ids and thoughts. Write every "
    "value exactly as one of the options shown. Use null for a field left empty, and an empty list for "
    "remove_item_ids if none.")
OPENING_DUPLICATE = (
    "You are filling in one card of the \"Report decisions\" deck in ARI3 Review, for a weekly report of the "
    "ARI3LLA INDEX. Below is exactly what the card shows: its title, its text and its form fields with their "
    "options, followed by the editor's definitions. Use only what is shown. Return one JSON object with the keys "
    "collapse (true for \"one story: count once\", false for \"separate pieces: count each\") and thoughts.")
SAVE_RULES = ("The app will not save if:\na kept signal needs a volatility label\n"
              "a kept signal needs the editor's thoughts (they become the editor note)\n"
              "choose which signal this merges into")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def code_sha():
    return {f: sha_file(os.path.join(SRC, f)) for f in CODE_FILES}


# ---------- decks ----------

def load_week(week, queues=QUEUES):
    with open(os.path.join(queues, f"report_{week}.json"), encoding="utf-8") as f:
        q = json.load(f)
    if q.get("kind") != "report_decisions" or q["report_date"] != week:
        raise RuntimeError(f"{week}: not a report decisions deck")
    return q


def required_cards(queue):
    return [c for c in queue["cards"] if c["kind"] in ("signal", "duplicate")]


# ---------- prompt ----------

def _opts(values, order):
    values = list(values)
    return values if order == "original" else values[::-1]


def render(queue, card, definitions, order="original"):
    """(system, user): the [ADDED] opening and the [APP] card, as protocol/prompt_v1.md specifies."""
    if card["kind"] == "signal":
        names = [n for n, _ in rr.merge_choices(queue, card)]
        conf = [f"baseline ({card['baseline_confidence']})"] + list(rr.CONFIDENCE)
        fields = [
            "Decision: " + " / ".join(_opts(rr.DECISIONS, order)),
            "Merge into (only for merge): " + " / ".join(_opts(names, order)),
            "Type: " + " / ".join(_opts(rr.SIGNAL_TYPES, order)) + f"   (preset: {card['type']})",
            "Confidence: " + " / ".join(_opts(conf, order)) + "   (preset: baseline)",
            "Volatility (needed to keep): " + " / ".join(_opts(VOLATILITY_LABELS, order)),
            "Origin: " + " / ".join(_opts(ORIGIN_CLASSIFICATIONS, order)) + "   (preset: unclear)",
            f"Name as published: (preset: {card['name']})",
            "Item IDs to remove (comma-separated)",
            "Your thoughts (for a kept signal they become your editor note)"]
        title, opening, tail = card["name"], OPENING_SIGNAL, f"\n\n{SAVE_RULES}"
    else:
        fields = ["Decision: " + " / ".join(_opts(DUP_OPTIONS, order)), "Your thoughts (optional)"]
        title, opening, tail = "Possible duplicates", OPENING_DUPLICATE, ""
    user = (f"{queue['title']}\n\n{title}\n\n{rr.card_text(card)}\n\n" + "\n".join(fields)
            + f"\n\nDEFINITIONS (your words)\n\n{definitions}" + tail)
    return opening, user


def definitions_text():
    """The definitions exactly as the app's panel shows them. Refuses an incomplete file."""
    problems = rd.problems()
    if problems:
        raise RuntimeError(f"the definitions are not complete: {problems[:5]}")
    return rd.panel_text()


# ---------- answers ----------

def to_payload(queue, card, answer):
    """The AI's JSON mapped to what the app would save, or raise ValueError with the reasons."""
    if not isinstance(answer, dict):
        raise ValueError("the answer is not a JSON object")
    thoughts = answer.get("thoughts") or ""
    if not isinstance(thoughts, str):
        raise ValueError("thoughts must be text")
    if card["kind"] == "duplicate":
        payload = {"thoughts": thoughts.strip(), "collapse": answer.get("collapse")}
    else:
        names = dict(rr.merge_choices(queue, card))
        merge = answer.get("merge_into")
        conf = answer.get("confidence") or ""
        conf = "" if str(conf).startswith("baseline") else conf
        origin = answer.get("origin") or ""
        remove = answer.get("remove_item_ids") or []
        if not isinstance(remove, list) or not all(isinstance(i, int) for i in remove):
            raise ValueError("remove_item_ids must be a list of item IDs")
        typ = answer.get("type") or ""
        name = (answer.get("name") or "").strip()
        payload = {"thoughts": thoughts.strip(), "decision": answer.get("decision"),
                   "merge_into": names.get(merge) if merge else None,
                   "name": "" if name == card["name"] else name, "type": "" if typ == card["type"] else typ,
                   "confidence": conf, "volatility": answer.get("volatility") or "",
                   "origin": "" if origin == "unclear" else origin, "remove_item_ids": remove}
        if merge and payload["merge_into"] is None:
            raise ValueError(f"merge_into {merge!r} is not one of the names in the list")
    errors = rr.payload_errors(queue, card, payload)
    if errors:
        raise ValueError("; ".join(errors))
    return payload


def decide(queue, card, definitions, order, provider, cost_fn=None):
    """One card, one order: at most one retry, only when the app would refuse to save."""
    system, user = render(queue, card, definitions, order)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    rec = {"week": queue["report_date"], "card_id": card["card_id"], "kind": card["kind"], "order": order,
           "prompt_sha256": sha_text(system + "\n\n" + user), "attempts": []}
    error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        msgs = messages if error is None else messages + [
            {"role": "user", "content": f"The app could not save that answer: {error}. Return only the JSON object."}]
        t0 = time.perf_counter()
        try:
            out = provider.generate_json(msgs)
        except Exception as e:  # noqa: BLE001 - recorded, never retried here
            rec.update(status="provider_error", error=f"{type(e).__name__}: {e}"[:300])
            return rec
        try:
            payload, error = to_payload(queue, card, json.loads(out.text)), None
        except (ValueError, json.JSONDecodeError) as e:
            payload, error = None, str(e)[:500]
        cost = cost_fn(getattr(provider, "model", out.model), out.usage, datetime.now(timezone.utc)) if cost_fn else None
        rec["attempts"].append({"attempt": attempt, "raw_output": out.text, "valid": payload is not None, "error": error,
                                "model": out.model, "usage": out.usage, "finish_reason": out.finish_reason,
                                "request_id": out.request_id, "latency_ms": round(1000 * (time.perf_counter() - t0), 1),
                                "estimated_cost_usd": cost})
        if payload is not None:
            rec.update(status="decided", payload=payload)
            return rec
    rec.update(status="invalid")
    return rec


# ---------- protocol ----------

def deck_fingerprints(queues=QUEUES):
    out = {}
    for w in WEEKS:
        q = load_week(w, queues)
        cards = required_cards(q)
        out[w] = {"deck_sha256": sha_file(os.path.join(queues, f"report_{w}.json")),
                  "evidence_snapshot_sha256": q.get("evidence_snapshot_sha256"),
                  "signal_cards": sum(c["kind"] == "signal" for c in cards),
                  "duplicate_cards": sum(c["kind"] == "duplicate" for c in cards)}
    return out


def protocol_body():
    import exp005 as v1
    decks = deck_fingerprints()
    return {
        "experiment": "EXP-007 AI labeler alignment on weekly report decisions", "version": "exp007-protocol-v1",
        "decided_by": "the owner, 2026-11-24", "preregistration": "PREREGISTRATION.md",
        "preregistration_sha256": sha_file(os.path.join(EXP, "PREREGISTRATION.md")),
        "prompt_spec": "protocol/prompt_v1.md", "prompt_spec_sha256": sha_file(os.path.join(EXP, "protocol", "prompt_v1.md")),
        "definitions": {"path_local_only": "editorial/report_definitions.md", "sha256": rd.sha256(),
                        "panel_text_sha256": sha_text(definitions_text()),
                        "note": "the file stays on the editor's PC; only its fingerprint is published"},
        "labeler": {"arm": "zero-shot", **v1.PROVIDER_SETTINGS},
        "orders": list(ORDERS), "max_attempts_per_card_and_order": MAX_ATTEMPTS,
        "retry": "one retry only when the app's own save rules (report_review.payload_errors) or JSON parsing reject "
                 "the answer, with the reasons shown",
        "weeks": decks, "cards": sum(d["signal_cards"] + d["duplicate_cards"] for d in decks.values()),
        "pre_plan_cards": sorted(f"{w}|{c}" for w, c in PRE_PLAN_CARDS),
        "looked_up_marker": LOOKED_UP, "cost_gate_usd": GATE_USD, "code_sha256": code_sha(), "frozen_at": _now()}


def check_frozen():
    with open(PROTOCOL, encoding="utf-8") as f:
        p = json.load(f)
    import exp005 as v1
    checks = {"definitions": p["definitions"]["sha256"] == rd.sha256(),
              "panel": p["definitions"]["panel_text_sha256"] == sha_text(definitions_text()),
              "decks": {w: d["deck_sha256"] for w, d in p["weeks"].items()}
                       == {w: d["deck_sha256"] for w, d in deck_fingerprints().items()},
              "code": p["code_sha256"] == code_sha(),
              "provider": {k: p["labeler"][k] for k in v1.PROVIDER_SETTINGS} == v1.PROVIDER_SETTINGS,
              "prereg": p["preregistration_sha256"] == sha_file(os.path.join(EXP, "PREREGISTRATION.md")),
              "prompt_spec": p["prompt_spec_sha256"] == sha_file(os.path.join(EXP, "protocol", "prompt_v1.md"))}
    if not all(checks.values()):
        raise RuntimeError(f"a frozen input changed: {checks}")
    return p


def max_cost(definitions):
    """Upper bound in USD: every character a token, both attempts at the full output limit, peak prices."""
    import exp005 as v1
    from llm_deepseek import PRICING
    price = PRICING[v1.PROVIDER_SETTINGS["model"]]
    total, calls = 0.0, 0
    for w in WEEKS:
        q = load_week(w)
        for c in required_cards(q):
            for order in ORDERS:
                system, user = render(q, c, definitions, order)
                chars = len(system) + len(user) + 600
                total += MAX_ATTEMPTS * (chars * price["input_cache_miss"][1]
                                         + v1.PROVIDER_SETTINGS["max_tokens"] * price["output"][1]) / 1_000_000
                calls += 1
    return {"max_total_usd": round(total, 4), "first_calls": calls, "gate_usd": GATE_USD,
            "assumptions": "1 token per character, 2 attempts, full max_tokens output, peak prices"}


# ---------- run ----------

def run(provider=None, out_path=OUTPUTS, manifest_path=SEALED_MANIFEST):
    if os.path.exists(out_path) or os.path.exists(manifest_path):
        raise RuntimeError("EXP-007 has already run. It runs once.")
    live = provider is None
    if live:
        import rag_select as rs
        ok, info = rs.rule_is_committed_and_pushed(PROTOCOL)
        if not ok:
            raise RuntimeError(f"protocol: {info}")
        check_frozen()
    definitions = definitions_text()
    cost = max_cost(definitions)
    if live and cost["max_total_usd"] > GATE_USD:
        raise RuntimeError(f"estimated maximum cost {cost['max_total_usd']} exceeds the gate")
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
        provider = llm_deepseek.DeepSeekProvider(model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
                                                 max_tokens=p["max_tokens"], timeout=p["timeout_s"],
                                                 max_retries=p["transport_retries"], thinking=p["thinking"],
                                                 allow_live=True)
        cost_fn = llm_deepseek.estimate_cost
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    started, records = _now(), []
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        for w in WEEKS:
            q = load_week(w)
            for c in required_cards(q):
                for order in ORDERS:
                    r = decide(q, c, definitions, order, provider, cost_fn)
                    if r.get("status") == "provider_error" and "not set" in r.get("error", ""):
                        raise RuntimeError("the API key is not loaded; nothing useful was sent")
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f.flush()
                    records.append(r)
    body = dict(seal_counts(records), started_at=started, finished_at=_now(), outputs_sha256=sha_file(out_path),
                provider=provider.config() if hasattr(provider, "config") else "scripted", max_cost_estimate=cost,
                note="counts only; the decisions stay sealed in data/store/blind/exp007/ until compare")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def seal_counts(records):
    """Counts that reveal nothing about what the AI decided."""
    attempts = [a for r in records for a in r["attempts"]]
    tok = lambda k: sum((a.get("usage") or {}).get(k, 0) or 0 for a in attempts)
    first = [r["attempts"][0] for r in records if r["attempts"]]
    return {"records": len(records), "calls": len(attempts),
            "first_attempt_valid": sum(a["valid"] for a in first), "retries": sum(len(r["attempts"]) > 1 for r in records),
            "status_counts": dict(collections.Counter(r["status"] for r in records)),
            "tokens": {"prompt": tok("prompt_tokens"), "completion": tok("completion_tokens")},
            "estimated_cost_usd": round(sum(a.get("estimated_cost_usd") or 0 for a in attempts), 6)}


def status():
    if not os.path.exists(OUTPUTS):
        return {"sealed": False}
    with open(OUTPUTS, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    return {"sealed": os.path.exists(SEALED_MANIFEST), **seal_counts(records)}


# ---------- after the editor's backlog ----------

def editor_log(week):
    return os.path.join(os.path.dirname(ROOT), "reports-editing", "app", f"{week}-decisions.jsonl")


def seal_editor():
    """Fingerprint the editor's decision logs before anything is unsealed."""
    if os.path.exists(EDITOR_MANIFEST):
        raise RuntimeError("the editor's logs are already fingerprinted")
    if not os.path.exists(SEALED_MANIFEST):
        raise RuntimeError("the AI run is not sealed yet")
    body = {"fingerprinted_at": _now(), "weeks": {}}
    for w in WEEKS:
        q = load_week(w)
        rows = rr.load_rows(editor_log(w))
        latest = rr.latest(q)
        need = [c["card_id"] for c in required_cards(q)]
        body["weeks"][w] = {"log_sha256": sha_file(editor_log(w)) if rows else None, "rows": len(rows),
                            "decided": sum(1 for c in need if c in latest), "required": len(need)}
    with open(EDITOR_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def kappa(pairs):
    """Cohen's kappa for a list of (editor, ai) labels."""
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return round((po - pe) / (1 - pe), 4) if pe < 1 else None


def agreement(pairs):
    n = len(pairs)
    if not n:
        return {"n": 0}
    top, top_n = collections.Counter(a for a, _ in pairs).most_common(1)[0]
    return {"n": n, "agreement": round(sum(a == b for a, b in pairs) / n, 4), "kappa": kappa(pairs),
            "majority_baseline": round(top_n / n, 4), "majority_label": top}


def compare(ai_records, editor):
    """ai_records: sealed records. editor: {week: {card_id: payload}}. The pre-registered metrics."""
    ai = {(r["week"], r["card_id"], r["order"]): r for r in ai_records}
    main = collections.defaultdict(list)
    out = {"excluded": collections.Counter(), "per_week": {}}
    sig, inc, vol, merge, dup, swap, separate = [], [], [], [], [], [], []
    for w in WEEKS:
        q = load_week(w)
        week_sig, kept_e, kept_a = [], set(), set()
        for c in required_cards(q):
            e = editor.get(w, {}).get(c["card_id"])
            a, s = ai.get((w, c["card_id"], "original")), ai.get((w, c["card_id"], "swapped"))
            if a and s and a["status"] == s["status"] == "decided":
                key = "decision" if c["kind"] == "signal" else "collapse"
                swap.append(a["payload"].get(key) == s["payload"].get(key))
            if e is None:
                out["excluded"]["editor_undecided"] += 1
                continue
            if not a or a["status"] != "decided":
                out["excluded"]["ai_invalid_or_missing"] += 1
                continue
            p = a["payload"]
            if LOOKED_UP in (e.get("thoughts") or "").lower() or (w, c["card_id"]) in PRE_PLAN_CARDS:
                separate.append({"week": w, "card_id": c["card_id"], "editor": e.get("decision", e.get("collapse")),
                                 "ai": p.get("decision", p.get("collapse")),
                                 "why": "looked up" if LOOKED_UP in (e.get("thoughts") or "").lower() else "decided before the plan"})
                continue
            if c["kind"] == "duplicate":
                dup.append((e["collapse"], p["collapse"]))
                continue
            pair = (e["decision"], p["decision"])
            sig.append(pair)
            week_sig.append(pair)
            inc.append((e["decision"] == "keep", p["decision"] == "keep"))
            if pair == ("keep", "keep"):
                vol.append((e["volatility"], p["volatility"]))
            if pair == ("merge", "merge"):
                merge.append((e["merge_into"], p["merge_into"]))
            if e["decision"] == "keep":
                kept_e.add(c["signal_id"])
            if p["decision"] == "keep":
                kept_a.add(c["signal_id"])
        union = kept_e | kept_a
        out["per_week"][w] = {**agreement(week_sig), "kept_editor": len(kept_e), "kept_ai": len(kept_a),
                              "kept_jaccard": round(len(kept_e & kept_a) / len(union), 4) if union else None}
    out.update({"decision": agreement(sig), "keep_vs_not": agreement(inc), "volatility_on_both_kept": agreement(vol),
                "merge_target_on_both_merged": agreement(merge), "duplicates": agreement(dup),
                "position_bias": {"cards_decided_in_both_orders": len(swap),
                                  "changed_under_swap": sum(not x for x in swap),
                                  "share_changed": round(sum(not x for x in swap) / len(swap), 4) if swap else None},
                "reported_separately": separate, "excluded": dict(out["excluded"])})
    out["confusion"] = {f"{a}->{b}": n for (a, b), n in sorted(collections.Counter(sig).items())}
    return out


def run_compare():
    import rag_select as rs
    if os.path.exists(RESULT):
        raise RuntimeError("the comparison already exists")
    for path in (SEALED_MANIFEST, EDITOR_MANIFEST):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    with open(SEALED_MANIFEST, encoding="utf-8") as f:
        if sha_file(OUTPUTS) != json.load(f)["outputs_sha256"]:
            raise RuntimeError("the sealed AI outputs changed")
    with open(EDITOR_MANIFEST, encoding="utf-8") as f:
        em = json.load(f)
    editor = {}
    for w in WEEKS:
        if (sha_file(editor_log(w)) if rr.load_rows(editor_log(w)) else None) != em["weeks"][w]["log_sha256"]:
            raise RuntimeError(f"{w}: the editor's log changed after it was fingerprinted")
        editor[w] = rr.latest(load_week(w))
    with open(OUTPUTS, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    body = dict(compare(records, editor), compared_at=_now(), code_sha256=code_sha())
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    write_detail(records, editor)
    return body


def write_detail(records, editor):
    """Local only: every disagreement with both sets of thoughts, and both kept-signal tables."""
    ai = {(r["week"], r["card_id"]): r for r in records if r["order"] == "original" and r["status"] == "decided"}
    lines = ["# EXP-007 comparison detail (local only)", ""]
    for w in WEEKS:
        q = load_week(w)
        lines += [f"## {w}", ""]
        for who, get in (("Editor", lambda c: editor[w].get(c["card_id"])),
                         ("AI", lambda c: (ai.get((w, c["card_id"])) or {}).get("payload"))):
            kept = [(c, get(c)) for c in q["cards"] if c["kind"] == "signal" and (get(c) or {}).get("decision") == "keep"]
            lines += [f"**{who} kept {len(kept)}:**", ""] + [
                f"- {c['name']}: {c['items']} items from {c['outlets']} outlets, volatility {p['volatility']}, "
                f"confidence {p.get('confidence') or 'baseline'}" for c, p in kept] + [""]
        for c in required_cards(q):
            e, a = editor[w].get(c["card_id"]), (ai.get((w, c["card_id"])) or {}).get("payload")
            if not e or not a:
                continue
            key = "decision" if c["kind"] == "signal" else "collapse"
            if e.get(key) != a.get(key):
                lines += [f"### {c.get('name', c['card_id'])}: editor {e.get(key)}, AI {a.get(key)}", "",
                          f"Editor: {e.get('thoughts') or '(no thoughts)'}", "", f"AI: {a.get('thoughts') or '(none)'}", ""]
    os.makedirs(os.path.dirname(DETAIL), exist_ok=True)
    with open(DETAIL, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["render-example", "freeze-protocol", "estimate-cost", "run", "status",
                                    "seal-editor", "compare"])
    ap.add_argument("--week", default=WEEKS[0])
    ap.add_argument("--card", default=None)
    ap.add_argument("--order", default="original", choices=ORDERS)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "render-example":
            q = load_week(args.week)
            card = next(c for c in required_cards(q) if args.card in (None, c["card_id"]))
            system, user = render(q, card, definitions_text(), args.order)
            print(f"--- system ---\n{system}\n\n--- user ---\n{user}")
            return 0
        if args.cmd == "freeze-protocol":
            os.makedirs(os.path.dirname(PROTOCOL), exist_ok=True)
            with open(PROTOCOL, "x", encoding="utf-8", newline="\n") as f:
                json.dump(protocol_body(), f, indent=1, ensure_ascii=False)
            body = {"protocol_sha256": sha_file(PROTOCOL)}
        elif args.cmd == "estimate-cost":
            body = max_cost(definitions_text())
        elif args.cmd == "run":
            body = run()
        elif args.cmd == "status":
            body = status()
        elif args.cmd == "seal-editor":
            body = seal_editor()
        else:
            body = run_compare()
    except (RuntimeError, FileExistsError) as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
