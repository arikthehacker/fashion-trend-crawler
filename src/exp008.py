"""EXP-008: does a taste profile of the editor, written by an AI from her other weeks, bring an AI
labeler closer to her decisions? (pre-registration: experiments/exp-008-taste-profile/PREREGISTRATION.md)

Step 1, the profiles. For each of the seven weeks, a fresh Claude subagent that has never seen EXP-007's
results reads only the editor's decisions, thoughts and cards from the OTHER six weeks and writes a short
profile of general rules. The profiles are saved unedited, checked by software for leaked names and
headlines, and sealed. Nobody reads them until the results are in.

Step 2, the rerun. EXP-007's thinking-off reader runs again on the same 226 cards with the same settings,
both option orders, and one change: the held-out week's profile is added to the prompt. The answers are
sealed, then compared with the editor and with EXP-007's thinking-off answers.

usage:
  python src/exp008.py build-inputs          # local profile inputs, from the fingerprinted editor logs
  python src/exp008.py freeze-protocol       # once, before any call; then commit
  python src/exp008.py instructions --week W # the filled subagent instructions for held-out week W
  python src/exp008.py check-profile --week W --transcript PATH   # software checks, prints no profile text
  python src/exp008.py seal-profiles         # after all 7 pass; then commit and push
  python src/exp008.py estimate-cost
  python src/exp008.py render-example --week W [--card ID]   # needs the sealed profile; prints it
  python src/exp008.py run                   # once; needs ARI3_LIVE_LLM=approved
  python src/exp008.py status                # counts only
  python src/exp008.py compare               # after the run is sealed and pushed
"""

import argparse
import collections
import json
import os
import random
import re
import sys
from datetime import datetime, timezone

import exp007 as e7
import report_review as rr
from item_store import ROOT

EXP = os.path.join(ROOT, "experiments", "exp-008-taste-profile")
PROTOCOL = os.path.join(EXP, "protocol", "protocol_v1.json")
PREREG = os.path.join(EXP, "PREREGISTRATION.md")
INSTRUCTIONS = os.path.join(EXP, "protocol", "profile_instructions_v1.md")
PROMPT_SPEC = os.path.join(EXP, "protocol", "prompt_v2.md")
PROFILE_MANIFEST = os.path.join(EXP, "runs", "sealed_profiles.json")
# (written record, frozen fingerprint) per amendment, in order; the code must match the latest frozen one
AMENDMENTS = [(os.path.join(EXP, "AMENDMENT_2026-11-25_handback.md"), os.path.join(EXP, "protocol", "amendment_1.json")),
              (os.path.join(EXP, "AMENDMENT_2026-11-25_self_edits.md"), os.path.join(EXP, "protocol", "amendment_2.json"))]
AUDIT_RULES = "amendment 2"
MAX_REPLY_CHARS = 300
MANIFEST = os.path.join(EXP, "runs", "sealed_manifest.json")
RESULT = os.path.join(EXP, "runs", "comparison.json")
BLIND = os.path.join(ROOT, "data", "store", "blind", "exp008")
INPUTS = os.path.join(BLIND, "profile_inputs")
PROFILES = os.path.join(BLIND, "profiles")
CHECKS = os.path.join(BLIND, "profile_checks")
OUT = os.path.join(BLIND, "outputs_thinking_off.jsonl")
DETAIL = os.path.join(BLIND, "comparison_detail.md")
WEEKS = e7.WEEKS
ARM = "thinking_off"
ORDERS = e7.ARMS[ARM]["orders"]
PROFILE_WRITER = "claude-opus-5-5 (Claude Code general-purpose subagent, fresh context)"
MAX_PROFILE_WORDS = 800
MAX_PROFILE_ATTEMPTS = 2  # per week: one profile, one fresh regeneration only if a software check fails
COST_CAP_USD = 1.00  # the run stops once its running estimated cost reaches this
BOOTSTRAP = {"resamples": 10000, "seed": 8008, "unit": "signal card", "interval": "percentile 95%"}
CODE_FILES = e7.CODE_FILES + ("exp008.py",)
PROFILE_HEADING = ("HOW THE EDITOR DECIDES (a profile written by an AI from the editor's decisions and "
                   "thoughts in other weeks, not this one)")
