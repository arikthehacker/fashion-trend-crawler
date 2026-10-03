"""ask_ari3: the application entry point for grounded answers from ARI3's stored evidence.

It runs the Prompt v2 pipeline evaluated in EXP-005 (dev-batch-2 and SC-1 condition A) by
calling the frozen EXP-005 code itself, so the application and the evaluated path cannot
drift apart:

  question and filters
  -> verify_identity(): pinned fingerprints of protocol v2, Prompt v2, schema v2, the v2
     code, the provider settings and the frozen EXP-004 retriever and index. Any mismatch
     raises PipelineIdentityError before retrieval or any provider call (fail closed).
  -> exp005_v2.answer_question(), unchanged:
       frozen hybrid retrieval (top 10) -> context check -> serializer exp005-context-v1
       -> Prompt v2 -> AnswerV2 parse (one retry on a schema failure only)
       -> deterministic validation of claims and cited limitations
       -> render(): the claims joined by code, no model-written summary
  -> a structured result for a future service layer.

No live call happens by default. A live provider is used only when the caller passes
allow_live=True, and the DeepSeek adapter still refuses unless ARI3_LIVE_LLM=approved.
Nothing is written anywhere. Generated text is never evidence.

The historical EXP-004 orchestration lives in rag_answer_exp004.py and is not reachable
from here.
"""

import json
import os
from dataclasses import dataclass

import exp005 as v1
import exp005_v2 as v2
import rag_select as rs
from llm_provider import LiveCallNotAllowed
from rag_eval import sha256_file
from rag_schema import Filters

PIPELINE = "ari3-ask-prompt-v2"
# Pinned identity of the evaluated pipeline. Everything else is checked through these.
EXPECTED = {
    "protocol_v2_sha256": "87e88618c83167157c7ce0102c50b9a9ca173bf82309841b3f82e3d60d2c6739",
    "prompt_v2_sha256": "efea461f8e079eb8c25a3e8f5acb371d5e01b9bf18c617aec123b01f62a7afce",
    "schema_v2_sha256": "47b747c14b5301df9a790538205e8fdd1014019a136671e38e8d094f06c4a5ee",
    "retriever_v1_sha256": "3b55fcebbb08ec54b87198ab4a18e2f1b2bd0b922c6677428f525ceeadfd6b21",
}
FROZEN_INDEX_DIR = rs.INDEX_DIR


class PipelineIdentityError(RuntimeError):
    """The code, prompt, schema, settings or index differ from the evaluated pipeline."""


def _schema_sha():
    import hashlib
    return hashlib.sha256(v2.schema_json().encode()).hexdigest()


def _index_fingerprints():
    return rs.code_and_index_fingerprints()


def verify_identity():
    """Check every fingerprint of the evaluated pipeline. Returns the identity on success,
    raises PipelineIdentityError listing each mismatch otherwise."""
    problems = []
    if sha256_file(v2.PROTOCOL_V2) != EXPECTED["protocol_v2_sha256"]:
        problems.append("protocol_v2.json differs from the pinned fingerprint")
    with open(v2.PROTOCOL_V2, encoding="utf-8") as f:
        protocol = json.load(f)
    prompt_sha = sha256_file(v2.PROMPT_V2)
    if prompt_sha != EXPECTED["prompt_v2_sha256"] or prompt_sha != protocol["prompt"]["sha256"]:
        problems.append(f"Prompt v2 file differs (sha256 {prompt_sha[:12]})")
    schema_sha = _schema_sha()
    if schema_sha != EXPECTED["schema_v2_sha256"] or schema_sha != protocol["schema"]["sha256"]:
        problems.append(f"schema v2 differs (sha256 {schema_sha[:12]})")
    code = {f: sha256_file(os.path.join(v1.SRC, f)) for f in v2.CODE_FILES_V2}
    changed = sorted(f for f in code if code[f] != protocol["code_sha256"].get(f))
    if changed:
        problems.append(f"evaluated code changed: {changed}")
    if protocol["provider_settings_check"] != v1.PROVIDER_SETTINGS:
        problems.append("provider settings differ from protocol v2")
    if sha256_file(rs.RETRIEVER_PATH) != EXPECTED["retriever_v1_sha256"]:
        problems.append("retriever_v1.json differs from the pinned fingerprint")
    with open(rs.RETRIEVER_PATH, encoding="utf-8") as f:
        retriever = json.load(f)
    rcode, rindex = _index_fingerprints()
    if rcode != retriever["code_sha256"]:
        problems.append(f"retriever code changed: {sorted(k for k in rcode if rcode[k] != retriever['code_sha256'].get(k))}")
    if rindex != retriever["index_files_sha256"]:
        problems.append("the retrieval index differs from the frozen EXP-004 index")
    if retriever["configuration"]["call"] != {"method": "hybrid", "lexical": "auto", "k": v1.MAX_ITEMS}:
        problems.append("the frozen retriever call no longer matches the pipeline's retrieval call")
    if problems:
        raise PipelineIdentityError("ask_ari3 refuses to run: " + "; ".join(problems))
    return {"pipeline": PIPELINE, **EXPECTED, "protocol": protocol["version"], "schema": protocol["schema"]["version"],
            "serializer": v1.SERIALIZER_VERSION, "retriever": retriever["version"],
            "index_cutoff_first_seen_at": retriever["configuration"]["index"]["cutoff_first_seen_at"],
            "limits": {"context_items": v1.MAX_ITEMS, "headline_chars": v1.MAX_HEADLINE,
                       "excerpt_chars": v1.MAX_EXCERPT, "context_chars": v1.MAX_CONTEXT_CHARS,
                       "claims": protocol["schema"]["max_claims"], "attempts": v1.MAX_ATTEMPTS},
            "provider_settings": v1.PROVIDER_SETTINGS}


