"""EXP-005 grounded generation, protocol v1.

  question -> frozen EXP-004 hybrid retriever (top 10) -> context validation
  -> context serializer v1 -> provider (prompt v1) -> schema v1 -> output validation
  -> human review in ARI3 Review

Nothing here writes to the evidence store. Generated text lives only in EXP-005
experiment files.

usage:
  python src/exp005.py freeze-protocol       # writes protocol/protocol_v1.json, once
  python src/exp005.py select-batch          # writes runs/dev-batch-1/batch.json, once
  python src/exp005.py estimate-cost         # the cost gate for the batch
  python src/exp005.py run-batch             # once; needs the live gate and the owner's authorization
"""

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
EXP = os.path.join(ROOT, "experiments", "exp-005-grounded-generation")
EXP004 = os.path.join(ROOT, "experiments", "exp-004-grounded-retrieval")
PROMPT_PATH = os.path.join(EXP, "protocol", "prompt_v1.txt")
PROTOCOL_PATH = os.path.join(EXP, "protocol", "protocol_v1.json")
BATCH_DIR = os.path.join(EXP, "runs", "dev-batch-1")
BATCH_PATH = os.path.join(BATCH_DIR, "batch.json")
OUTPUTS_PATH = os.path.join(BATCH_DIR, "outputs.jsonl")
SUMMARY_PATH = os.path.join(BATCH_DIR, "summary.json")

PROTOCOL_VERSION = "exp005-protocol-v1"
SCHEMA_VERSION = "exp005-schema-v1"
SERIALIZER_VERSION = "exp005-context-v1"
MAX_ITEMS = 10
MAX_HEADLINE = 300
MAX_EXCERPT = 500
MAX_CONTEXT_CHARS = 12000
MAX_ATTEMPTS = 2  # one initial generation, one retry only when the output does not parse
PROVIDER_SETTINGS = {"provider": "deepseek", "model": "deepseek-flash", "endpoint": "https://api.deepseek.com/chat/completions",
                     "api_format": "OpenAI-compatible chat completions", "temperature": 0.0, "top_p": 1.0,
                     "max_tokens": 1000, "thinking": "disabled", "response_format": "json_object", "stream": False,
                     "generations_per_question": 1, "timeout_s": 60, "transport_retries": 2}
CODE_FILES = ("exp005.py", "llm_provider.py", "llm_deepseek.py", "rag_validate.py", "rag_corpus.py")


# ---------- schema v1 ----------

Strict = ConfigDict(extra="forbid", strict=True, frozen=True)


class SummaryV1(BaseModel):
    model_config = Strict
    text: str = Field(min_length=1, max_length=500)
    supporting_item_ids: List[int] = Field(min_length=1, max_length=10)


class ClaimV1(BaseModel):
    model_config = Strict
    text: str = Field(min_length=1, max_length=400)
    supporting_item_ids: List[int] = Field(min_length=1, max_length=5)


class AnswerV1(BaseModel):
    """The model's output. The summary is cited and is reviewed like a claim. There is no
    uncited prose field. URLs are never part of the model's output."""
    model_config = Strict
    insufficient_evidence: bool
    answer_summary: Optional[SummaryV1] = None
    claims: List[ClaimV1] = Field(default_factory=list, max_length=4)
    limitations: List[str] = Field(default_factory=list, max_length=3)

    @field_validator("limitations")
    @classmethod
    def _short(cls, v):
        if any(not 1 <= len(x) <= 300 for x in v):
            raise ValueError("each limitation is 1 to 300 characters")
        return v

    @model_validator(mode="after")
    def _shape(self):
        if self.insufficient_evidence and (self.answer_summary is not None or self.claims):
            raise ValueError("an insufficient-evidence answer has no summary and no claims")
        if not self.insufficient_evidence and (self.answer_summary is None or not self.claims):
            raise ValueError("an answer needs a cited summary and 1 to 4 claims")
        return self