OPENING_FROM = "followed by the editor's definitions."
OPENING_TO = "followed by the editor's definitions and a profile of how the editor decides."
# outlet name parts that are also ordinary English words; only their full domains are checked
COMMON_WORDS = {"complex", "stylist", "nylon", "wallpaper", "numero"}
WORD = re.compile(r"[a-z0-9']+")
# amendment 1: the harness's own reply channel, allowed only when the reply is just the word count
HANDBACK_TOOL = "SubagentHandback"
HANDBACK_REPLY = re.compile(r"\s*\d+(\s+words?)?\s*\.?\s*", re.I)
GENERIC_LABELS = {"www", "en", "m", "com", "co", "uk", "it", "de", "fr", "es", "me", "net", "org", "mx", "au",
                  "id", "in", "jp", "kr", "br", "ca", "ae", "cn"}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(path):
    return os.path.normcase(os.path.abspath(path)).replace("\\", "/")


# ---------- the editor's decisions (already fingerprinted by EXP-007) ----------

def editor_decisions():
    """{week: {card_id: payload}}, refusing any log that changed since EXP-007 fingerprinted it."""
    with open(e7.EDITOR_MANIFEST, encoding="utf-8") as f:
        em = json.load(f)
    out = {}
    for w in WEEKS:
        rows = rr.load_rows(e7.editor_log(w))
        if (e7.sha_file(e7.editor_log(w)) if rows else None) != em["weeks"][w]["log_sha256"]:
            raise RuntimeError(f"{w}: the editor's log changed after EXP-007 fingerprinted it")
        out[w] = rr.latest(e7.load_week(w))
    return out


def _decision_lines(queue, card, p):
    if card["kind"] == "duplicate":
        choice = e7.DUP_OPTIONS[0] if p.get("collapse") else e7.DUP_OPTIONS[1]
        return [f"Editor's decision: {choice}", f"Editor's thoughts: {p.get('thoughts') or '(none)'}"]
    names = {sid: n for n, sid in rr.merge_choices(queue, card)}
    lines = [f"Editor's decision: {p['decision']}"]
    if p.get("merge_into"):
        lines.append(f"Merged into: {names.get(p['merge_into'], p['merge_into'])}")
    if p.get("volatility"):
        lines.append(f"Volatility: {p['volatility']}")
    lines.append(f"Confidence: {p.get('confidence') or 'baseline (' + card['baseline_confidence'] + ')'}")
    if p.get("type"):
        lines.append(f"Type changed to: {p['type']}")
    if p.get("origin"):
        lines.append(f"Origin: {p['origin']}")
    if p.get("name"):
        lines.append(f"Name as published changed to: {p['name']}")
    if p.get("remove_item_ids"):
        lines.append(f"Items removed: {len(p['remove_item_ids'])}")
    lines.append(f"Editor's thoughts: {p.get('thoughts') or '(none)'}")
    return lines


def week_input(week, editor):
    """One week's cards as the app showed them, each followed by the editor's answer. Deterministic."""
    q = e7.load_week(week)
    parts = [f"# Week ending {week}: {q['title']}", ""]
    for i, c in enumerate(e7.required_cards(q), 1):
        p = editor[week].get(c["card_id"])
        if p is None:
            raise RuntimeError(f"{week} {c['card_id']}: the editor left this card undecided")
        title = c["name"] if c["kind"] == "signal" else "Possible duplicates"
        parts += [f"## Card {i}: {title}", "", rr.card_text(c), ""] + _decision_lines(q, c, p) + [""]
    return "\n".join(parts)


def input_paths(held):
    return {w: os.path.join(INPUTS, held, f"week-{w}.md") for w in WEEKS if w != held}


