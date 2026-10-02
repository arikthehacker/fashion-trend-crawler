"""EXP-005 SC-1: schema-capacity DEV comparison, Prompt v2 (A) against Prompt v2.1 (B).

Prompt v2.1 is Prompt v2 with one appended section that states the schema v2 size
limits. Schema v2, the serializer, the frozen hybrid retriever, the provider settings
and the retry policy are unchanged. Each question goes through the frozen v2 pipeline
once per condition, and both conditions must receive the same retrieval and the same
evidence packet (checked by context_sha256). Every attempt is kept.

usage:
  python src/exp005_schema.py select-batch      # once, before any output
  python src/exp005_schema.py freeze-protocol   # once, after the batch; then commit and push
  python src/exp005_schema.py estimate-cost
  python src/exp005_schema.py run               # once; needs ARI3_LIVE_LLM=approved
  python src/exp005_schema.py make-deck         # the blind review deck
"""

import argparse
import collections
import hashlib
import json
import os
import re
import statistics
import sys
from datetime import datetime, timezone

import exp005 as v1
import exp005_adjudicate as adj
import exp005_review_v2 as rv2
import exp005_v2 as v2

SC = os.path.join(v1.EXP, "schema-capacity")
PROMPT_V21 = os.path.join(SC, "protocol", "prompt_v2_1.txt")
PROTOCOL = os.path.join(SC, "protocol", "protocol_sc1.json")
RUN = os.path.join(SC, "runs", "sc-batch-1")
BATCH = os.path.join(RUN, "batch.json")
OUTPUTS = os.path.join(RUN, "outputs.jsonl")
SUMMARY = os.path.join(RUN, "summary.json")
BLIND_KEY = os.path.join(RUN, "blind_key.json")
REVIEWS = os.path.join(SC, "reviews", "sc-batch-1_blind_reviews.jsonl")
QUEUE_NAME = "exp005_sc1_blind"
TITLE = "Schema-capacity blind review (EXP-005 SC-1)"
USED = ("q003", "q013", "q015", "q016", "q029", "q005", "q017", "q020", "q023", "q031")
CONDITIONS = {"A": v2.PROMPT_V2, "B": PROMPT_V21}
BLIND_SEED = "exp005-sc1-blind-v1"
CAPS = ("claim_count", "claim_length", "limitation_length")
CODE_FILES = v2.CODE_FILES_V2 + ("exp005_review_v2.py", "exp005_adjudicate.py", "exp005_schema.py")
GATE_USD = 5.0


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------- batch ----------