def schema_json():
    return json.dumps(AnswerV1.model_json_schema(), sort_keys=True, separators=(",", ":"))


def parse(raw):
    try:
        return AnswerV1.model_validate_json(raw or ""), None
    except ValidationError as e:
        return None, "; ".join(f"{'.'.join(map(str, err['loc'])) or 'answer'}: {err['msg']}" for err in e.errors())[:600]


# ---------- context serializer v1 ----------

def describe_constraints(filters):
    from rag_review import describe_filters
    return describe_filters(filters.model_dump(exclude_none=True))


def serialize_context(evidence, filters):
    """The evidence packet, in the frozen hybrid ranking order. Fixed fields and caps.
    first_seen_at is included only in replay mode, where it decides eligibility."""
    items = []
    for e in evidence[:MAX_ITEMS]:
        item = {"item_id": e.item_id, "outlet": e.outlet, "sector_group": e.coarse_group or "unknown",
                "published_at": e.published_at}
        if filters.temporal_mode == "replay":
            item["first_seen_at"] = e.first_seen_at
        item.update({"language": e.lang or "unknown", "headline": (e.title or "")[:MAX_HEADLINE],
                     "excerpt": (e.excerpt or "")[:MAX_EXCERPT], "url": e.url})
        items.append(item)
    if len(json.dumps(items, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
        raise RuntimeError("context exceeds its bound")
    return items


def build_messages(question, context, prompt_text, schema_error=None):
    payload = {"question": question.question,
               "constraints": {"description": describe_constraints(question.filters),
                               "filters": question.filters.model_dump(mode="json", exclude_none=True)},
               "evidence": context}
    messages = [{"role": "system", "content": prompt_text},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
    if schema_error:
        messages.append({"role": "user", "content": "Your previous output did not match the required JSON format: "
                                                    f"{schema_error}. Return only the JSON object."})
    return messages


# ---------- validation ----------

def validate_output(corpus, answer, context_ids, filters):
    """Deterministic checks on a parsed answer: membership, corpus, temporal, filters,
    citation presence (enforced by the schema) and provenance."""
    from rag_corpus import get_items
    from rag_validate import check_items
    cited_groups = ([("summary", answer.answer_summary.supporting_item_ids)] if answer.answer_summary else []) + \
        [(f"claim {n}", c.supporting_item_ids) for n, c in enumerate(answer.claims)]
    cited = [i for _, ids in cited_groups for i in ids]
    problems = check_items(corpus, cited, filters)
    context = set(context_ids)
    violations = []
    for where, ids in cited_groups:
        for i in ids:  # every failed check is recorded, so one fault cannot hide another
            if i not in context and problems.get(i) != "nonexistent":
                violations.append({"where": where, "item_id": i, "reason": "not_in_context"})
            if problems.get(i):
                violations.append({"where": where, "item_id": i, "reason": problems[i]})
    stored = {e.item_id: e for e in get_items(corpus, list(dict.fromkeys(cited)))}
    provenance = {i: stored[i].url for i in dict.fromkeys(cited) if i in stored}
    counts = {r: sum(v["reason"] == r for v in violations) for r in
              ("not_in_context", "nonexistent", "published_after_as_of", "first_seen_after_as_of", "fails_filters",
               "missing_provenance")}
    return {"valid": not violations, "violations": violations, "citations": len(cited),
            "membership_valid": counts["not_in_context"] == 0 and counts["nonexistent"] == 0,
            "temporal_violations": counts["published_after_as_of"] + counts["first_seen_after_as_of"],
            "filter_violations": counts["fails_filters"], "nonexistent_citations": counts["nonexistent"],
            "provenance_resolved": len(provenance), "provenance_total": len(set(cited)), "citation_urls": provenance}


def answer_question(question, provider, corpus, index, prompt_text, cost_fn=None):
    """One question through the frozen pipeline. Returns the audit record."""
    from rag_corpus import get_items
    from rag_eval import run_method
    from rag_validate import check_items
    record = {"question_id": question.question_id, "question": question.question, "retrieval_query": question.query,
              "filters": question.filters.model_dump(mode="json", exclude_none=True), "attempts": []}
    ids, seconds = run_method(corpus, index, question, "hybrid", "auto", MAX_ITEMS)
    record["retrieval"] = {"item_ids": ids, "latency_ms": round(1000 * seconds, 1)}
    bad = check_items(corpus, ids, question.filters)
    if bad:
        record.update(status="context_invalid", context_violations=bad)
        return record
    if not ids:
        record.update(status="system_abstention", note="no eligible evidence; the provider was not called")
        return record
    evidence = {e.item_id: e for e in get_items(corpus, ids)}
    context = serialize_context([evidence[i] for i in ids], question.filters)
    record["context_sha256"] = hashlib.sha256(json.dumps(context, ensure_ascii=False).encode()).hexdigest()
    schema_error, answer = None, None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        messages = build_messages(question, context, prompt_text, schema_error)
        t0 = time.perf_counter()
        try:
            out = provider.generate_json(messages)
        except Exception as e:  # the provider's message is already sanitized
            record.update(status="provider_error", error=f"{type(e).__name__}: {e}"[:300])
            return record
        answer, schema_error = parse(out.text)
        cost = cost_fn(getattr(provider, "model", out.model), out.usage, datetime.now(timezone.utc)) if cost_fn else None
        record["attempts"].append({"attempt": attempt, "raw_output": out.text, "schema_valid": answer is not None,
                                   "schema_error": schema_error, "model": out.model, "usage": out.usage,
                                   "finish_reason": out.finish_reason, "request_id": out.request_id,
                                   "latency_ms": round(1000 * (time.perf_counter() - t0), 1),
                                   "estimated_cost_usd": cost})
        if answer is not None:
            break
    if answer is None:
        record.update(status="rejected_schema")
        return record
    record["answer"] = answer.model_dump(mode="json")
    record["validation"] = validate_output(corpus, answer, ids, question.filters)
    if not record["validation"]["valid"]:
        record["status"] = "rejected_citation"
    else:
        record["status"] = "model_abstention" if answer.insufficient_evidence else "answered"
    return record


# ---------- protocol, batch and cost ----------

def _sha_file(path):
    from rag_eval import sha256_file
    return sha256_file(path)


def protocol_body(docs_check):
    from rag_eval import sha256_file
    closed = os.path.join(EXP004, "CLOSED.json")
    retriever = os.path.join(EXP004, "frozen", "retriever_v1.json")
    return {
        "version": PROTOCOL_VERSION, "decided_by": "the owner, directive 030",
        "provider": dict(PROVIDER_SETTINGS), "documentation_check": docs_check,
        "retry_policy": "one initial generation; one retry only if the output does not parse into schema v1, with the "
                        "parser error shown. No retry for wrong, weak, incomplete or abstaining answers. Transport "
                        "retries (at most 2) re-send a request only when no response was received.",
        "prompt": {"path": "protocol/prompt_v1.txt", "sha256": sha256_file(PROMPT_PATH)},
        "schema": {"version": SCHEMA_VERSION, "sha256": hashlib.sha256(schema_json().encode()).hexdigest(),
                   "max_claims": 4, "claim_citations": "1 to 5", "summary": "cited, reviewed like a claim",
                   "limitations": "0 to 3, at most 300 characters, reviewed for uncited facts",
                   "urls": "never produced by the model; resolved from the store"},
        "context_serializer": {"version": SERIALIZER_VERSION, "max_items": MAX_ITEMS,
                               "order": "frozen EXP-004 hybrid ranking", "fields": ["item_id", "outlet", "sector_group",
                               "published_at", "first_seen_at (replay mode only)", "language", "headline", "excerpt",
                               "url"], "truncation": f"headline first {MAX_HEADLINE} characters, excerpt first "
                               f"{MAX_EXCERPT} characters", "max_total_chars": MAX_CONTEXT_CHARS},
        "retriever": {"source": "EXP-004 frozen hybrid", "retriever_v1_sha256": sha256_file(retriever),
                      "exp004_closed_sha256": sha256_file(closed), "call": {"method": "hybrid", "lexical": "auto",
                                                                            "k": MAX_ITEMS}},
        "pre_generation_validation": ["every context item exists", "every context item passes the question's filters",
                                      "publication mode: published_at <= cutoff", "replay mode: also first_seen_at <= "
                                      "cutoff", "frozen retriever code and index unchanged",
                                      "empty context: deterministic system abstention, no provider call"],
        "post_generation_validation": ["schema v1", "citation membership in the supplied context", "corpus membership",
                                       "temporal validity", "filter validity", "every claim and the summary cite",
                                       "provenance: every citation resolves to its stored URL"],
        "human_rubric": {
            "claim_support": {"applies_to": "the summary and each claim of answers that passed validation",
                              "values": ["SUPPORTED", "UNSUPPORTED", "UNSURE"]},
            "answer_completeness": {"applies_to": "answered questions", "values": ["COMPLETE", "PARTIAL",
                                                                                   "INSUFFICIENT", "UNSURE"]},
            "context_sufficiency": {"applies_to": "answered questions", "question": "Does the supplied context hold "
                                    "enough evidence to answer?", "values": ["YES", "NO", "UNSURE"]},
            "abstention": {"applies_to": "model abstentions", "values": ["CORRECT", "INCORRECT", "UNSURE"]},
            "limitations": {"applies_to": "answers with limitations", "question": "Do the limitations add an uncited "
                            "factual claim?", "values": ["NO", "YES", "UNSURE"]},
            "unsure": "never counted as unsupported or incorrect; reported separately"},
        "metrics": {
            "claim_support_precision": "SUPPORTED / (SUPPORTED + UNSUPPORTED) over reviewed claims and summaries; "
                                       "UNSURE reported separately",
            "grounded_answer_rate": "over evaluable model outputs (answered, model abstention, rejected). An output is "
                                    "evaluable unless its context_sufficiency or abstention judgment is UNSURE or "
                                    "missing. Grounded when: deterministic validation passed; no claim or summary is "
                                    "UNSUPPORTED; and it is not an INCORRECT abstention and not an answer judged "
                                    "INSUFFICIENT while context_sufficiency is YES. Rejected outputs count as not "
                                    "grounded. System abstentions are reported separately",
            "abstention": "correct = model abstention judged CORRECT; incorrect = judged INCORRECT; missed = answered "
                          "while context_sufficiency is NO. precision = correct / (correct + incorrect); recall = "
                          "correct / (correct + missed)",
            "deterministic": ["schema-valid rate (final outputs)", "citation-membership-valid rate",
                              "temporal-violation count", "filter-violation count", "nonexistent-citation count",
                              "provenance-resolution rate"],
            "targets": {"citation_membership": 1.0, "nonexistent_citations": 0, "temporal_violations": 0,
                        "filter_violations": 0},
            "secondary": ["claims per answer", "citations per claim", "insufficient-evidence rate", "latency",
                          "tokens", "estimated cost", "completeness distribution", "human unsure rate"]},
        "failure_taxonomy": {
            "RETRIEVAL_MISS": "required evidence never entered the context (from EXP-004 DEV gold where available)",
            "GENERATION_OMISSION": "evidence in the context was not used (completeness PARTIAL or INSUFFICIENT)",
            "UNSUPPORTED_CLAIM": "a claim judged UNSUPPORTED", "CITATION_MISMATCH": "an allowed item cited for "
            "another claim or topic (human note)", "FABRICATED_CITATION": "an item not in the context (validator)",
            "TEMPORAL_VIOLATION": "evidence outside the time boundary (validator)",
            "FILTER_VIOLATION": "evidence outside the filters (validator)",
            "OVERSTATEMENT": "evidence supports a weaker statement (human note)",
            "CAUSAL_OVERREACH": "association presented as causation (human note)",
            "INCORRECT_ABSTENTION": "abstention judged INCORRECT", "MISSED_ABSTENTION": "answered while context "
            "sufficiency is NO", "CONTRADICTION_HANDLING_FAILURE": "conflicting evidence collapsed (human note)",
            "SCHEMA_FAILURE": "output rejected by schema v1 after the retry",
            "extension_rule": "new categories only as explicitly post-hoc extensions"},
        "development_set": "EXP-004 DEV questions (37). EXP-004 TEST questions are never used: they were inspected "
                           "descriptively and are not a pristine generation test. A fresh generation holdout is "
                           "authored, owner-reviewed and frozen before final evaluation.",
        "code_sha256": {f: sha256_file(os.path.join(SRC, f)) for f in CODE_FILES},
    }


def select_batch():
    """The first live batch, chosen by fixed rules before any output exists."""
    import rag_questions as rq
    from rag_eval import load_gold, load_split
    from rag_corpus import eligible_ids, open_corpus
    from rag_index import Index
    questions, qm = rq.load_frozen()
    split = load_split(qm["questions_sha256"])
    gold, _ = load_gold()
    dev = sorted((q for q in questions if q.question_id in set(split["dev"])), key=lambda q: q.question_id)
    rel = {q.question_id: {i for i, v in gold.get(q.question_id, {}).items() if v == "relevant"} for q in dev}
    rows = [json.loads(line) for line in open(os.path.join(EXP004, "results", "dev-retrieval-v1.per_question.jsonl"),
                                              encoding="utf-8")]
    top10 = {r["question_id"]: r["ranking"] for r in rows if r["candidate"] == "hybrid"}
    corpus, index = open_corpus(), Index(os.path.join(ROOT, "data", "index", "exp004-v1"))
    filtered = lambda q: bool(q.filters.sectors or q.filters.coarse_groups or q.filters.outlets)
    has_filters = lambda q: bool(q.filters.model_dump(exclude_none=True, exclude_defaults=True))
    picks, rules = [], {}

    def take(name, rule, candidates):
        chosen = next((q for q in candidates if q.question_id not in picks), None)
        rules[name] = {"rule": rule, "question_id": chosen.question_id if chosen else None}
        if chosen:
            picks.append(chosen.question_id)

    take("term", "lowest ID: query_type term, no filters, at least one relevant item",
         [q for q in dev if q.query_type == "term" and not has_filters(q) and rel[q.question_id]])
    take("temporal", "lowest ID: query_type temporal, at least one relevant item",
         [q for q in dev if q.query_type == "temporal" and rel[q.question_id]])
    take("filtered", "lowest ID: query_type source_filter or sector_filter, at least one relevant item",
         [q for q in dev if q.query_type in ("source_filter", "sector_filter") and rel[q.question_id]])
    take("several_evidence", "most relevant items in the frozen hybrid DEV top 10 (ties: lowest ID)",
         sorted((q for q in dev if rel[q.question_id]),
                key=lambda q: (-len(rel[q.question_id] & set(top10.get(q.question_id, []))), q.question_id)))
    take("abstention", "lowest ID: drafted unanswerable, no relevant item, at least one eligible item (non-empty "
                       "context, so the model itself must decide)",
         [q for q in dev if not q.answerable_expected and not rel[q.question_id]
          and set(eligible_ids(corpus, q.filters)) & set(index.row)])
    return {"batch": "dev-batch-1", "selected_before_any_output": True, "rules": rules, "question_ids": picks}


def max_cost(batch, prompt_text):
    """Upper bound in USD: every input character counted as a token, two attempts per
    question at the full output limit, all at peak prices."""
    import rag_questions as rq
    from rag_corpus import get_items, open_corpus
    from rag_eval import run_method
    from rag_index import Index
    from llm_deepseek import PRICING
    questions = {q.question_id: q for q in rq.load_frozen()[0]}
    corpus, index = open_corpus(), Index(os.path.join(ROOT, "data", "index", "exp004-v1"))
    price = PRICING[PROVIDER_SETTINGS["model"]]
    total, per_q = 0.0, {}
    for qid in batch["question_ids"]:
        q = questions[qid]
        ids, _ = run_method(corpus, index, q, "hybrid", "auto", MAX_ITEMS)
        ev = {e.item_id: e for e in get_items(corpus, ids)}
        context = serialize_context([ev[i] for i in ids], q.filters) if ids else []
        chars = sum(len(m["content"]) for m in build_messages(q, context, prompt_text, "x" * 600))
        cost = MAX_ATTEMPTS * (chars * price["input_cache_miss"][1] + PROVIDER_SETTINGS["max_tokens"]
                               * price["output"][1]) / 1_000_000
        per_q[qid] = {"context_items": len(ids), "input_chars_upper_bound": chars, "max_cost_usd": round(cost, 6)}
        total += cost
    return {"max_total_usd": round(total, 6), "gate_usd": 5.0, "per_question": per_q,
            "assumptions": "1 token per input character, 2 attempts, full max_tokens output, peak prices"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-protocol", "select-batch", "estimate-cost", "run-batch"])
    ap.add_argument("--docs-check")
    args = ap.parse_args(argv)
    with open(PROMPT_PATH, encoding="utf-8") as f:
        prompt_text = f.read()
    if args.cmd == "freeze-protocol":
        with open(args.docs_check, encoding="utf-8") as f:
            docs = json.load(f)
        os.makedirs(os.path.dirname(PROTOCOL_PATH), exist_ok=True)
        with open(PROTOCOL_PATH, "x", encoding="utf-8", newline="\n") as f:
            json.dump(dict(protocol_body(docs), frozen_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
                      f, indent=1)
        print(json.dumps({"protocol": PROTOCOL_PATH, "sha256": _sha_file(PROTOCOL_PATH)}, indent=1))
        return 0
    if args.cmd == "select-batch":
        os.makedirs(BATCH_DIR, exist_ok=True)
        body = dict(select_batch(), selected_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        with open(BATCH_PATH, "x", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1)
        print(json.dumps(body, indent=1))
        return 0
    with open(BATCH_PATH, encoding="utf-8") as f:
        batch = json.load(f)
    if args.cmd == "estimate-cost":
        print(json.dumps(max_cost(batch, prompt_text), indent=1))
        return 0
    try:
        body = run_batch(batch, prompt_text)
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1))
    return 0


def run_batch(batch, prompt_text, provider=None):
    """The first live batch, once. Checks every frozen boundary before the first call."""
    import rag_questions as rq
    import rag_select as rs
    from rag_corpus import open_corpus
    from rag_index import Index
    import llm_deepseek

    if os.path.exists(OUTPUTS_PATH) or os.path.exists(SUMMARY_PATH):
        raise RuntimeError("this batch has already run. It runs once.")
    for path in (PROTOCOL_PATH, BATCH_PATH, PROMPT_PATH):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    with open(PROTOCOL_PATH, encoding="utf-8") as f:
        protocol = json.load(f)
    if protocol["prompt"]["sha256"] != _sha_file(PROMPT_PATH):
        raise RuntimeError("prompt v1 changed after the protocol was frozen")
    if protocol["schema"]["sha256"] != hashlib.sha256(schema_json().encode()).hexdigest():
        raise RuntimeError("schema v1 changed after the protocol was frozen")
    if protocol["code_sha256"] != {f: _sha_file(os.path.join(SRC, f)) for f in CODE_FILES}:
        raise RuntimeError("EXP-005 code changed after the protocol was frozen")
    with open(rs.RETRIEVER_PATH, encoding="utf-8") as f:
        frozen = json.load(f)
    code, index_files = rs.code_and_index_fingerprints()
    if code != frozen["code_sha256"] or index_files != frozen["index_files_sha256"] or \
            rs.current_fingerprints() != frozen["fingerprints"]:
        raise RuntimeError("the frozen EXP-004 retriever or its inputs changed")
    cost = max_cost(batch, prompt_text)
    if cost["max_total_usd"] > cost["gate_usd"]:
        raise RuntimeError(f"estimated maximum cost {cost['max_total_usd']} exceeds the gate")
    if provider is None:
        p = PROVIDER_SETTINGS
        provider = llm_deepseek.DeepSeekProvider(model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
                                                 max_tokens=p["max_tokens"], timeout=p["timeout_s"],
                                                 max_retries=p["transport_retries"], thinking=p["thinking"],
                                                 allow_live=True)
    questions = {q.question_id: q for q in rq.load_frozen()[0]}
    corpus, index = open_corpus(), Index(os.path.join(ROOT, "data", "index", "exp004-v1"))
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    os.makedirs(BATCH_DIR, exist_ok=True)
    with open(OUTPUTS_PATH, "x", encoding="utf-8", newline="\n") as out:
        for qid in batch["question_ids"]:
            r = answer_question(questions[qid], provider, corpus, index, prompt_text, llm_deepseek.estimate_cost)
            r.update(run="dev-batch-1", protocol_sha256=_sha_file(PROTOCOL_PATH))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            records.append(r)
    body = {"run": "dev-batch-1", "started_at": started, "protocol_sha256": _sha_file(PROTOCOL_PATH),
            "provider": provider.config(), "max_cost_estimate": cost, **deterministic_summary(records),
            "outputs_sha256": _sha_file(OUTPUTS_PATH)}
    with open(SUMMARY_PATH, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def deterministic_summary(records):
    calls = [a for r in records for a in r["attempts"]]
    final = [r for r in records if r["attempts"]]
    validated = [r for r in records if "validation" in r]
    citations = sum(r["validation"]["citations"] for r in validated)
    usage = {}
    for a in calls:
        for k, v in (a.get("usage") or {}).items():
            if isinstance(v, (int, float)):
                usage[k] = usage.get(k, 0) + v
    lat = [a["latency_ms"] for a in calls]
    answered = [r for r in records if r["status"] == "answered"]
    return {
        "questions": len(records), "status_counts": {s: sum(r["status"] == s for r in records) for s in
                                                     sorted({r["status"] for r in records})},
        "provider_calls": len(calls), "schema_retries": sum(1 for r in records if len(r["attempts"]) > 1),
        "schema_valid_rate": round(sum(r["status"] != "rejected_schema" for r in final) / len(final), 4) if final else None,
        "citation_membership_valid_rate": round(sum(r["validation"]["membership_valid"] for r in validated)
                                                / len(validated), 4) if validated else None,
        "temporal_violations": sum(r["validation"]["temporal_violations"] for r in validated),
        "filter_violations": sum(r["validation"]["filter_violations"] for r in validated),
        "nonexistent_citations": sum(r["validation"]["nonexistent_citations"] for r in validated),
        "provenance_resolution_rate": round(sum(r["validation"]["provenance_resolved"] for r in validated)
                                            / max(1, sum(r["validation"]["provenance_total"] for r in validated)), 4)
        if validated else None,
        "claims_per_answer": round(statistics.mean(len(r["answer"]["claims"]) for r in answered), 2) if answered else None,
        "citations": citations, "tokens": usage,
        "latency_ms": {"median": statistics.median(lat), "max": max(lat)} if lat else None,
        "estimated_cost_usd": round(sum(a["estimated_cost_usd"] or 0 for a in calls), 6),
    }


if __name__ == "__main__":
    sys.exit(main())