def build_inputs():
    editor = editor_decisions()
    texts = {w: week_input(w, editor) for w in WEEKS}
    out = {}
    for held in WEEKS:
        out[held] = {}
        for w, path in input_paths(held).items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    if f.read() != texts[w]:
                        raise RuntimeError(f"{path} exists with different content")
            else:
                with open(path, "x", encoding="utf-8", newline="\n") as f:
                    f.write(texts[w])
            out[held][w] = e7.sha_file(path)
    return out


# ---------- what a profile may not contain ----------

def vocabulary():
    """Signal names, outlet names and headline 5-grams from all seven decks."""
    names, outlets, grams = set(), set(), set()
    for w in WEEKS:
        for c in e7.required_cards(e7.load_week(w)):
            items = c.get("evidence", []) if c["kind"] == "signal" else c.get("items", [])
            if c["kind"] == "signal":
                names.add(c["name"].lower())
            for it in items:
                dom = (it.get("outlet") or "").lower()
                if dom:
                    outlets.add(dom)
                    outlets.update(x for x in dom.split(".")[:-1]
                                   if x not in GENERIC_LABELS and x not in COMMON_WORDS and len(x) > 1)
                toks = WORD.findall((it.get("title") or "").lower())
                grams.update(tuple(toks[i:i + 5]) for i in range(len(toks) - 4))
    return sorted(names), sorted(outlets), grams


def _name_pattern(name):
    parts = [re.escape(p) for p in re.split(r"[\s-]+", name.lower())]
    return re.compile(r"(?<![a-z0-9])" + r"[\s-]?".join(parts) + r"(s|es)?(?![a-z0-9])")


def leak_problems(text, vocab=None):
    """Software checks on a profile. Returns problems naming only the matched words, never the text."""
    names, outlets, grams = vocab or vocabulary()
    low = text.lower()
    problems = []
    words = len(WORD.findall(low))
    if words == 0:
        problems.append("empty")
    if words > MAX_PROFILE_WORDS:
        problems.append(f"too long: {words} words")
    problems += [f"signal name: {n}" for n in names if _name_pattern(n).search(low)]
    problems += [f"outlet: {o}" for o in outlets
                 if re.search(r"(?<![a-z0-9])" + re.escape(o) + r"(?![a-z0-9])", low)]
    toks = WORD.findall(low)
    hits = {" ".join(toks[i:i + 5]) for i in range(len(toks) - 4) if tuple(toks[i:i + 5]) in grams}
    problems += [f"headline words: {h}" for h in sorted(hits)]
    return problems


# ---------- the subagent ----------

def banned_list():
    names, outlets, _ = vocabulary()
    return names, sorted(o for o in outlets if "." in o)


def instructions(held):
    with open(INSTRUCTIONS, encoding="utf-8") as f:
        tpl = f.read()
    names, domains = banned_list()
    files = "\n".join(f"- {_norm(p)}" for p in input_paths(held).values())
    return (tpl.replace("{files}", files).replace("{output}", _norm(os.path.join(PROFILES, f"{held}.md")))
            .replace("{names}", ", ".join(names)).replace("{outlets}", ", ".join(domains)))


def audit_transcript(path, held):
    """The subagent may read only its six input files and write only its profile. Returns problems."""
    allowed_read = {_norm(p) for p in input_paths(held).values()}
    allowed_write = _norm(os.path.join(PROFILES, f"{held}.md"))
    calls, problems = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                msg = json.loads(line).get("message") or {}
            except json.JSONDecodeError:
                continue
            content = msg.get("content") if isinstance(msg, dict) else None
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    name, inp = b.get("name"), b.get("input") or {}
                    target = _norm(inp["file_path"]) if inp.get("file_path") else None
                    calls.append({"tool": name, "path": target})
                    if name == "Read" and target in allowed_read:
                        continue
                    if name in ("Write", "Edit", "Read") and target == allowed_write:
                        continue  # amendment 2: the subagent may reread and revise its own profile
                    if name == HANDBACK_TOOL and _reply_ok(str(inp.get("message", ""))):
                        calls[-1]["reply"] = str(inp.get("message"))
                        continue
                    problems.append(f"tool call not allowed: {name} {target or ''}".strip())
    if not any(c["tool"] == "Write" for c in calls):
        problems.append("the profile was not written with the Write tool")
    read = {c["path"] for c in calls if c["tool"] == "Read"} - {allowed_write}
    if read != allowed_read:
        problems.append(f"input files not read: {len(allowed_read - read)}")
    return calls, problems