def select_batch():
    """Eight fresh DEV questions by fixed rules, chosen before any output. Rarer kinds first."""
    import rag_questions as rq
    from rag_corpus import eligible_ids, open_corpus
    from rag_eval import load_gold, load_split
    from rag_index import Index
    questions, qm = rq.load_frozen()
    split = load_split(qm["questions_sha256"])
    gold, _ = load_gold()
    dev = sorted((q for q in questions if q.question_id in set(split["dev"]) and q.question_id not in USED),
                 key=lambda q: q.question_id)
    rel = {q.question_id: {i for i, v in gold.get(q.question_id, {}).items() if v == "relevant"} for q in dev}
    rows = [json.loads(line) for line in open(os.path.join(v1.EXP004, "results", "dev-retrieval-v1.per_question.jsonl"),
                                              encoding="utf-8")]
    top10 = {r["question_id"]: set(r["ranking"]) for r in rows if r["candidate"] == "hybrid"}
    in_top = lambda q: len(rel[q.question_id] & top10.get(q.question_id, set()))
    corpus, index = open_corpus(), Index(os.path.join(v1.ROOT, "data", "index", "exp004-v1"))
    has_filters = lambda q: bool(q.filters.model_dump(exclude_none=True, exclude_defaults=True))
    picks, rules = [], {}

    def take(name, rule, candidates):
        chosen = next((q for q in candidates if q.question_id not in picks), None)
        rules[name] = {"rule": rule, "question_id": chosen.question_id if chosen else None}
        if chosen:
            picks.append(chosen.question_id)

    take("likely_abstention", "lowest ID: drafted unanswerable, no relevant item, at least one eligible item",
         [q for q in dev if not q.answerable_expected and not rel[q.question_id]
          and set(eligible_ids(corpus, q.filters)) & set(index.row)])
    take("temporal", "lowest ID: query_type temporal, at least one relevant item",
         [q for q in dev if q.query_type == "temporal" and rel[q.question_id]])
    take("filtered", "lowest ID: query_type source_filter or sector_filter, at least one relevant item",
         [q for q in dev if q.query_type in ("source_filter", "sector_filter") and rel[q.question_id]])
    take("low_evidence", "fewest relevant items in the frozen hybrid DEV top 10, at least one (ties: lowest ID)",
         sorted((q for q in dev if in_top(q) >= 1), key=lambda q: (in_top(q), q.question_id)))
    for n in (1, 2):
        take(f"evidence_rich_{n}", "most relevant items in the frozen hybrid DEV top 10 (ties: lowest ID)",
             sorted((q for q in dev if rel[q.question_id]), key=lambda q: (-in_top(q), q.question_id)))
    for n in (1, 2):
        take(f"term_{n}", "lowest ID: query_type term or general, no filters, at least one relevant item",
             [q for q in dev if q.query_type in ("term", "general") and not has_filters(q) and rel[q.question_id]])
    return {"batch": "sc-batch-1", "selected_before_any_output": True, "excluded_used": list(USED),
            "rules": rules, "question_ids": picks}


# ---------- protocol ----------

def prompt_difference():
    a = _read(v2.PROMPT_V2).encode()
    b = _read(PROMPT_V21).encode()
    if not b.startswith(a):
        raise RuntimeError("Prompt v2.1 does not begin with the exact bytes of Prompt v2")
    return {"kind": "appended section only", "appended_text": b[len(a):].decode(), "prefix_identical_bytes": len(a)}


def code_sha():
    from rag_eval import sha256_file
    return {f: sha256_file(os.path.join(v1.SRC, f)) for f in CODE_FILES}


