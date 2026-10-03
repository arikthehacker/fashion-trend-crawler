"""EXP-005 holdout C2: the one-time generation run over the frozen C1 packets, and the
human review deck built from its frozen raw outputs.

Owner authorization C2 (2026-10-03): run the 30 frozen questions once with the frozen
evidence packets, Prompt v2, AnswerV2 and the one-retry schema rule, with no retrieval rerun.
exp005_v2.answer_question retrieves internally, so this module sends each frozen packet's
messages (hash-checked) and repeats only the steps answer_question takes after retrieval,
using the same frozen functions (build_messages, the provider, parse, estimate_cost, render,
validate_output). test_exp005_holdout_c2.py checks record-for-record parity with
answer_question on scripted responses. The frozen C1 sufficiency labels are never read here.

Before the first provider call, preflight() checks every pinned fingerprint, the pipeline
identity, the packets and the conservative projected cost (<= 0.50 USD). During the run a
call is made only if the spend so far plus that call's conservative bound stays within
0.50 USD; otherwise the run stops and is recorded NOT EVALUABLE.

usage:
  python src/exp005_holdout_c2.py preflight           # no provider call
  ARI3_LIVE_LLM=approved python src/exp005_holdout_c2.py run   # once
  python src/exp005_holdout_c2.py deck                # the C2 review queue from the frozen outputs
"""

import argparse
import collections
import json
import os
import random
import sys
import time
from datetime import datetime, timezone

import exp005 as v1
import exp005_holdout as h
import exp005_holdout_freeze as fz
import exp005_v2 as v2

RUN_DIR = os.path.join(h.HOLDOUT, "runs", "c2-v1")
OUTPUTS = os.path.join(RUN_DIR, "outputs.jsonl")
PREFLIGHT = os.path.join(RUN_DIR, "preflight.json")
RUN_MANIFEST = os.path.join(RUN_DIR, "run_manifest.json")
REVIEWS = os.path.join(h.HOLDOUT, "reviews", "c2_semantic_reviews_v1.jsonl")
QUEUE_NAME = "exp005_holdout_c2_review"
CAP_USD = 0.50
DECK_SEED = 20261004
EXPECTED = {  # from the owner's C2 authorization
    "protocol": "0e0e6a98fa3982e246e12a959b50ae5ede237748275a626c017c8bf5c6232af5",
    "questions": "a6b789672fe2ac25f76f07fd7f571a3dfcb8e0a2c6d1b32ba7745d04754236ac",
    "packet_manifest": "cfb304502588deabf23350f1a2d718321d49b46fdefcf07c3e831abf7f61dbc6",
    "packets": "ad67316abfa8306c66ed002036fe4438883409a813bc3a0dfdc0af8eb3d5bc6a",
    "sufficiency_review": "ad1ca24ed2d422a757551df4995d8de4b132ef1b9870e8ac4c25c99e375992bf",
    "amendment": "9c5fde6cdedc74421dd3929946f2581df6998c127fe041c210339ded09563cab",
    "prompt_v2": "efea461f8e079eb8c25a3e8f5acb371d5e01b9bf18c617aec123b01f62a7afce",
    "schema_v2": "47b747c14b5301df9a790538205e8fdd1014019a136671e38e8d094f06c4a5ee",
    "protocol_v2": "87e88618c83167157c7ce0102c50b9a9ca173bf82309841b3f82e3d60d2c6739",
    "retriever": "3b55fcebbb08ec54b87198ab4a18e2f1b2bd0b922c6677428f525ceeadfd6b21",
}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def call_bound_usd(messages):
    """Conservative bound for one call, as in exp005.max_cost: one token per input character,
    full max_tokens output, peak prices."""
    from llm_deepseek import PRICING
    price = PRICING[v1.PROVIDER_SETTINGS["model"]]
    chars = sum(len(m["content"]) for m in messages)
    return (chars * price["input_cache_miss"][1] + v1.PROVIDER_SETTINGS["max_tokens"] * price["output"][1]) / 1_000_000