def _reply_ok(message):
    """Amendment 1 allowed a bare word count. Amendment 2: any short reply that leaks nothing."""
    if HANDBACK_REPLY.fullmatch(message):
        return True
    return len(message) <= MAX_REPLY_CHARS and not leak_problems(message)


def check_profile(held, transcript):
    path = os.path.join(PROFILES, f"{held}.md")
    if not os.path.exists(path):
        raise RuntimeError(f"no profile for {held}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    calls, audit = audit_transcript(transcript, held)
    leaks = leak_problems(text)
    os.makedirs(CHECKS, exist_ok=True)
    shas = list(dict.fromkeys(r["profile_sha256"] for r in _load_jsonl(os.path.join(CHECKS, f"{held}.jsonl"))))
    sha = e7.sha_file(path)
    attempt = shas.index(sha) + 1 if sha in shas else len(shas) + 1  # a recheck of the same profile is not a new attempt
    rec = {"week": held, "attempt": attempt, "audit_rules": AUDIT_RULES, "checked_at": _now(), "profile_sha256": sha,
           "words": len(WORD.findall(text.lower())), "transcript": os.path.basename(transcript),
           "transcript_sha256": e7.sha_file(transcript), "tool_calls": calls, "audit_problems": audit,
           "leak_problems": leaks, "pass": not audit and not leaks}
    with open(os.path.join(CHECKS, f"{held}.jsonl"), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {k: rec[k] for k in ("week", "attempt", "words", "audit_problems", "leak_problems", "pass")}


def _load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def seal_profiles():
    if os.path.exists(PROFILE_MANIFEST):
        raise RuntimeError("the profiles are already sealed")
    check_frozen()
    body = {"sealed_at": _now(), "writer": PROFILE_WRITER, "weeks": {}}
    for w in WEEKS:
        checks = _load_jsonl(os.path.join(CHECKS, f"{w}.jsonl"))
        if not checks or not checks[-1]["pass"]:
            raise RuntimeError(f"{w}: no passing check")
        path = os.path.join(PROFILES, f"{w}.md")
        if e7.sha_file(path) != checks[-1]["profile_sha256"]:
            raise RuntimeError(f"{w}: the profile changed after its check")
        final = checks[-1]["profile_sha256"]
        last = {c["profile_sha256"]: c for c in checks}  # the latest check of each attempt
        body["weeks"][w] = {"profile_sha256": final, "words": checks[-1]["words"], "attempts": len(last),
                            "checks_run": len(checks), "audit_rules": checks[-1].get("audit_rules"),
                            "transcript_sha256": checks[-1]["transcript_sha256"],
                            "failed_attempts": [{"attempt": c["attempt"], "audit_problems": c["audit_problems"],
                                                 "leak_problems": c["leak_problems"]}
                                                for sha, c in last.items() if sha != final]}
    os.makedirs(os.path.dirname(PROFILE_MANIFEST), exist_ok=True)
    with open(PROFILE_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def load_profiles():
    with open(PROFILE_MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    out = {}
    for w in WEEKS:
        path = os.path.join(PROFILES, f"{w}.md")
        if e7.sha_file(path) != m["weeks"][w]["profile_sha256"]:
            raise RuntimeError(f"{w}: the sealed profile changed")
        with open(path, encoding="utf-8") as f:
            out[w] = f.read().strip()
    return out


# ---------- prompt ----------

_E7_RENDER = e7.render  # kept before _decide swaps e7.render, so EXP-007's prompt is always the base


def render(queue, card, definitions, profile, order="original"):
    """EXP-007's prompt with one change: the profile after the definitions (protocol/prompt_v2.md)."""
    system, user = _E7_RENDER(queue, card, definitions, order)
    anchor = f"DEFINITIONS (your words)\n\n{definitions}"
    if system.count(OPENING_FROM) != 1 or user.count(anchor) != 1:
        raise RuntimeError("the EXP-007 prompt no longer has the expected anchors")
    return (system.replace(OPENING_FROM, OPENING_TO),
            user.replace(anchor, f"{anchor}\n\n{PROFILE_HEADING}\n\n{profile}"))


# ---------- protocol ----------

def protocol_body():
    names, outlets, grams = vocabulary()
    return {
        "experiment": "EXP-008 taste profile, leave-one-week-out", "version": "exp008-protocol-v1",
        "decided_by": "the owner, 2026-11-25",
        "preregistration_sha256": e7.sha_file(PREREG),
        "profile_instructions_sha256": e7.sha_file(INSTRUCTIONS),
        "prompt_spec_sha256": e7.sha_file(PROMPT_SPEC),
        "profile_writer": PROFILE_WRITER, "max_profile_words": MAX_PROFILE_WORDS,
        "max_profile_attempts_per_week": MAX_PROFILE_ATTEMPTS,
        "profile_inputs_sha256": {h: {w: e7.sha_file(p) for w, p in input_paths(h).items()} for h in WEEKS},
        "leak_vocabulary": {"signal_names": len(names), "outlet_names": len(outlets), "headline_5grams": len(grams),
                            "sha256": e7.sha_text(json.dumps([names, outlets, sorted(map(list, grams))]))},
        "definitions": {"sha256": e7.rd.sha256(), "panel_text_sha256": e7.sha_text(e7.definitions_text())},
        "weeks": e7.deck_fingerprints(),
        "editor_logs_manifest_sha256": e7.sha_file(e7.EDITOR_MANIFEST),
        "exp007_thinking_off_outputs_sha256": _exp007_manifest()["outputs_sha256"],
        "reader": {"orders": list(ORDERS), "settings": e7.arm_settings(ARM)},
        "max_attempts_per_card_and_order": e7.MAX_ATTEMPTS, "running_cost_cap_usd": COST_CAP_USD,
        "bootstrap": BOOTSTRAP, "code_sha256": code_sha(), "frozen_at": _now()}


def code_sha():
    return {f: e7.sha_file(os.path.join(e7.SRC, f)) for f in CODE_FILES}


def _exp007_manifest():
    with open(e7.ARMS[ARM]["manifest"], encoding="utf-8") as f:
        return json.load(f)


def check_frozen():
    with open(PROTOCOL, encoding="utf-8") as f:
        p = json.load(f)
    now = protocol_body()
    keys = ("preregistration_sha256", "profile_instructions_sha256", "prompt_spec_sha256", "profile_inputs_sha256",
            "leak_vocabulary", "definitions", "weeks", "editor_logs_manifest_sha256",
            "exp007_thinking_off_outputs_sha256", "reader", "code_sha256")
    changed = [k for k in keys if p[k] != now[k]]
    frozen = [(md, js) for md, js in AMENDMENTS if os.path.exists(js)]
    if changed == ["code_sha256"] and frozen:
        for md, js in frozen:
            with open(js, encoding="utf-8") as f:
                a = json.load(f)
            if a["amends_protocol_sha256"] != e7.sha_file(PROTOCOL) or a["amendment_sha256"] != e7.sha_file(md):
                raise RuntimeError(f"{os.path.basename(js)} no longer matches its files")
        if a["code_sha256"] == now["code_sha256"]:
            return p
        raise RuntimeError("the code matches neither the protocol nor the latest amendment")
    if changed:
        raise RuntimeError(f"a frozen input changed: {changed}")
    return p


def max_cost(definitions, profiles):
    """Upper bound as in EXP-007: every character a token, both attempts at full output, peak prices."""
    import exp005 as v1
    from llm_deepseek import PRICING
    price = PRICING[v1.PROVIDER_SETTINGS["model"]]
    total, calls = 0.0, 0
    for w in WEEKS:
        q = e7.load_week(w)
        for c in e7.required_cards(q):
            for order in ORDERS:
                system, user = render(q, c, definitions, profiles[w], order)
                total += e7.MAX_ATTEMPTS * ((len(system) + len(user) + 600) * price["input_cache_miss"][1]
                                            + e7.ARMS[ARM]["max_tokens"] * price["output"][1]) / 1_000_000
                calls += 1
    return {"max_total_usd": round(total, 4), "first_calls": calls, "running_cap_usd": COST_CAP_USD,
            "assumptions": "1 token per character, 2 attempts, full max_tokens output, peak prices"}


# ---------- run ----------

def run(provider=None, out_path=OUT, manifest_path=MANIFEST):
    if os.path.exists(out_path) or os.path.exists(manifest_path):
        raise RuntimeError("EXP-008 has already run. It runs once.")
    live = provider is None
    if live:
        import rag_select as rs
        for path in (PROTOCOL, *[js for _, js in AMENDMENTS], PROFILE_MANIFEST):
            ok, info = rs.rule_is_committed_and_pushed(path)
            if not ok:
                raise RuntimeError(f"{os.path.basename(path)}: {info}")
        check_frozen()
    definitions, profiles = e7.definitions_text(), load_profiles()
    cost = max_cost(definitions, profiles)
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
            max_tokens=e7.ARMS[ARM]["max_tokens"], timeout=p["timeout_s"], max_retries=p["transport_retries"],
            allow_live=True)
        cost_fn = llm_deepseek.estimate_cost
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    started, records, spent, stopped = _now(), [], 0.0, False
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        for w in WEEKS:
            q = e7.load_week(w)
            for c in e7.required_cards(q):
                for order in ORDERS:
                    if spent >= COST_CAP_USD:
                        stopped = True
                        break
                    r = _decide(q, c, definitions, profiles[w], order, provider, cost_fn)
                    r["arm"] = "exp008_" + ARM
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
                note="counts only; the decisions stay sealed in data/store/blind/exp008/ until compare")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def _decide(queue, card, definitions, profile, order, provider, cost_fn):
    """EXP-007's decide() with this experiment's prompt (same retry rule, same record)."""
    e7.render = lambda q, c, d, o="original": render(q, c, d, profile, o)
    try:
        return e7.decide(queue, card, definitions, order, provider, cost_fn)
    finally:
        e7.render = _E7_RENDER


def status():
    out = {"profiles_sealed": os.path.exists(PROFILE_MANIFEST),
           "profile_checks": {w: [c["pass"] for c in _load_jsonl(os.path.join(CHECKS, f"{w}.jsonl"))] for w in WEEKS}}
    if os.path.exists(OUT):
        out.update(run_sealed=os.path.exists(MANIFEST), **e7.seal_counts(e7.load_records(OUT)))
    return out


# ---------- compare ----------

def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value on the discordant counts b and c."""
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return round(min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n), 6)


def paired(rec7, rec8, editor, bootstrap=BOOTSTRAP):
    """Card-level pairs on the signal cards both runs decided in app order, EXP-007's exclusions."""
    a7 = {(r["week"], r["card_id"]): r for r in rec7 if r["order"] == "original" and r["status"] == "decided"}
    a8 = {(r["week"], r["card_id"]): r for r in rec8 if r["order"] == "original" and r["status"] == "decided"}
    rows = []
    for w in WEEKS:
        for c in e7.required_cards(e7.load_week(w)):
            k, e = (w, c["card_id"]), editor.get(w, {}).get(c["card_id"])
            if c["kind"] != "signal" or e is None or k not in a7 or k not in a8:
                continue
            if (w, c["card_id"]) in e7.PRE_PLAN_CARDS or e7.LOOKED_UP in (e.get("thoughts") or "").lower():
                continue
            rows.append((e["decision"], a7[k]["payload"]["decision"], a8[k]["payload"]["decision"]))

    def stats(rs):
        k7 = e7.kappa([(r[0], r[1]) for r in rs])
        k8 = e7.kappa([(r[0], r[2]) for r in rs])
        i7 = e7.kappa([(r[0] == "keep", r[1] == "keep") for r in rs])
        i8 = e7.kappa([(r[0] == "keep", r[2] == "keep") for r in rs])
        return k7, k8, i7, i8

    k7, k8, i7, i8 = stats(rows)
    rng = random.Random(bootstrap["seed"])
    d_dec, d_inc = [], []
    for _ in range(bootstrap["resamples"]):
        s = [rows[rng.randrange(len(rows))] for _ in rows]
        b7, b8, j7, j8 = stats(s)
        if None not in (b7, b8):
            d_dec.append(b8 - b7)
        if None not in (j7, j8):
            d_inc.append(j8 - j7)

    def ci(xs):
        xs = sorted(xs)
        return [round(xs[int(0.025 * len(xs))], 4), round(xs[min(len(xs) - 1, int(0.975 * len(xs)))], 4)] if xs else None

    def verdict(interval):
        if interval is None:
            return "not computable"
        return "supported" if interval[0] > 0 else ("reversed" if interval[1] < 0 else "not supported")

    b = sum(r[1] == r[0] and r[2] != r[0] for r in rows)
    c = sum(r[1] != r[0] and r[2] == r[0] for r in rows)
    dci, ici = ci(d_dec), ci(d_inc)
    return {"n": len(rows), "kappa_exp007": k7, "kappa_exp008": k8,
            "delta_kappa": round(k8 - k7, 4) if None not in (k7, k8) else None, "delta_kappa_ci": dci,
            "H1_decision_kappa": verdict(dci),
            "keep_kappa_exp007": i7, "keep_kappa_exp008": i8,
            "delta_keep_kappa": round(i8 - i7, 4) if None not in (i7, i8) else None, "delta_keep_kappa_ci": ici,
            "H2_keep_kappa": verdict(ici),
            "mcnemar": {"exp007_right_exp008_wrong": b, "exp007_wrong_exp008_right": c, "p_exact": mcnemar_exact(b, c)},
            "ai_drops": {"exp007": sum(r[1] == "drop" for r in rows), "exp008": sum(r[2] == "drop" for r in rows),
                         "editor": sum(r[0] == "drop" for r in rows)},
            "bootstrap": bootstrap}


def _rename(d):
    s = json.dumps(d).replace("thinking_on", "exp008").replace("thinking_off", "exp007")
    return json.loads(s.replace("changed_by_thinking", "changed_by_profile"))


def run_compare():
    import rag_select as rs
    if os.path.exists(RESULT):
        raise RuntimeError("the comparison already exists")
    for path in (PROTOCOL, *[js for _, js in AMENDMENTS], PROFILE_MANIFEST, MANIFEST):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    with open(MANIFEST, encoding="utf-8") as f:
        if e7.sha_file(OUT) != json.load(f)["outputs_sha256"]:
            raise RuntimeError("the sealed EXP-008 outputs changed")
    out7 = e7.ARMS[ARM]["out"]
    if e7.sha_file(out7) != _exp007_manifest()["outputs_sha256"]:
        raise RuntimeError("the sealed EXP-007 outputs changed")
    rec8, rec7, editor = e7.load_records(OUT), e7.load_records(out7), editor_decisions()
    with open(e7.RESULT, encoding="utf-8") as f:
        exp007_result = json.load(f)["editor_vs_thinking_off"]
    body = {"editor_vs_exp008": e7.compare(rec8, editor),
            "editor_vs_exp007_thinking_off": exp007_result,
            "exp007_vs_exp008": _rename(e7.compare_ai(rec7, rec8)),
            "paired": paired(rec7, rec8, editor), "compared_at": _now(), "code_sha256": code_sha()}
    with open(RESULT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    write_detail(rec7, rec8, editor)
    return body


def write_detail(rec7, rec8, editor):
    """Local only: every signal or duplicate card where the editor, EXP-007 and EXP-008 differ."""
    a7 = {(r["week"], r["card_id"]): r.get("payload") for r in rec7 if r["order"] == "original"}
    a8 = {(r["week"], r["card_id"]): r.get("payload") for r in rec8 if r["order"] == "original"}
    lines = ["# EXP-008 comparison detail (local only)", ""]
    for w in WEEKS:
        lines += [f"## {w}", ""]
        for c in e7.required_cards(e7.load_week(w)):
            key = "decision" if c["kind"] == "signal" else "collapse"
            got = [("Editor", editor[w].get(c["card_id"])), ("EXP-007", a7.get((w, c["card_id"]))),
                   ("EXP-008", a8.get((w, c["card_id"])))]
            if any(p is None for _, p in got) or len({str(p.get(key)) for _, p in got}) == 1:
                continue
            lines += [f"### {c.get('name', c['card_id'])}: " + ", ".join(f"{who} {p.get(key)}" for who, p in got), ""]
            lines += [f"{who}: {p.get('thoughts') or '(no thoughts)'}" for who, p in got] + [""]
    with open(DETAIL, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build-inputs", "freeze-protocol", "freeze-amendment", "instructions", "check-profile",
                                    "seal-profiles", "estimate-cost", "render-example", "run", "status", "compare"])
    ap.add_argument("--week", default=WEEKS[0])
    ap.add_argument("--card", default=None)
    ap.add_argument("--transcript", default=None)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "build-inputs":
            body = build_inputs()
        elif args.cmd == "freeze-protocol":
            os.makedirs(os.path.dirname(PROTOCOL), exist_ok=True)
            with open(PROTOCOL, "x", encoding="utf-8", newline="\n") as f:
                json.dump(protocol_body(), f, indent=1, ensure_ascii=False)
            body = {"protocol_sha256": e7.sha_file(PROTOCOL)}
        elif args.cmd == "freeze-amendment":
            n = next(i for i, (_, js) in enumerate(AMENDMENTS, 1) if not os.path.exists(js))
            md, js = AMENDMENTS[n - 1]
            with open(js, "x", encoding="utf-8", newline="\n") as f:
                json.dump({"amendment": os.path.basename(md), "amendment_sha256": e7.sha_file(md),
                           "amends_protocol_sha256": e7.sha_file(PROTOCOL), "code_sha256": code_sha(),
                           "frozen_at": _now()}, f, indent=1)
            body = {f"amendment_{n}_sha256": e7.sha_file(js)}
        elif args.cmd == "instructions":
            print(instructions(args.week))
            return 0
        elif args.cmd == "check-profile":
            body = check_profile(args.week, args.transcript)
        elif args.cmd == "seal-profiles":
            body = seal_profiles()
        elif args.cmd == "estimate-cost":
            placeholder = {w: "x" * (MAX_PROFILE_WORDS * 7) for w in WEEKS}
            profiles = load_profiles() if os.path.exists(PROFILE_MANIFEST) else placeholder
            body = dict(max_cost(e7.definitions_text(), profiles),
                        profiles="sealed" if profiles is not placeholder else f"placeholder of {MAX_PROFILE_WORDS * 7} characters")
        elif args.cmd == "render-example":
            q = e7.load_week(args.week)
            card = next(c for c in e7.required_cards(q) if args.card in (None, c["card_id"]))
            system, user = render(q, card, e7.definitions_text(), load_profiles()[args.week])
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