@dataclass(frozen=True)
class AppQuestion:
    """The fields exp005_v2.answer_question reads from a question."""
    question_id: str
    question: str
    query: str
    filters: Filters


def _live_provider():
    import llm_deepseek
    p = v1.PROVIDER_SETTINGS
    return llm_deepseek.DeepSeekProvider(model=p["model"], temperature=p["temperature"], top_p=p["top_p"],
                                         max_tokens=p["max_tokens"], timeout=p["timeout_s"],
                                         max_retries=p["transport_retries"], thinking=p["thinking"], allow_live=True)


def _citations(corpus, answer):
    from rag_corpus import get_items
    ids = [i for c in answer["claims"] for i in c["supporting_item_ids"]] + \
        [i for lim in answer["limitations"] for i in lim["supporting_item_ids"]]
    return [{"item_id": e.item_id, "url": e.url, "title": e.title, "outlet": e.outlet, "sector": e.sector,
             "published_at": e.published_at, "first_seen_at": e.first_seen_at, "first_seen_basis": e.first_seen_basis}
            for e in get_items(corpus, list(dict.fromkeys(ids)))]


def ask_ari3(question, filters=None, *, provider=None, allow_live=False, corpus=None, index=None,
             retrieval_query=None):
    """Answer `question` from stored evidence with the evaluated Prompt v2 pipeline.

    `filters` is a rag_schema.Filters or a dict of its fields. `retrieval_query`, when given,
    is sent to the retriever instead of the question. The EXP-005 runs used each frozen
    question's curated retrieval query. Without one, the question text itself is used.

    Raises PipelineIdentityError before anything else if the pipeline differs from the one
    evaluated, and LiveCallNotAllowed if a live provider would be used without allow_live."""
    identity = verify_identity()
    live = provider is None or getattr(provider, "name", "") != "scripted"
    if live and not allow_live:
        raise LiveCallNotAllowed("ask_ari3 makes no live call unless the caller passes allow_live=True "
                                 "(and the adapter also requires ARI3_LIVE_LLM=approved)")
    if provider is None:
        provider = _live_provider()
    if filters is None:
        filters = Filters()
    elif isinstance(filters, dict):
        filters = Filters(**filters)
    if corpus is None:
        from rag_corpus import open_corpus
        corpus = open_corpus()
    if index is None:
        from rag_index import Index
        index = Index(FROZEN_INDEX_DIR)
    cost_fn = None
    if live:
        import llm_deepseek
        cost_fn = llm_deepseek.estimate_cost
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    q = AppQuestion("ask", question, retrieval_query or question, filters)
    record = v2.answer_question(q, provider, corpus, index, prompt_text, cost_fn)
    status = record["status"]
    accepted = status in ("answered", "model_abstention")
    answer = record.get("answer") if accepted else None
    messages = {"system_abstention": "no stored evidence satisfies the question's filters; the provider was not called",
                "context_invalid": "retrieved context failed validation; the provider was not called",
                "rejected_schema": "the model's output did not match the answer schema after one retry",
                "rejected_citation": "the answer failed citation validation and is withheld",
                "provider_error": "the provider call failed"}
    return {
        "status": status,
        "abstained": status in ("model_abstention", "system_abstention"),
        "rendered_answer": record.get("rendered_answer", "") if status == "answered" else "",
        "answer": answer,
        "citations": _citations(corpus, answer) if answer else [],
        "validation": ({k: v for k, v in record["validation"].items() if k != "citation_urls"}
                       if "validation" in record else None),
        "message": messages.get(status, ""),
        "question": question, "retrieval_query": q.query, "filters": record["filters"],
        "retrieval": {"item_ids": record["retrieval"]["item_ids"],
                      "index_cutoff_first_seen_at": identity["index_cutoff_first_seen_at"],
                      "retriever": identity["retriever"]},
        "context_sha256": record.get("context_sha256"),
        "attempts": len(record["attempts"]), "schema_retries": max(0, len(record["attempts"]) - 1),
        "pipeline": identity,
        "audit": record,
    }