def protocol_body():
    from rag_eval import sha256_file
    import rag_select as rs
    with open(v2.PROTOCOL_V2, encoding="utf-8") as f:
        p2 = json.load(f)
    return {
        "version": "exp005-sc1-protocol-v1", "experiment": "EXP-005 SC-1 schema-capacity DEV comparison",
        "decided_by": "the owner, directive 036",
        "question": "Does stating the existing schema v2 size limits in the prompt raise first-attempt schema validity "
                    "without new integrity failures or a material loss of grounding or completeness?",
        "conditions": {"A": {"name": "Prompt v2 baseline", "path": "protocol/prompt_v2.txt",
                             "sha256": sha256_file(v2.PROMPT_V2)},
                       "B": {"name": "Prompt v2.1 explicit caps", "path": "schema-capacity/protocol/prompt_v2_1.txt",
                             "sha256": sha256_file(PROMPT_V21)}},
        "prompt_difference": prompt_difference(),
        "schema": {"version": "exp005-schema-v2", "sha256": hashlib.sha256(v2.schema_json().encode()).hexdigest(),
                   "changed": False, "caps": {"claims": 4, "claim_text_chars": 400, "limitations": 3,
                                              "limitation_text_chars": 300, "citations_per_statement": "1 to 10"}},
        "provider_settings": v1.PROVIDER_SETTINGS,
        "serializer": {"version": v1.SERIALIZER_VERSION, "max_items": v1.MAX_ITEMS, "max_headline": v1.MAX_HEADLINE,
                       "max_excerpt": v1.MAX_EXCERPT, "max_context_chars": v1.MAX_CONTEXT_CHARS},
        "retriever": {"path": os.path.relpath(rs.RETRIEVER_PATH, v1.ROOT).replace(os.sep, "/"),
                      "sha256": sha256_file(rs.RETRIEVER_PATH), "method": "hybrid, auto mode, top 10"},
        "retry_policy": p2["unchanged_from_v1"]["retry_policy"].replace("schema v1", "schema v2"),
        "pairing": "Each question goes through the frozen v2 pipeline once per condition, A then B. Retrieval is run "
                   "twice per question before any call and must agree. After both calls, the two records must have "
                   "the same retrieval item IDs in the same order and the same context_sha256, or the run stops. "
                   "Only the system prompt differs.",
        "batch": {"path": "schema-capacity/runs/sc-batch-1/batch.json", "sha256": sha256_file(BATCH)},
        "metrics": {
            "primary": "first-attempt schema validity: schema-valid initial responses / all initial responses, per "
                       "condition. Never replaced by final validity. A system abstention (empty context) has no "
                       "initial response and is excluded from the denominator.",
            "secondary": ["first-attempt valid count", "retry count", "final schema-valid count",
                          "claim_count, claim_length, limitation_length and other violations on first attempts "
                          "(from the parser error; one attempt can have several)", "tokens", "latency",
                          "estimated cost", "deterministic validation as in v2"],
            "semantic": "rubric v2 under the context-only evidence boundary (amendment 2026-10-01): claim support, "
                        "completeness, context sufficiency, abstention, limitations. metrics_v2 per condition, after "
                        "the owner's blind review is complete and frozen."},
        "comparison_rule": {
            "order": "the first rule that applies",
            "definitions": {
                "first_valid": "first-attempt schema-valid count",
                "cap_violations_B": "B first attempts with at least one claim_count, claim_length or "
                                    "limitation_length violation",
                "integrity_failures": "outputs with any deterministic validation violation, or status "
                                      "rejected_citation or context_invalid",
                "material_human_regression (impl)": "B is worse than A by at least 2 on any of: grounded outputs, "
                                                    "UNSUPPORTED statements, PARTIAL or INSUFFICIENT completeness "
                                                    "judgments, incorrect or missed abstentions (8 questions, so a "
                                                    "difference of 1 is treated as noise)"},
            "rules": [
                "FORMAT_GROUNDING_TRADEOFF: first_valid B > A, and a material human regression",
                "SCHEMA_AWARENESS: first_valid B > A, cap_violations_B <= 1, integrity_failures B <= A, and no "
                "material human regression",
                "SCHEMA_CAPACITY_CONFIRMED: cap_violations_B >= 3 of 8 (B still often breaks the caps it was told)",
                "INCONCLUSIVE: otherwise"],
            "frozen": "not changed after any output exists"},
        "live_call_scope": {"questions": 8, "conditions": 2, "max_initial_generations": 16,
                            "max_schema_retries": 16, "semantic_retries": 0, "test_calls": 0,
                            "authorization": "directive 036, LIVE DEV GENERATION AUTHORIZED", "cost_gate_usd": GATE_USD},
        "blind_review": {"deck": TITLE, "seed": BLIND_SEED, "log": "schema-capacity/reviews/sc-batch-1_blind_reviews.jsonl",
                         "hidden": "condition, prompt name, call order and format outcome"},
        "code_sha256": code_sha(),
    }


def check_frozen():
    """The frozen protocol still matches every input it fingerprints."""
    from rag_eval import sha256_file
    import rag_select as rs
    with open(PROTOCOL, encoding="utf-8") as f:
        p = json.load(f)
    checks = {"prompt_A": p["conditions"]["A"]["sha256"] == sha256_file(v2.PROMPT_V2),
              "prompt_B": p["conditions"]["B"]["sha256"] == sha256_file(PROMPT_V21),
              "schema": p["schema"]["sha256"] == hashlib.sha256(v2.schema_json().encode()).hexdigest(),
              "provider": p["provider_settings"] == v1.PROVIDER_SETTINGS,
              "batch": p["batch"]["sha256"] == sha256_file(BATCH),
              "code": p["code_sha256"] == code_sha(),
              "retriever": p["retriever"]["sha256"] == sha256_file(rs.RETRIEVER_PATH)}
    if not all(checks.values()):
        raise RuntimeError(f"a frozen input changed: {checks}")
    return p


