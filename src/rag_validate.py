"""Citation validation for EXP-004 answers. Deterministic, no language model.

A cited item_id is valid only if it
  1. exists in the evidence store,
  2. was among the items retrieved for this query,
  3. satisfies every filter of the query, including the temporal mode, and
  4. still resolves to a URL and a publication time.
Any failure rejects the whole answer. Invalid citations are reported, never repaired.
"""

from pydantic import ValidationError

from rag_corpus import get_items, satisfies
from rag_schema import Answer, Filters, upper_bound


def parse_answer(raw):
    """(Answer or None, error message). Malformed output is rejected, not coerced."""
    try:
        return (Answer.model_validate_json(raw) if isinstance(raw, (str, bytes))
                else Answer.model_validate(raw)), None
    except ValidationError as e:
        return None, "; ".join(f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors())


def temporal_leaks(con, item_ids, filters: Filters):
    """Cited items that break the temporal mode: published after as_of, or, in replay
    mode, first seen by ARI3 after as_of."""
    if not filters.as_of:
        return []
    as_of = upper_bound(filters.as_of)
    leaks = []
    for e in get_items(con, item_ids):
        if e.published_at > as_of or (filters.temporal_mode == "replay" and e.first_seen_at > as_of):
            leaks.append(e.item_id)
    return leaks


def validate_answer(con, raw, retrieved_ids, filters: Filters):
    """Return a report dict: valid, schema_error, violations, citation counts and
    temporal leaks. The answer is valid only if every citation passes every check."""
    answer, error = parse_answer(raw)
    if answer is None:
        return {"valid": False, "schema_error": error, "violations": [], "citations": 0,
                "valid_citations": 0, "temporal_leaks": []}
    cited = [i for s in answer.answer_sentences for i in s.cited_item_ids]
    existing = {e.item_id: e for e in get_items(con, cited)}
    passing = satisfies(con, cited, filters)
    retrieved = set(retrieved_ids)
    violations = []
    for n, sentence in enumerate(answer.answer_sentences):
        for item_id in sentence.cited_item_ids:
            e = existing.get(item_id)
            reason = ("nonexistent" if e is None else
                      "not_retrieved" if item_id not in retrieved else
                      "fails_filters" if item_id not in passing else
                      "missing_provenance" if not (e.url and e.published_at) else None)
            if reason:
                violations.append({"sentence": n, "item_id": item_id, "reason": reason})
    return {"valid": not violations, "schema_error": None, "violations": violations,
            "citations": len(cited), "valid_citations": len(cited) - len(violations),
            "insufficient_evidence": answer.insufficient_evidence,
            "temporal_leaks": temporal_leaks(con, cited, filters)}