def projected_total(deck, packets, prompt_text):
    """exp005.max_cost's rule on the frozen packets: two attempts per question, the retry
    messages carrying a 600-character schema error."""
    per = {}
    for q, p in zip(deck, packets):
        if p["status"] != "packet_built":
            per[q.question_id] = 0.0
            continue
        per[q.question_id] = round(v1.MAX_ATTEMPTS * call_bound_usd(
            v1.build_messages(h.app_question(q), p["context"], prompt_text, "x" * 600)), 6)
    return round(sum(per.values()), 6), per


# ---------- preflight (no provider call) ----------

def preflight():
    import rag_answer
    import rag_select as rs
    from rag_eval import sha256_file as normalized_sha
    checks = {}
    files = {"protocol": h.PROTOCOL, "questions": h.FROZEN, "packet_manifest": h.MANIFEST,
             "sufficiency_review": fz.FROZEN_REVIEW, "amendment": fz.AMENDMENT}
    for key, path in files.items():
        checks[f"{key}_sha256"] = h.sha256_file(path) == EXPECTED[key]
        checks[f"{key}_committed_and_pushed"] = rs.rule_is_committed_and_pushed(path)[0]
    with open(h.MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    checks["all_packets_hash"] = h.sha256_json(m["packets"]) == m["packets_sha256"] == EXPECTED["packets"]
    checks["prompt_v2_sha256"] = normalized_sha(v2.PROMPT_V2) == EXPECTED["prompt_v2"]
    checks["schema_v2_sha256"] = rag_answer._schema_sha() == EXPECTED["schema_v2"]
    checks["protocol_v2_sha256"] = normalized_sha(v2.PROTOCOL_V2) == EXPECTED["protocol_v2"]
    checks["retriever_sha256"] = normalized_sha(rs.RETRIEVER_PATH) == EXPECTED["retriever"]
    try:
        identity = rag_answer.verify_identity()
        checks["ask_ari3_identity"] = True
    except rag_answer.PipelineIdentityError as e:
        identity, checks["ask_ari3_identity"] = {"error": str(e)}, False
    checks["store_snapshot_sha256"] = h.sha256_file(h.SNAPSHOT) == m["store_snapshot"]["sha256"]
    checks["local_packets_match_manifest"] = fz.packets_unchanged(m)
    deck, packets = h.load_deck(), h.load_packets()
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    checks["question_order_matches_packets"] = [q.question_id for q in deck] == [p["question_id"] for p in packets]
    checks["retrieval_query_is_question"] = all(q.retrieval_query == q.question == p["retrieval_query"]
                                                for q, p in zip(deck, packets))
    checks["first_attempt_messages_rebuild_from_frozen_context"] = all(
        h.sha256_json(v1.build_messages(h.app_question(q), p["context"], prompt_text)) == p["messages_sha256"]
        for q, p in zip(deck, packets) if p["status"] == "packet_built")
    checks["provider_settings_match_protocol_v2"] = identity.get("provider_settings") == v1.PROVIDER_SETTINGS
    checks["not_run_before"] = not os.path.exists(RUN_DIR)
    total, per = projected_total(deck, packets, prompt_text)
    checks["projected_total_within_cap"] = total <= CAP_USD
    return {"checked_at": _now(), "passed": all(checks.values()), "checks": checks,
            "projected_total_usd": total, "cap_usd": CAP_USD, "projected_per_question_usd": per,
            "projection_rule": "exp005.max_cost: 1 token per input character, 2 attempts, full max_tokens output, "
                               "peak prices, retry messages with a 600-character schema error",
            "expected_fingerprints": EXPECTED, "provider_settings": v1.PROVIDER_SETTINGS,
            "runner_sha256": h.sha256_file(os.path.abspath(__file__)),
            "api_key_present": bool(os.environ.get("DEEPSEEK_API_KEY")),
            "live_gate_set": os.environ.get("ARI3_LIVE_LLM") == "approved"}


# ---------- generation over one frozen packet ----------

class Budget:
    def __init__(self, cap=CAP_USD):
        self.cap, self.spent, self.calls, self.stopped = cap, 0.0, 0, False


def generate(q, packet, provider, corpus, prompt_text, budget, cost_fn=None):
    """exp005_v2.answer_question from the point its context exists, on the frozen packet.
    Same record fields, same retry rule, same statuses, plus the cost-cap stop."""
    aq = h.app_question(q)
    ids = packet["item_ids"]
    record = {"question_id": q.question_id, "question": q.question, "retrieval_query": aq.query,
              "filters": q.filters.model_dump(mode="json", exclude_none=True), "attempts": [],
              "retrieval": {"item_ids": ids, "source": "frozen C1 packet (no retrieval rerun)"}}
    if packet["status"] == "context_invalid":
        record.update(status="context_invalid", context_violations=packet["context_violations"])
        return record
    if packet["status"] == "system_abstention":
        record.update(status="system_abstention", note="no eligible evidence; the provider was not called")
        return record
    context = packet["context"]
    record["context_sha256"] = h.sha256_json(context)
    schema_error, answer = None, None
    for attempt in range(1, v1.MAX_ATTEMPTS + 1):
        messages = v1.build_messages(aq, context, prompt_text, schema_error)
        if attempt == 1 and h.sha256_json(messages) != packet["messages_sha256"]:
            raise RuntimeError(f"{q.question_id}: first-attempt messages differ from the frozen packet")
        bound = call_bound_usd(messages)
        if budget.spent + bound > budget.cap:
            budget.stopped = True
            record.update(status="cost_cap_stop", note=f"spent {budget.spent:.6f} + bound {bound:.6f} > cap {budget.cap}")
            return record
        t0 = time.perf_counter()
        budget.calls += 1
        try:
            out = provider.generate_json(messages)
        except Exception as e:
            budget.spent += bound  # unknown spend on a failed call: count the bound
            record.update(status="provider_error", error=f"{type(e).__name__}: {e}"[:300])
            return record
        answer, schema_error = v2.parse(out.text)
        cost = cost_fn(getattr(provider, "model", out.model), out.usage, datetime.now(timezone.utc)) if cost_fn else None
        budget.spent += cost if cost is not None else (bound if cost_fn else 0.0)
        record["attempts"].append({"attempt": attempt, "raw_output": out.text, "schema_valid": answer is not None,
                                   "schema_error": schema_error, "model": out.model, "usage": out.usage,
                                   "finish_reason": out.finish_reason, "request_id": out.request_id,
                                   "latency_ms": round(1000 * (time.perf_counter() - t0), 1),
                                   "estimated_cost_usd": cost, "messages_sha256": h.sha256_json(messages)})
        if answer is not None:
            break
    if answer is None:
        record.update(status="rejected_schema")
        return record
    record["answer"] = answer.model_dump(mode="json")
    record["rendered_answer"] = v2.render(answer)
    record["validation"] = v2.validate_output(corpus, answer, ids, q.filters)
    record["status"] = ("rejected_citation" if not record["validation"]["valid"] else
                        "model_abstention" if answer.insufficient_evidence else "answered")
    return record


# ---------- the run (once) ----------

DETERMINISTIC_FAILURES = ("rejected_citation", "context_invalid", "rejected_schema", "provider_error")


def summarize(records, budget):
    calls = [a for r in records for a in r["attempts"]]
    called = [r for r in records if r["attempts"] or r["status"] == "provider_error"]
    final_valid = [r for r in called if "answer" in r]
    first_valid = [r for r in records if r["attempts"] and r["attempts"][0]["schema_valid"]]
    failures = {r["question_id"]: r["status"] for r in records if r["status"] in DETERMINISTIC_FAILURES}
    for r in records:
        v = r.get("validation")
        if v and r["status"] not in DETERMINISTIC_FAILURES and (not v["valid"] or v["provenance_resolved"] < v["provenance_total"]):
            failures[r["question_id"]] = "validation_violation"
    tokens = collections.Counter()
    for a in calls:
        tokens.update({k: v for k, v in (a.get("usage") or {}).items() if isinstance(v, (int, float))})
    return {"questions": len(records), "status_counts": dict(collections.Counter(r["status"] for r in records)),
            "provider_calls": budget.calls, "attempts_recorded": len(calls),
            "schema_retries": sum(1 for r in records if len(r["attempts"]) > 1),
            "first_attempt_schema_valid": f"{len(first_valid)}/{len(called)}",
            "final_schema_valid": f"{len(final_valid)}/{len(called)}",
            "deterministic_integrity_failures": failures, "tokens": dict(tokens),
            "estimated_cost_usd": round(sum(a["estimated_cost_usd"] or 0 for a in calls), 8),
            "budget_spent_usd": round(budget.spent, 8), "cost_cap_stop": budget.stopped,
            "evaluable": not budget.stopped and len(records) == h.N_QUESTIONS}


def run(provider=None):
    import llm_deepseek
    import rag_answer
    from rag_corpus import open_corpus
    pre = preflight()
    if not pre["passed"]:
        print(json.dumps({"stopped_before_first_call": True, "failed": sorted(k for k, v in pre["checks"].items() if not v),
                          "projected_total_usd": pre["projected_total_usd"]}, indent=1))
        return 1
    os.makedirs(RUN_DIR)
    with open(PREFLIGHT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(pre, f, indent=1, ensure_ascii=False)
        f.write("\n")
    provider = provider or rag_answer._live_provider()
    deck, packets = h.load_deck(), h.load_packets()
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    with open(h.MANIFEST, encoding="utf-8") as f:
        snapshot_sha = json.load(f)["store_snapshot"]["sha256"]
    corpus = open_corpus(h.SNAPSHOT)
    budget, records, started = Budget(), [], _now()
    with open(OUTPUTS, "x", encoding="utf-8", newline="\n") as out:
        for q, p in zip(deck, packets):
            r = generate(q, p, provider, corpus, prompt_text, budget, llm_deepseek.estimate_cost)
            r.update(run="c2-v1", protocol_sha256=EXPECTED["protocol"], packet_messages_sha256=p.get("messages_sha256"),
                     cited_item_ids=sorted({i for c in (r.get("answer") or {}).get("claims", []) for i in c["supporting_item_ids"]}
                                           | {i for x in (r.get("answer") or {}).get("limitations", [])
                                              for i in x["supporting_item_ids"]}))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            out.flush()
            records.append(r)
            if budget.stopped:
                break
    corpus.close()
    ended = _now()
    rows = [{"question_id": r["question_id"], "status": r["status"], "context_sha256": r.get("context_sha256"),
             "attempts": len(r["attempts"]), "record_sha256": h.sha256_json(r)} for r in records]
    body = {"version": "exp005-holdout-c2-run-v1", "run": "c2-v1", "started_at": started, "ended_at": ended,
            "authorization": "owner C2 authorization, 2026-10-03 (one run, 30 questions, 0.50 USD hard cap)",
            "inputs": {**{f"{k}_sha256": v for k, v in EXPECTED.items()},
                       "store_snapshot_sha256": snapshot_sha,
                       "preflight_sha256": h.sha256_file(PREFLIGHT)},
            "provider": provider.config(), "summary": summarize(records, budget),
            "outputs_sha256": h.sha256_file(OUTPUTS), "records_sha256": h.sha256_json(rows), "records": rows}
    with open(RUN_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k: v for k, v in body.items() if k != "records"}, indent=1, ensure_ascii=False))
    return 0


