"""EXP-004 question review and freezing.

The 60 questions in questions_v1.jsonl are machine drafts. The editor reviews each one in
ARI3 Review without seeing any retrieval result, and every decision is appended to
reviews/question_reviews_v1.jsonl (tracked). The latest decision per question counts.

Decisions: approve, edit (new question text, query, filters or answerable flag),
reject, ambiguous (blocks the freeze until resolved) and duplicate (excluded).

`freeze` materializes the approved set once: every draft needs a decision, none may be
ambiguous, every review must name the draft file's current fingerprint, and the frozen
files are never regenerated. Question IDs never change, so rejected IDs leave gaps.

usage:
  python src/rag_questions.py status
  python src/rag_questions.py freeze
"""

import argparse
import collections
import json
import os
import sys
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from item_store import ROOT, utc_now
from rag_eval import Question, load_jsonl, sha256_file, stratum
from rag_schema import Filters

EXP = os.path.join(ROOT, "experiments", "exp-004-grounded-retrieval")
DRAFTS = os.path.join(EXP, "questions_v1.jsonl")
REVIEWS = os.path.join(EXP, "reviews", "question_reviews_v1.jsonl")
FROZEN = os.path.join(EXP, "frozen", "questions_v1_frozen.jsonl")
FREEZE_MANIFEST = os.path.join(EXP, "frozen", "questions_v1_freeze.json")
ACTIONS = ("approve", "edit", "reject", "ambiguous", "duplicate")


