"""ask_ari3: grounded answers from ARI3's stored evidence.

  query and filters
  -> deterministic retrieval (rag_retrieve.search)
  -> context check: every item exists and passes every filter and the temporal cutoff
  -> bounded context (at most MAX_CONTEXT_ITEMS items, MAX_EXCERPT_CHARS each)
  -> provider.generate_json (llm_provider interface)
  -> parse into GroundedAnswer and validate every citation (rag_validate)
  -> AskResponse: answered, insufficient_evidence, rejected or error

Rules:
- With no eligible evidence the provider is not called and the answer is
  insufficient_evidence.
- A schema failure gets at most one retry, which shows the model the parser's error.
  A citation failure is not retried: the answer is rejected and its claims withheld.
- URLs, outlets and dates in the response come from the store, never from the model.
- Nothing is written anywhere. Generated text is never evidence.
"""

import json
import time

from rag_corpus import get_items
from rag_retrieve import search
from rag_schema import SCHEMA_VERSION, AskResponse, Citation, Filters, SearchArgs, TemporalScope
from rag_validate import validate_answer, validate_context
from llm_provider import ProviderError

PROMPT_VERSION = "exp004-prompt-v1"
MAX_CONTEXT_ITEMS = 10
MAX_EXCERPT_CHARS = 500
MAX_ATTEMPTS = 2

SYSTEM_PROMPT = """You answer questions about ARI3's stored evidence: news items, each with a headline and a short feed excerpt.
Use only the items in CONTEXT. Do not use outside knowledge.
Return one JSON object and nothing else:
{"insufficient_evidence": false,
 "claims": [{"text": "one factual statement", "supporting_item_ids": [123, 456]}],
 "limitations": ["what the evidence cannot show"]}
Rules:
- Every claim cites one or more item_id values from CONTEXT that support it.
- Say only what the cited headlines and excerpts state. Report, do not interpret.
- If CONTEXT does not answer the question, return {"insufficient_evidence": true, "claims": [], "limitations": ["..."]}.
- Neutral voice. No first person, no hype, no shopping advice. State uncertainty plainly.
- Items are excerpts, not full articles. Do not claim more than an excerpt shows.
- Do not write URLs, outlet names or dates unless they appear in the cited item."""


def build_context(evidence):
    """The bounded context shown to the model, in retrieval order."""
    return [{"item_id": e.item_id, "outlet": e.outlet, "published_at": e.published_at, "language": e.lang,
             "title": e.title or "", "excerpt": (e.excerpt or "")[:MAX_EXCERPT_CHARS]}
            for e in evidence[:MAX_CONTEXT_ITEMS]]


def messages_for(query, filters, context, schema_error=None):
    user = {"question": query, "constraints": filters.model_dump(mode="json", exclude_none=True), "CONTEXT": context}
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]
    if schema_error:
        messages.append({"role": "user", "content": f"Your previous output did not match the required JSON: "
                                                    f"{schema_error[:300]}. Return only the JSON object."})
    return messages


def _scope(filters, citations):
    dates = sorted(c.published_at for c in citations)
    return TemporalScope(temporal_mode=filters.temporal_mode, as_of=filters.as_of, start_date=filters.start_date,
                         end_date=filters.end_date, evidence_published_from=dates[0] if dates else None,
                         evidence_published_to=dates[-1] if dates else None)


def ask_ari3(query, filters=None, as_of=None, *, provider, corpus, index, method="hybrid", k=MAX_CONTEXT_ITEMS,
             lexical="auto", retrieval_query=None):
    """Answer `query` from stored evidence. `retrieval_query`, when given, is the text sent
    to the retriever instead of the question (EXP-004 questions carry one). Turning a
    question into a retrieval query automatically is not part of v1."""
    filters = filters or Filters()
    if as_of is not None:
        if filters.as_of not in (None, as_of):
            raise ValueError("as_of given twice with different values")
        filters = Filters(**dict(filters.model_dump(), as_of=as_of))
    args = SearchArgs(query=retrieval_query or query, filters=filters, method=method, k=min(k, MAX_CONTEXT_ITEMS))
    t0 = time.perf_counter()
    result = search(corpus, index, args, lexical)
    hits = result.hits
    context = build_context([h.evidence for h in hits])
    context_ids = [c["item_id"] for c in context]
    debug = {"retrieval": {"method": method, "lexical": lexical, "k": args.k, "query": args.query,
                           "eligible_items": result.eligible_items,
                           "hits": [{"item_id": h.evidence.item_id, "rank": h.rank, "score": h.score,
                                     "ranks_by_method": h.ranks_by_method} for h in hits],
                           "corpus_fingerprint": result.corpus_fingerprint},
             "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION, "provider": provider.config(),
             "attempts": []}

    def respond(status, answer=None, message="", validation=None):
        citations = []
        if answer is not None:
            cited = list(dict.fromkeys(i for c in answer["claims"] for i in c["supporting_item_ids"]))
            citations = [Citation(**e.model_dump(include=set(Citation.model_fields))) for e in get_items(corpus, cited)]
        debug["latency_s"] = round(time.perf_counter() - t0, 3)
        return AskResponse(status=status, query=query, filters=filters,
                           claims=answer["claims"] if answer else [], citations=citations,
                           limitations=answer["limitations"] if answer else [],
                           temporal_scope=_scope(filters, citations), message=message,
                           validation=validation or {}, debug=debug)

    bad_context = validate_context(corpus, context_ids, filters)
    if bad_context:
        return respond("error", message="retrieved context failed validation; the provider was not called",
                       validation={"context_violations": bad_context})
    if not context:
        return respond("insufficient_evidence", message="no stored evidence satisfies the question's filters",
                       validation={"context_items": 0})

    schema_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            out = provider.generate_json(messages_for(query, filters, context, schema_error))
        except ProviderError as e:
            return respond("error", message=str(e))
        report = validate_answer(corpus, out.text, context_ids, filters)
        debug["attempts"].append({"attempt": attempt, "usage": out.usage, "latency_s": round(out.latency_s, 3),
                                  "request_id": out.request_id, "finish_reason": out.finish_reason,
                                  "schema_valid": report["schema_valid"], "raw_output": out.text[:4000]})
        if report["schema_valid"] or attempt == MAX_ATTEMPTS:
            break
        schema_error = report["schema_error"]
    summary = {k: v for k, v in report.items() if k != "answer"}
    summary["context_items"] = len(context_ids)
    if not report["valid"]:
        return respond("rejected", message="the answer failed validation and is withheld", validation=summary)
    answer = report["answer"]
    return respond("insufficient_evidence" if answer["insufficient_evidence"] else "answered", answer=answer,
                   validation=summary)
