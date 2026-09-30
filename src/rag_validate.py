"""Deterministic validation for EXP-004 generation. No language model checks anything
that code can check exactly.

validate_context runs before a provider is called. Every item offered to the model must
exist and satisfy every filter of the query, including the temporal mode, so no future
evidence can reach the model.

validate_answer runs on the model's output. It must parse into rag_schema.GroundedAnswer,
and every item a claim cites must
  1. be one of the context items given to the model (membership),
  2. exist in the evidence store (corpus),
  3. satisfy every filter of the query (filters),
  4. satisfy the temporal constraint: published_at <= as_of, and in replay mode also
     first_seen_at <= as_of (temporal), and
  5. resolve to a URL and a publication time (provenance).
Any failure rejects the whole answer. Invalid citations are reported, never repaired.
"""

from pydantic import ValidationError

from rag_corpus import get_items, satisfies
from rag_schema import Filters, GroundedAnswer, upper_bound


def parse_answer(raw):
    """(GroundedAnswer or None, error message). Malformed output is rejected, not coerced."""
    try:
        if isinstance(raw, (str, bytes)):
            return GroundedAnswer.model_validate_json(raw), None
        return GroundedAnswer.model_validate(raw), None
    except ValidationError as e:
        return None, "; ".join(f"{'.'.join(map(str, err['loc'])) or 'answer'}: {err['msg']}" for err in e.errors())


def temporal_violation(evidence, filters: Filters):
    """The reason an item breaks the temporal constraint, or None."""
    if not filters.as_of:
        return None
    as_of = upper_bound(filters.as_of)
    if evidence.published_at > as_of:
        return "published_after_as_of"
    if filters.temporal_mode == "replay" and evidence.first_seen_at > as_of:
        return "first_seen_after_as_of"
    return None


def check_items(con, item_ids, filters: Filters):
    """{item_id: reason} for every item that is missing, fails a filter, breaks the
    temporal constraint or lacks provenance. Valid items are absent."""
    ids = list(dict.fromkeys(int(i) for i in item_ids))
    found = {e.item_id: e for e in get_items(con, ids)}
    passing = satisfies(con, ids, filters)
    problems = {}
    for i in ids:
        e = found.get(i)
        if e is None:
            problems[i] = "nonexistent"
        elif temporal_violation(e, filters):
            problems[i] = temporal_violation(e, filters)
        elif i not in passing:
            problems[i] = "fails_filters"
        elif not (e.url and e.published_at):
            problems[i] = "missing_provenance"
    return problems


def validate_context(con, context_ids, filters: Filters):
    """Violations among the items about to be shown to a model. Must be empty."""
    return [{"item_id": i, "reason": r} for i, r in check_items(con, context_ids, filters).items()]


def validate_answer(con, raw, context_ids, filters: Filters):
    """Return a report dict. The answer is valid only if it parses and every citation
    passes every check."""
    answer, error = parse_answer(raw)
    if answer is None:
        return {"valid": False, "schema_valid": False, "schema_error": error, "violations": [], "citations": 0,
                "valid_citations": 0, "temporal_leaks": [], "insufficient_evidence": None}
    context = set(context_ids)
    cited = [i for c in answer.claims for i in c.supporting_item_ids]
    problems = check_items(con, cited, filters)
    violations = []
    for n, claim in enumerate(answer.claims):
        for item_id in claim.supporting_item_ids:
            reason = problems.get(item_id)
            if reason != "nonexistent" and item_id not in context:
                reason = "not_in_context"
            if reason:
                violations.append({"claim": n, "item_id": item_id, "reason": reason})
    leaks = sorted({i for i, r in problems.items() if r in ("published_after_as_of", "first_seen_after_as_of")})
    return {"valid": not violations, "schema_valid": True, "schema_error": None, "violations": violations,
            "citations": len(cited), "valid_citations": len(cited) - len(violations),
            "insufficient_evidence": answer.insufficient_evidence, "temporal_leaks": leaks,
            "answer": answer.model_dump(mode="json")}