# ---------- the C2 human review deck ----------

def _packet_items(packet, ids):
    by = {e["item_id"]: e for e in packet["context"]}
    out = []
    for i in ids:
        e = by.get(i)
        if e is None:
            out.append(f"item {i}: NOT IN THE PACKET\n")
            continue
        seen = f"  |  first seen {e['first_seen_at']}" if "first_seen_at" in e else ""
        out.append(f"item {e['item_id']}  |  {e['outlet']}  |  {e['sector_group']}  |  published {e['published_at']}"
                   f"{seen}  |  {e['language']}\n{e['headline'] or '(no headline)'}\n{(e['excerpt'] or '').strip()}\n"
                   f"{e['url']}\n")
    return "\n".join(out)


def _answer_text(a):
    claims = "\n".join(f"{n}. {c['text']}  (items {', '.join(map(str, c['supporting_item_ids']))})"
                       for n, c in enumerate(a["claims"]))
    lims = "\n".join(f"- {x['text']}" + (f"  (items {', '.join(map(str, x['supporting_item_ids']))})"
                                         if x["supporting_item_ids"] else "") for x in a["limitations"]) or "(none)"
    return f"CLAIMS\n{claims or '(none: insufficient evidence)'}\n\nLIMITATIONS\n{lims}"


def review_tasks(records, packets):
    """Protocol c2.review: claim_support for every claim and cited limitation, limitation_uncited
    for every uncited limitation, answer_completeness for every answered question. Only outputs
    that passed validation. Abstention correctness comes from the frozen C1 labels, so there is
    no abstention card. Cards never show the C1 label. Questions come in a fixed shuffled order,
    a question's cards together."""
    import exp005_review_v2 as rv2
    by_packet = {p["question_id"]: p for p in packets}
    order = [r for r in records if r["status"] in ("answered", "model_abstention")]
    random.Random(DECK_SEED).shuffle(order)
    tasks = []
    for r in order:
        p, a = by_packet[r["question_id"]], r["answer"]
        head = {"question_id": r["question_id"], "question": r["question"]}
        packet = "SUPPLIED EVIDENCE PACKET\n\n" + h.packet_text(p)
        for n, c in enumerate(a["claims"]):
            tasks.append({**head, "task_id": f"{r['question_id']}:claim {n}", "kind": "claim_support",
                          "target": f"claim {n}",
                          "body": f"CLAIM {n}\n{c['text']}\n\nCITED EVIDENCE (as in the packet)\n\n"
                                  f"{_packet_items(p, c['supporting_item_ids'])}"})
        for n, lim in enumerate(a["limitations"]):
            if lim["supporting_item_ids"]:
                tasks.append({**head, "task_id": f"{r['question_id']}:limitation {n}", "kind": "claim_support",
                              "target": f"limitation {n}",
                              "body": f"LIMITATION {n} (cites items)\n{lim['text']}\n\nCITED EVIDENCE (as in the packet)\n\n"
                                      f"{_packet_items(p, lim['supporting_item_ids'])}"})
            else:
                tasks.append({**head, "task_id": f"{r['question_id']}:limitation {n}", "kind": "limitation_uncited",
                              "target": f"limitation {n}",
                              "body": f"LIMITATION {n} (cites no item)\n{lim['text']}\n\n{packet}"})
        if r["status"] == "answered":
            tasks.append({**head, "task_id": f"{r['question_id']}:completeness", "kind": "answer_completeness",
                          "target": "answer", "body": f"{_answer_text(a)}\n\n{packet}"})
    for t in tasks:
        t["prompt"] = rv2.PROMPTS[t["kind"]]
        t["options"] = [{"key": k, "label": label, "value": v} for k, label, v in rv2.OPTIONS[t["kind"]]]
    return tasks


def write_deck():
    import label_tool
    with open(OUTPUTS, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": "Answer review (EXP-005 holdout C2)",
             "outputs_sha256": h.sha256_file(OUTPUTS), "run_manifest_sha256": h.sha256_file(RUN_MANIFEST),
             "notes": True, "reviews_path": os.path.relpath(REVIEWS, h.ROOT).replace(os.sep, "/"),
             "seed": DECK_SEED, "tasks": review_tasks(records, h.load_packets()), "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue), queue


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["preflight", "run", "deck"])
    args = ap.parse_args(argv)
    if args.cmd == "preflight":
        pre = preflight()
        print(json.dumps({k: v for k, v in pre.items() if k not in ("projected_per_question_usd", "expected_fingerprints")},
                         indent=1))
        return 0 if pre["passed"] else 1
    if args.cmd == "run":
        return run()
    path, queue = write_deck()
    print(json.dumps({"queue": path, "tasks": len(queue["tasks"]),
                      "by_kind": dict(collections.Counter(t["kind"] for t in queue["tasks"])),
                      "reviews_path": queue["reviews_path"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