# ---------- run ----------

def max_cost(batch):
    total, per = 0.0, {}
    for cond, path in CONDITIONS.items():
        c = v1.max_cost({"question_ids": batch["question_ids"]}, _read(path))
        per[cond] = c
        total += c["max_total_usd"]
    return {"max_total_usd": round(total, 6), "gate_usd": GATE_USD, "per_condition": per}


def violations(schema_error):
    """Categories of a parser error from schema v2 (one attempt can break several caps)."""
    out = []
    for part in (schema_error or "").split("; "):
        if not part:
            continue
        if re.match(r"claims: List should have at most", part):
            out.append("claim_count")
        elif re.match(r"claims\.\d+\.text: String should have at most", part):
            out.append("claim_length")
        elif re.match(r"limitations\.\d+\.text: String should have at most", part):
            out.append("limitation_length")
        else:
            out.append("other")
    return out


def check_pair(a, b):
    if a["retrieval"]["item_ids"] != b["retrieval"]["item_ids"] or a.get("context_sha256") != b.get("context_sha256"):
        raise RuntimeError(f"{a['question_id']}: the two conditions received different evidence")


def run(provider=None, corpus=None, index=None, questions=None):
    import rag_select as rs
    import llm_deepseek
    from rag_eval import run_method, sha256_file
    from rag_validate import check_items
    if os.path.exists(OUTPUTS) or os.path.exists(SUMMARY):
        raise RuntimeError("sc-batch-1 has already run. It runs once.")
    live = provider is None
    if live:
        for path in (PROTOCOL, BATCH, PROMPT_V21):
            ok, info = rs.rule_is_committed_and_pushed(path)
            if not ok:
                raise RuntimeError(f"{os.path.basename(path)}: {info}")
        with open(rs.RETRIEVER_PATH, encoding="utf-8") as f:
            frozen = json.load(f)
        code, index_files = rs.code_and_index_fingerprints()
        if code != frozen["code_sha256"] or index_files != frozen["index_files_sha256"] or \
                rs.current_fingerprints() != frozen["fingerprints"]:
            raise RuntimeError("the frozen EXP-004 retriever or its inputs changed")
    check_frozen()
    with open(BATCH, encoding="utf-8") as f:
        batch = json.load(f)
    if live:
        cost = max_cost(batch)
        if cost["max_total_usd"] > GATE_USD:
            raise RuntimeError(f"estimated maximum cost {cost['max_total_usd']} exceeds the gate")
    if questions is None:
        import rag_questions as rq
        questions = {q.question_id: q for q in rq.load_frozen()[0]}
    if corpus is None:
        from rag_corpus import open_corpus
        from rag_index import Index
        corpus, index = open_corpus(), Index(os.path.join(v1.ROOT, "data", "index", "exp004-v1"))
    for qid in batch["question_ids"]:  # retrieval must be deterministic and valid before any call
        q = questions[qid]
        first, _ = run_method(corpus, index, q, "hybrid", "auto", v1.MAX_ITEMS)
        second, _ = run_method(corpus, index, q, "hybrid", "auto", v1.MAX_ITEMS)
        if first != second or check_items(corpus, first, q.filters):
            raise RuntimeError(f"{qid}: retrieval is not repeatable or not valid")
    if live:
        p = v1.PROVIDER_SETTINGS
        provider = llm_deepseek.DeepSeekProvider(model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
                                                 max_tokens=p["max_tokens"], timeout=p["timeout_s"],
                                                 max_retries=p["transport_retries"], thinking=p["thinking"],
                                                 allow_live=True)
    prompts = {c: _read(path) for c, path in CONDITIONS.items()}
    protocol_sha = sha256_file(PROTOCOL)
    records = []
    os.makedirs(RUN, exist_ok=True)
    with open(OUTPUTS, "x", encoding="utf-8", newline="\n") as out:
        for qid in batch["question_ids"]:
            pair = []
            for cond in ("A", "B"):
                r = v2.answer_question(questions[qid], provider, corpus, index, prompts[cond],
                                       llm_deepseek.estimate_cost if live else None)
                r.update(run="sc-batch-1", role="fresh", condition=cond, prompt_sha256=sha256_file(CONDITIONS[cond]),
                         protocol_sha256=protocol_sha)
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
                out.flush()
                pair.append(r)
            records += pair
            check_pair(*pair)
    body = {"run": "sc-batch-1", "protocol_sha256": protocol_sha, "provider": provider.config() if live else "scripted",
            "max_cost_estimate": cost if live else None, "format": format_metrics(records),
            "deterministic": {c: v1.deterministic_summary([r for r in records if r["condition"] == c]) for c in "AB"},
            "pairs_identical_evidence": len(batch["question_ids"]), "outputs_sha256": sha256_file(OUTPUTS),
            "finished_at": _now()}
    with open(SUMMARY, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def format_metrics(records):
    out = {}
    for c in ("A", "B"):
        rs_ = [r for r in records if r["condition"] == c]
        called = [r for r in rs_ if r["attempts"]]
        first = [r["attempts"][0] for r in called]
        cats = collections.Counter(v for a in first if not a["schema_valid"] for v in set(violations(a["schema_error"])))
        all_attempts = [a for r in called for a in r["attempts"]]
        tok = lambda xs, k: sum((a.get("usage") or {}).get(k, 0) or 0 for a in xs)
        lat = [a["latency_ms"] for a in all_attempts]
        valid_first = sum(a["schema_valid"] for a in first)
        out[c] = {
            "questions": len(rs_), "initial_responses": len(first),
            "first_attempt_valid": valid_first,
            "first_attempt_valid_rate": round(valid_first / len(first), 4) if first else None,
            "retries": sum(len(r["attempts"]) > 1 for r in called),
            "final_schema_valid": sum(r["status"] not in ("rejected_schema", "provider_error") for r in called),
            "first_attempt_violations": {k: cats.get(k, 0) for k in CAPS + ("other",)},
            "first_attempts_with_cap_violation": sum(1 for a in first if set(violations(a["schema_error"])) & set(CAPS)),
            "first_attempt_errors": {r["question_id"]: r["attempts"][0]["schema_error"] for r in called
                                     if not r["attempts"][0]["schema_valid"]},
            "status_counts": dict(collections.Counter(r["status"] for r in rs_)),
            "tokens": {"prompt": tok(all_attempts, "prompt_tokens"), "completion": tok(all_attempts, "completion_tokens"),
                       "first_attempt_completion": tok(first, "completion_tokens")},
            "latency_ms": {"median": round(statistics.median(lat), 1) if lat else None,
                           "total": round(sum(lat), 1)},
            "estimated_cost_usd": round(sum(a.get("estimated_cost_usd") or 0 for a in all_attempts), 6),
            "integrity_failures": sum(1 for r in rs_ if r["status"] in ("rejected_citation", "context_invalid")
                                      or (r.get("validation") and not r["validation"]["valid"]))}
    return out


def classify(fmt, human=None):
    """The frozen comparison rule. `human` is {"A": metrics_v2, "B": metrics_v2} after the owner's review."""
    a, b = fmt["A"], fmt["B"]
    better = b["first_attempt_valid"] > a["first_attempt_valid"]
    regression = None
    if human is not None:
        ha, hb = human["A"], human["B"]
        bad = lambda h: (h["completeness"]["PARTIAL"] + h["completeness"]["INSUFFICIENT"])
        wrong_abst = lambda h: h["abstention"]["incorrect"] + h["abstention"]["missed"]
        regression = (ha["grounded"] - hb["grounded"] >= 2 or hb["unsupported"] - ha["unsupported"] >= 2
                      or bad(hb) - bad(ha) >= 2 or wrong_abst(hb) - wrong_abst(ha) >= 2)
    if better and regression:
        return "FORMAT_GROUNDING_TRADEOFF"
    if better and b["first_attempts_with_cap_violation"] <= 1 and b["integrity_failures"] <= a["integrity_failures"]:
        return "SCHEMA_AWARENESS" if regression is False else "PENDING_HUMAN_REVIEW"
    if b["first_attempts_with_cap_violation"] >= 3:
        return "SCHEMA_CAPACITY_CONFIRMED"
    return "INCONCLUSIVE" if regression is not None else "PENDING_HUMAN_REVIEW"


# ---------- blind review ----------

def blind_id(qid, cond):
    return "ans-" + hashlib.sha256(f"{BLIND_SEED}|{qid}|{cond}".encode()).hexdigest()[:6]


def _order_key(text):
    return hashlib.sha256(f"{BLIND_SEED}|order|{text}".encode()).hexdigest()


def build_blind_tasks(records, questions, corpus):
    """Blind tasks: the condition, prompt and call order are not shown. Sufficiency is judged
    once per question (the packet is identical in both conditions)."""
    from exp005_review import OPTIONS, PROMPTS
    by_q = collections.defaultdict(dict)
    for r in records:
        by_q[r["question_id"]][r["condition"]] = r
    tasks = []
    for qid in sorted(by_q, key=_order_key):
        pair = by_q[qid]
        check_pair(pair["A"], pair["B"])
        q = questions[qid]
        packet = adj.rebuild_packet(pair["A"], q, corpus)
        full = adj.packet_text(packet, q)
        head = {"question_id": qid, "question": pair["A"]["question"]}
        meta = (f"FROZEN METADATA\nquestion {qid}, run sc-batch-1, filters "
                f"{json.dumps(pair['A']['filters'], ensure_ascii=False)}\n"
                f"packet sha256 {pair['A']['context_sha256'][:16]}... (rebuilt and verified)")
        tasks.append({**head, "task_id": f"{qid}:sufficiency", "kind": "context_sufficiency", "target": "packet",
                      "prompt": PROMPTS["context_sufficiency"] + " Judge from the packet only.",
                      "body": f"{adj.HEADER}\n\n{meta}\n\n{full}"})
        for cond in sorted("AB", key=lambda c: _order_key(blind_id(qid, c))):
            r, b = pair[cond], blind_id(qid, cond)
            if r["status"] not in ("answered", "model_abstention"):
                continue
            a = r["answer"]
            label = f"ANSWER {b}"
            if r["status"] == "model_abstention":
                tasks.append({**head, "task_id": f"{qid}:{b}:abstention", "kind": "abstention", "target": "answer",
                              "body": f"{label}: the model said the evidence is insufficient\n\n"
                                      f"{rv2._answer_text(a)}\n\n{full}"})
            for kind_key, items in (("claim", a["claims"]), ("limitation", a["limitations"])):
                for n, st in enumerate(items):
                    target = f"{kind_key} {n}"
                    if st["supporting_item_ids"]:
                        cited = set(st["supporting_item_ids"])
                        sub = adj.packet_text([i for i in packet if i["item_id"] in cited], q).replace(
                            "EVIDENCE PACKET", "CITED ITEMS FROM THE PACKET", 1)
                        tasks.append({**head, "task_id": f"{qid}:{b}:{target}", "kind": "claim_support",
                                      "target": target, "body": f"{label}, {target.upper()}\n{st['text']}\n"
                                                                f"(cites items {', '.join(map(str, sorted(cited)))})"
                                                                f"\n\n{sub}"})
                    else:
                        tasks.append({**head, "task_id": f"{qid}:{b}:{target}", "kind": "limitation_uncited",
                                      "target": target, "body": f"{label}, {target.upper()} (cites no item)\n"
                                                                f"{st['text']}\n\n{full}"})
            if r["status"] == "answered":
                tasks.append({**head, "task_id": f"{qid}:{b}:completeness", "kind": "answer_completeness",
                              "target": "answer", "body": f"{label}\n\n{rv2._answer_text(a)}\n\n{full}"})
    for t in tasks:
        t.setdefault("prompt", (rv2.PROMPTS.get(t["kind"]) or PROMPTS.get(t["kind"], "")) + " Judge from the packet only.")
        t["options"] = [{"key": k, "label": label, "value": v} for k, label, v in rv2.OPTIONS[t["kind"]]]
        if not t["body"].startswith(adj.HEADER):
            t["body"] = f"{adj.HEADER}\n\n{t['body']}"
    return tasks


def make_deck(corpus=None):
    import label_tool
    from item_store import ROOT
    from rag_eval import sha256_file
    import rag_questions as rq
    with open(SUMMARY, encoding="utf-8") as f:
        if sha256_file(OUTPUTS) != json.load(f)["outputs_sha256"]:
            raise RuntimeError("the sc-batch-1 outputs changed")
    if os.path.exists(REVIEWS) and os.path.getsize(REVIEWS):
        raise RuntimeError("the blind review log already has judgments; the deck is not rebuilt")
    if corpus is None:
        from rag_corpus import open_corpus
        corpus = open_corpus()
    records = v1_load(OUTPUTS)
    questions = {q.question_id: q for q in rq.load_frozen()[0]}
    tasks = build_blind_tasks(records, questions, corpus)
    key = {blind_id(r["question_id"], r["condition"]): {"question_id": r["question_id"], "condition": r["condition"]}
           for r in records}
    if not os.path.exists(BLIND_KEY):
        with open(BLIND_KEY, "x", encoding="utf-8", newline="\n") as f:
            json.dump({"seed": BLIND_SEED, "note": "do not open before the blind review is frozen", "key": key}, f,
                      indent=1, sort_keys=True)
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": TITLE, "notes": True,
             "outputs_sha256": sha256_file(OUTPUTS), "reviews_path": os.path.relpath(REVIEWS, ROOT).replace(os.sep, "/"),
             "tasks": tasks, "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue), tasks


def v1_load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv=None):
    from rag_eval import sha256_file
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["select-batch", "freeze-protocol", "estimate-cost", "run", "make-deck"])
    args = ap.parse_args(argv)
    try:
        if args.cmd == "select-batch":
            os.makedirs(RUN, exist_ok=True)
            body = dict(select_batch(), selected_at=_now())
            with open(BATCH, "x", encoding="utf-8", newline="\n") as f:
                json.dump(body, f, indent=1)
        elif args.cmd == "freeze-protocol":
            with open(PROTOCOL, "x", encoding="utf-8", newline="\n") as f:
                json.dump(dict(protocol_body(), frozen_at=_now()), f, indent=1, ensure_ascii=False)
            body = {"protocol": sha256_file(PROTOCOL)}
        elif args.cmd == "estimate-cost":
            with open(BATCH, encoding="utf-8") as f:
                body = max_cost(json.load(f))
        elif args.cmd == "run":
            body = run()
        else:
            path, tasks = make_deck()
            body = {"queue": path, "title": TITLE, "tasks": len(tasks),
                    "by_kind": dict(collections.Counter(t["kind"] for t in tasks))}
    except (RuntimeError, FileExistsError) as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