class QuestionEdits(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    question: Optional[str] = Field(default=None, min_length=3, max_length=500)
    query: Optional[str] = Field(default=None, min_length=1, max_length=500)
    answerable_expected: Optional[bool] = None
    filters: Optional[Filters] = None


class QuestionReview(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    question_id: str = Field(pattern=r"^q\d{3}$")
    action: str = Field(pattern="^(" + "|".join(ACTIONS) + ")$")
    reviewer: str
    reviewed_at: str
    drafts_sha256: str = Field(min_length=64, max_length=64)
    edits: Optional[QuestionEdits] = None
    duplicate_of: Optional[str] = Field(default=None, pattern=r"^q\d{3}$")
    note: str = ""


def _paths(**given):
    """Resolve file paths at call time, so tests and tools can point the module elsewhere."""
    defaults = {"drafts": DRAFTS, "reviews": REVIEWS, "frozen": FROZEN, "manifest": FREEZE_MANIFEST}
    return [given[k] if given[k] is not None else defaults[k] for k in given]


def record_review(question_id, action, reviewer="ariella", edits=None, duplicate_of=None, note="",
                  drafts=None, reviews=None):
    """Validate and append one review decision. Returns it."""
    drafts, reviews = _paths(drafts=drafts, reviews=reviews)
    if action == "edit" and not edits:
        raise ValueError("an edit needs at least one changed field")
    if action != "edit" and edits:
        raise ValueError("only an edit carries changed fields")
    if action == "duplicate" and not duplicate_of:
        raise ValueError("a duplicate names the question it duplicates")
    ids = {q.question_id for q in load_jsonl(drafts, Question)}
    if question_id not in ids or (duplicate_of and duplicate_of not in ids):
        raise ValueError("unknown question_id")
    review = QuestionReview(question_id=question_id, action=action, reviewer=reviewer, reviewed_at=utc_now(),
                            drafts_sha256=sha256_file(drafts),
                            edits=QuestionEdits.model_validate_json(json.dumps(edits)) if edits else None,
                            duplicate_of=duplicate_of, note=note)
    os.makedirs(os.path.dirname(reviews), exist_ok=True)
    with open(reviews, "a", encoding="utf-8", newline="\n") as f:
        f.write(review.model_dump_json(exclude_none=True) + "\n")
    return review


def latest_reviews(reviews=None):
    (reviews,) = _paths(reviews=reviews)
    if not os.path.exists(reviews):
        return {}
    latest = {}
    for r in sorted(load_jsonl(reviews, QuestionReview), key=lambda r: r.reviewed_at):
        latest[r.question_id] = r
    return latest


def review_status(drafts=None, reviews=None):
    drafts, reviews = _paths(drafts=drafts, reviews=reviews)
    questions = load_jsonl(drafts, Question)
    latest = latest_reviews(reviews)
    counts = collections.Counter(latest[q.question_id].action if q.question_id in latest else "unreviewed"
                                 for q in questions)
    stale = sorted(q for q, r in latest.items() if r.drafts_sha256 != sha256_file(drafts))
    return {"questions": len(questions), "decisions": dict(counts), "stale_reviews": stale,
            "ready_to_freeze": counts.get("unreviewed", 0) == 0 and counts.get("ambiguous", 0) == 0 and not stale}


def materialize(drafts=None, reviews=None):
    """The approved question set, with edits applied. Raises if review is incomplete."""
    drafts, reviews = _paths(drafts=drafts, reviews=reviews)
    status = review_status(drafts, reviews)
    if status["stale_reviews"]:
        raise RuntimeError(f"reviews name an older draft file: {status['stale_reviews']}")
    if not status["ready_to_freeze"]:
        raise RuntimeError(f"review is incomplete: {status['decisions']}")
    latest = latest_reviews(reviews)
    out = []
    for q in load_jsonl(drafts, Question):
        r = latest[q.question_id]
        if r.action in ("reject", "duplicate"):
            continue
        data = q.model_dump(mode="json")
        if r.action == "edit":
            changes = r.edits.model_dump(mode="json", exclude_none=True)
            data.update(changes)
            data["notes"] = (data["notes"] + " " if data["notes"] else "") + f"edited by the editor: {sorted(changes)}"
        data["review_status"] = "edited" if r.action == "edit" else "approved"
        out.append(Question.model_validate_json(json.dumps(data)))
    return out


def summary(questions):
    return {"total": len(questions),
            "answerable_expected": sum(q.answerable_expected for q in questions),
            "unanswerable_expected": sum(not q.answerable_expected for q in questions),
            "languages": dict(sorted(collections.Counter(q.language for q in questions).items())),
            "temporal": sum(stratum(q)[1] for q in questions),
            "replay": sum(q.filters.temporal_mode == "replay" for q in questions),
            "query_types": dict(sorted(collections.Counter(q.query_type for q in questions).items()))}


def freeze(drafts=None, reviews=None, frozen=None, manifest=None):
    drafts, reviews, frozen, manifest = _paths(drafts=drafts, reviews=reviews, frozen=frozen, manifest=manifest)
    if os.path.exists(frozen) or os.path.exists(manifest):
        raise RuntimeError("the question set is already frozen. A change needs a new version.")
    questions = materialize(drafts, reviews)
    os.makedirs(os.path.dirname(frozen), exist_ok=True)
    with open(frozen, "w", encoding="utf-8", newline="\n") as f:
        for q in questions:
            f.write(json.dumps(q.model_dump(mode="json", exclude_none=True), ensure_ascii=False) + "\n")
    body = {"frozen_at": utc_now(), "dataset_version": questions[0].dataset_version,
            "questions_sha256": sha256_file(frozen), "drafts_sha256": sha256_file(drafts),
            "reviews_sha256": sha256_file(reviews), "review_decisions": review_status(drafts, reviews)["decisions"],
            "question_ids": [q.question_id for q in questions], **summary(questions)}
    with open(manifest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
    return body


def load_frozen(frozen=None, manifest=None):
    """The frozen questions, after checking the file still matches its manifest."""
    frozen, manifest = _paths(frozen=frozen, manifest=manifest)
    with open(manifest, encoding="utf-8") as f:
        body = json.load(f)
    if sha256_file(frozen) != body["questions_sha256"]:
        raise RuntimeError("the frozen question file no longer matches its fingerprint")
    return load_jsonl(frozen, Question), body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["status", "freeze"])
    args = ap.parse_args(argv)
    if args.cmd == "status":
        print(json.dumps(review_status(), indent=1))
        return 0
    try:
        print(json.dumps(freeze(), indent=1, ensure_ascii=False))
    except RuntimeError as e:
        print(f"not frozen: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
