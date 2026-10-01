"""EXP-005 Prompt v2: schema v2, protocol v2, the dev-batch-2 run (one q013 regression probe
plus five fresh DEV questions).

Unchanged from v1 and reused from exp005.py: the frozen hybrid retriever and its call,
context serializer v1, the message builder, provider settings, the retry policy and the
pre-generation context check. Prompt v1 and every v1 artifact stay as they are.

Changes (each tied to a Prompt-v1 failure on q013):
  - no model-written summary: the answer is the list of validated claims, rendered by code
    (v1: the summary added "hair", which its citations did not support)
  - coverage instructions and up to 10 citations per claim, still at most 4 claims
    (v1: PARTIAL answer, 5 relevant context items left out)
  - limitations carry supporting_item_ids; any item-specific limitation must cite and is
    reviewed like a claim (v1: a limitation stated an uncited fact about item 1363)

usage:
  python src/exp005_v2.py freeze-protocol
  python src/exp005_v2.py select-batch
  python src/exp005_v2.py estimate-cost
  python src/exp005_v2.py run-batch          # needs the owner's explicit authorization and the live gate
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

import exp005 as v1

PROMPT_V2 = os.path.join(v1.EXP, "protocol", "prompt_v2.txt")
PROTOCOL_V2 = os.path.join(v1.EXP, "protocol", "protocol_v2.json")
BATCH2_DIR = os.path.join(v1.EXP, "runs", "dev-batch-2")
BATCH2 = os.path.join(BATCH2_DIR, "batch.json")
OUTPUTS2 = os.path.join(BATCH2_DIR, "outputs.jsonl")
SUMMARY2 = os.path.join(BATCH2_DIR, "summary.json")
PROBE_QUESTION = "q013"
V1_QUESTIONS = ("q003", "q013", "q015", "q016", "q029")
CODE_FILES_V2 = ("exp005_v2.py", "exp005.py", "llm_provider.py", "llm_deepseek.py", "rag_validate.py", "rag_corpus.py")

Strict = ConfigDict(extra="forbid", strict=True, frozen=True)


class ClaimV2(BaseModel):
    model_config = Strict
    text: str = Field(min_length=1, max_length=400)
    supporting_item_ids: List[int] = Field(min_length=1, max_length=10)


class LimitationV2(BaseModel):
    model_config = Strict
    text: str = Field(min_length=1, max_length=300)
    supporting_item_ids: List[int] = Field(default_factory=list, max_length=10)


class AnswerV2(BaseModel):
    model_config = Strict
    insufficient_evidence: bool
    claims: List[ClaimV2] = Field(default_factory=list, max_length=4)
    limitations: List[LimitationV2] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def _shape(self):
        if self.insufficient_evidence and self.claims:
            raise ValueError("an insufficient-evidence answer has no claims")
        if not self.insufficient_evidence and not self.claims:
            raise ValueError("an answer needs 1 to 4 claims")
        return self


def schema_json():
    return json.dumps(AnswerV2.model_json_schema(), sort_keys=True, separators=(",", ":"))


def parse(raw):
    try:
        return AnswerV2.model_validate_json(raw or ""), None
    except ValidationError as e:
        return None, "; ".join(f"{'.'.join(map(str, err['loc'])) or 'answer'}: {err['msg']}" for err in e.errors())[:600]


def render(answer):
    """The displayed answer, built by code from validated claims only."""
    return " ".join(c.text for c in answer.claims)


def validate_output(corpus, answer, context_ids, filters):
    """As v1, over claims and cited limitations. Every failed check is recorded."""
    from rag_corpus import get_items
    from rag_validate import check_items
    groups = [(f"claim {n}", c.supporting_item_ids) for n, c in enumerate(answer.claims)] + \
        [(f"limitation {n}", lim.supporting_item_ids) for n, lim in enumerate(answer.limitations)
         if lim.supporting_item_ids]
    cited = [i for _, ids in groups for i in ids]
    problems = check_items(corpus, cited, filters)
    context = set(context_ids)
    violations = []
    for where, ids in groups:
        for i in ids:
            if i not in context and problems.get(i) != "nonexistent":
                violations.append({"where": where, "item_id": i, "reason": "not_in_context"})
            if problems.get(i):
                violations.append({"where": where, "item_id": i, "reason": problems[i]})
    stored = {e.item_id: e for e in get_items(corpus, list(dict.fromkeys(cited)))}
    reasons = [v["reason"] for v in violations]
    return {"valid": not violations, "violations": violations, "citations": len(cited),
            "membership_valid": "not_in_context" not in reasons and "nonexistent" not in reasons,
            "temporal_violations": reasons.count("published_after_as_of") + reasons.count("first_seen_after_as_of"),
            "filter_violations": reasons.count("fails_filters"), "nonexistent_citations": reasons.count("nonexistent"),
            "provenance_resolved": sum(1 for i in set(cited) if i in stored and stored[i].url),
            "provenance_total": len(set(cited)), "citation_urls": {i: stored[i].url for i in set(cited) if i in stored}}


def answer_question(question, provider, corpus, index, prompt_text, cost_fn=None):
    """One question through the frozen pipeline with Prompt v2. Same flow and retry policy as v1."""
    from rag_corpus import get_items
    from rag_eval import run_method
    from rag_validate import check_items
    record = {"question_id": question.question_id, "question": question.question, "retrieval_query": question.query,
              "filters": question.filters.model_dump(mode="json", exclude_none=True), "attempts": []}
    ids, seconds = run_method(corpus, index, question, "hybrid", "auto", v1.MAX_ITEMS)
    record["retrieval"] = {"item_ids": ids, "latency_ms": round(1000 * seconds, 1)}
    bad = check_items(corpus, ids, question.filters)
    if bad:
        record.update(status="context_invalid", context_violations=bad)
        return record
    if not ids:
        record.update(status="system_abstention", note="no eligible evidence; the provider was not called")
        return record
    evidence = {e.item_id: e for e in get_items(corpus, ids)}
    context = v1.serialize_context([evidence[i] for i in ids], question.filters)
    record["context_sha256"] = hashlib.sha256(json.dumps(context, ensure_ascii=False).encode()).hexdigest()
    schema_error, answer = None, None
    for attempt in range(1, v1.MAX_ATTEMPTS + 1):
        t0 = time.perf_counter()
        try:
            out = provider.generate_json(v1.build_messages(question, context, prompt_text, schema_error))
        except Exception as e:
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
    record["rendered_answer"] = render(answer)
    record["validation"] = validate_output(corpus, answer, ids, question.filters)
    record["status"] = ("rejected_citation" if not record["validation"]["valid"] else
                        "model_abstention" if answer.insufficient_evidence else "answered")
    return record


# ---------- protocol v2, batch and run ----------

def protocol_v2_body():
    from rag_eval import sha256_file
    with open(v1.PROTOCOL_PATH, encoding="utf-8") as f:
        p1 = json.load(f)
    return {
        "version": "exp005-protocol-v2", "decided_by": "the owner, directive 032",
        "based_on": {"protocol_v1_sha256": sha256_file(v1.PROTOCOL_PATH), "prompt_v1_sha256": sha256_file(v1.PROMPT_PATH),
                     "v1_scores": "runs/dev-batch-1/prompt_v1_scores.json", "v1_failures": "runs/dev-batch-1/prompt_v1_evaluation.json"},
        "unchanged_from_v1": {"provider": p1["provider"], "retry_policy": p1["retry_policy"],
                              "context_serializer": p1["context_serializer"], "retriever": p1["retriever"],
                              "pre_generation_validation": p1["pre_generation_validation"]},
        "changes": [
            {"what": "no model-written summary; the displayed answer is the validated claims joined by code",
             "why": "v1 q013: the summary added 'hair', which its citations did not support (UNSUPPORTED_CLAIM)",
             "choice": "removal chosen over a 'summary may add nothing' rule, because no deterministic check can verify "
                       "that a free-text summary adds no fact"},
            {"what": "coverage instructions (read every item, represent each distinct relevant finding, group items "
                     "that support the same finding, cite nothing irrelevant); citations per claim raised from 5 to 10; "
                     "the cap of 4 claims is kept",
             "why": "v1 q013: PARTIAL, with 5 relevant context items left out (GENERATION_OMISSION); grouping needs more "
                    "citations per claim"},
            {"what": "limitations become {text, supporting_item_ids}; a limitation about a specific item must cite it and "
                     "is reviewed like a claim; a limitation about the evidence set as a whole cites nothing",
             "why": "v1 q013: a limitation stated an uncited fact about item 1363 (LIMITATION_UNCITED_FACT)"}],
        "prompt": {"path": "protocol/prompt_v2.txt", "sha256": sha256_file(PROMPT_V2)},
        "schema": {"version": "exp005-schema-v2", "sha256": hashlib.sha256(schema_json().encode()).hexdigest(),
                   "max_claims": 4, "claim_citations": "1 to 10", "summary": "none",
                   "limitations": "0 to 3, each {text <= 300 chars, supporting_item_ids 0 to 10}"},
        "post_generation_validation": "as v1, over claims and cited limitations",
        "human_rubric": {
            "version": "rubric-v2",
            "claim_support": "each claim, and each limitation that cites items: SUPPORTED / UNSUPPORTED / UNSURE",
            "limitation_uncited": "each limitation that cites nothing: does it state a fact about a specific item? "
                                  "NO / YES / UNSURE",
            "answer_completeness": "as v1", "context_sufficiency": "as v1", "abstention": "as v1",
            "reviewer_notes": "optional free-text note on any task (unsupported detail, citation mismatch, omission, "
                              "overstatement, causal overreach, other); qualitative only, never a metric input",
            "regression_probe": "q013 only, separate deck and log: for each v1 failure FIXED / RECURRED / CHANGED_FORM "
                                "/ UNSURE; descriptive, never part of fresh metrics"},
        "metrics": {
            "version": "metrics-v2",
            "claim_support_precision": "SUPPORTED / (SUPPORTED + UNSUPPORTED) over claims and cited limitations; "
                                       "UNSURE separate",
            "grounded_answer_rate": "as v1 (claims replace claims + summary); comparable with v1",
            "uncited_item_specific_limitations": "count of uncited limitations judged YES; reported separately, as in v1",
            "abstention": "as v1", "deterministic": "as v1",
            "scope": "fresh DEV questions only; the q013 probe is excluded"},
        "failure_taxonomy": {
            "version": "taxonomy-v2",
            "categories": "the 13 v1 categories, plus LIMITATION_UNCITED_FACT (a post-hoc extension in v1, now "
                          "pre-registered: an uncited limitation judged YES)",
            "notes": "CITATION_MISMATCH, OVERSTATEMENT, CAUSAL_OVERREACH and CONTRADICTION_HANDLING_FAILURE can now be "
                     "assigned from reviewer notes"},
        "provider_settings_check": v1.PROVIDER_SETTINGS,
        "code_sha256": {f: sha256_file(os.path.join(v1.SRC, f)) for f in CODE_FILES_V2},
    }


def select_batch():
    """Five fresh DEV questions by the v1 rules, excluding every question used in v1."""
    import rag_questions as rq
    from rag_corpus import eligible_ids, open_corpus
    from rag_eval import load_gold, load_split
    from rag_index import Index
    questions, qm = rq.load_frozen()
    split = load_split(qm["questions_sha256"])
    gold, _ = load_gold()
    dev = sorted((q for q in questions if q.question_id in set(split["dev"]) and q.question_id not in V1_QUESTIONS),
                 key=lambda q: q.question_id)
    rel = {q.question_id: {i for i, v in gold.get(q.question_id, {}).items() if v == "relevant"} for q in dev}
    rows = [json.loads(line) for line in open(os.path.join(v1.EXP004, "results", "dev-retrieval-v1.per_question.jsonl"),
                                              encoding="utf-8")]
    top10 = {r["question_id"]: r["ranking"] for r in rows if r["candidate"] == "hybrid"}
    corpus, index = open_corpus(), Index(os.path.join(v1.ROOT, "data", "index", "exp004-v1"))
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
    take("abstention", "lowest ID: drafted unanswerable, no relevant item, at least one eligible item",
         [q for q in dev if not q.answerable_expected and not rel[q.question_id]
          and set(eligible_ids(corpus, q.filters)) & set(index.row)])
    return {"batch": "dev-batch-2", "selected_before_any_output": True, "excluded": list(V1_QUESTIONS),
            "rules": rules, "fresh_question_ids": picks,
            "regression_probe": {"question_id": PROBE_QUESTION, "label": "POST-TUNING REGRESSION PROBE",
                                 "runs": 1, "in_fresh_metrics": False}}


def max_cost(batch, prompt_text):
    ids = [batch["regression_probe"]["question_id"]] + batch["fresh_question_ids"]
    return v1.max_cost({"question_ids": ids}, prompt_text)


def run_batch(batch, prompt_text, provider=None):
    import rag_questions as rq
    import rag_select as rs
    import llm_deepseek
    from rag_corpus import open_corpus
    from rag_index import Index
    from rag_eval import sha256_file
    if os.path.exists(OUTPUTS2) or os.path.exists(SUMMARY2):
        raise RuntimeError("dev-batch-2 has already run. It runs once.")
    for path in (PROTOCOL_V2, BATCH2, PROMPT_V2):
        ok, info = rs.rule_is_committed_and_pushed(path)
        if not ok:
            raise RuntimeError(f"{os.path.basename(path)}: {info}")
    with open(PROTOCOL_V2, encoding="utf-8") as f:
        protocol = json.load(f)
    if protocol["prompt"]["sha256"] != sha256_file(PROMPT_V2) or \
            protocol["schema"]["sha256"] != hashlib.sha256(schema_json().encode()).hexdigest() or \
            protocol["code_sha256"] != {f: sha256_file(os.path.join(v1.SRC, f)) for f in CODE_FILES_V2} or \
            protocol["provider_settings_check"] != v1.PROVIDER_SETTINGS:
        raise RuntimeError("prompt, schema, code or provider settings changed after protocol v2 was frozen")
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
        p = v1.PROVIDER_SETTINGS
        provider = llm_deepseek.DeepSeekProvider(model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
                                                 max_tokens=p["max_tokens"], timeout=p["timeout_s"],
                                                 max_retries=p["transport_retries"], thinking=p["thinking"],
                                                 allow_live=True)
    questions = {q.question_id: q for q in rq.load_frozen()[0]}
    corpus, index = open_corpus(), Index(os.path.join(v1.ROOT, "data", "index", "exp004-v1"))
    plan = [(batch["regression_probe"]["question_id"], "regression_probe")] + \
        [(q, "fresh") for q in batch["fresh_question_ids"]]
    records = []
    with open(OUTPUTS2, "x", encoding="utf-8", newline="\n") as out:
        for qid, role in plan:
            r = answer_question(questions[qid], provider, corpus, index, prompt_text, llm_deepseek.estimate_cost)
            r.update(run="dev-batch-2", role=role, protocol_sha256=sha256_file(PROTOCOL_V2))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            records.append(r)
    fresh = [r for r in records if r["role"] == "fresh"]
    body = {"run": "dev-batch-2", "protocol_sha256": sha256_file(PROTOCOL_V2), "provider": provider.config(),
            "max_cost_estimate": cost, "all_calls": v1.deterministic_summary(records),
            "fresh_only": v1.deterministic_summary(fresh), "outputs_sha256": sha256_file(OUTPUTS2)}
    with open(SUMMARY2, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1)
    return body


def main(argv=None):
    from rag_eval import sha256_file
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["freeze-protocol", "select-batch", "estimate-cost", "run-batch"])
    args = ap.parse_args(argv)
    with open(PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    try:
        if args.cmd == "freeze-protocol":
            with open(PROTOCOL_V2, "x", encoding="utf-8", newline="\n") as f:
                json.dump(dict(protocol_v2_body(), frozen_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
                          f, indent=1)
            print(json.dumps({"protocol_v2": sha256_file(PROTOCOL_V2)}, indent=1))
        elif args.cmd == "select-batch":
            os.makedirs(BATCH2_DIR, exist_ok=True)
            body = dict(select_batch(), selected_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            with open(BATCH2, "x", encoding="utf-8", newline="\n") as f:
                json.dump(body, f, indent=1)
            print(json.dumps(body, indent=1))
        else:
            with open(BATCH2, encoding="utf-8") as f:
                batch = json.load(f)
            body = max_cost(batch, prompt_text) if args.cmd == "estimate-cost" else run_batch(batch, prompt_text)
            print(json.dumps(body, indent=1))
    except (RuntimeError, FileExistsError) as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
