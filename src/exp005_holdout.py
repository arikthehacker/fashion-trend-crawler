"""EXP-005 final generation holdout (C1): question records, deck checks, the duplicate
report, the store snapshot, retrieval-only evidence packets and the blind packet-sufficiency
deck. No provider is ever constructed in this module, and nothing is generated.

A holdout question carries no expected answer, no expected citations and no answerability
label. Its retrieval query is the question text itself, byte for byte (C1 policy: the
holdout evaluates what a user would get, with no query rewriting).

Packets are built with the same frozen calls exp005_v2.answer_question makes before its
provider step (hybrid retrieval, context check, serializer exp005-context-v1, Prompt v2
messages), against a frozen copy of the item store, so feed refreshes cannot change a
reviewed packet. Packet bodies stay local (data/store/, never committed). The manifest
holds item IDs and fingerprints only.

usage:
  python src/exp005_holdout.py check       # validate the frozen deck and print its coverage
  python src/exp005_holdout.py duplicates  # similarity report against every earlier question text
  python src/exp005_holdout.py snapshot    # copy the item store to the frozen C1 snapshot (once)
  python src/exp005_holdout.py packets     # retrieval only: packets, manifest and integrity checks (once)
  python src/exp005_holdout.py deck        # write the blind packet-sufficiency review queue
"""

import argparse
import collections
import difflib
import hashlib
import json
import os
import random
import re
import sqlite3
import sys
import unicodedata
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from item_store import ROOT
from rag_schema import Filters

HOLDOUT = os.path.join(ROOT, "experiments", "exp-005-grounded-generation", "holdout")
FROZEN = os.path.join(HOLDOUT, "questions_v1_frozen.jsonl")
PROTOCOL = os.path.join(HOLDOUT, "protocol_v1_frozen.json")
MANIFEST = os.path.join(HOLDOUT, "packets_v1_manifest.json")
REVIEWS = os.path.join(HOLDOUT, "reviews", "sufficiency_reviews_v1.jsonl")
LOCAL = os.path.join(ROOT, "data", "store", "exp005_holdout")  # ignored by git: snapshot and packet bodies
SNAPSHOT = os.path.join(LOCAL, "store_snapshot_c1.db")
PACKETS = os.path.join(LOCAL, "packets_v1.jsonl")
QUEUE_NAME = "exp005_holdout_sufficiency"
DECK_SEED = 20261003
CATEGORIES = ("direct", "synthesis", "temporal", "filtered", "stress")
TARGET = {"direct": 8, "synthesis": 7, "temporal": 5, "filtered": 5, "stress": 5}
N_QUESTIONS = 30
PRIOR_SOURCES = [os.path.join(ROOT, "experiments", "exp-004-grounded-retrieval", "questions_v1.jsonl"),
                 os.path.join(ROOT, "experiments", "exp-004-grounded-retrieval", "frozen", "questions_v1_frozen.jsonl")]


class HoldoutQuestion(BaseModel):
    """One holdout question. Unknown fields (an answer, citations, an answerability label)
    are rejected."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    question_id: str = Field(pattern=r"^h\d{3}$")
    question: str = Field(min_length=10, max_length=300)
    retrieval_query: str
    filters: Filters
    categories: List[Literal[CATEGORIES]] = Field(min_length=1)
    primary_category: Literal[CATEGORIES]
    probes: str = Field(min_length=10, max_length=400)

    @model_validator(mode="after")
    def _policy(self):
        if self.retrieval_query != self.question:
            raise ValueError("retrieval_query must be byte-identical to question (C1 retrieval-query policy)")
        if self.primary_category not in self.categories:
            raise ValueError("primary_category must be one of categories")
        return self


def load_deck(path=FROZEN):
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return [HoldoutQuestion(**{**r, "filters": Filters(**r.get("filters", {}))}) for r in rows]


def deck_errors(deck):
    errors = []
    ids = [q.question_id for q in deck]
    if len(deck) != N_QUESTIONS:
        errors.append(f"deck has {len(deck)} questions, not {N_QUESTIONS}")
    if len(set(ids)) != len(ids):
        errors.append("question IDs repeat")
    if len({normalize(q.question) for q in deck}) != len(deck):
        errors.append("two questions are identical after normalization")
    primary = collections.Counter(q.primary_category for q in deck)
    for cat, n in TARGET.items():
        if primary.get(cat, 0) != n:
            errors.append(f"{cat}: {primary.get(cat, 0)} primary questions, target {n}")
    return errors


def coverage(deck):
    filt = collections.Counter()
    for q in deck:
        f = q.filters.model_dump(exclude_none=True, exclude_defaults=True)
        for key in f:
            filt[key] += 1
    return {"primary": dict(collections.Counter(q.primary_category for q in deck)),
            "any_category": dict(collections.Counter(c for q in deck for c in q.categories)),
            "filter_fields": dict(filt),
            "outlets": sorted({o for q in deck for o in (q.filters.outlets or [])}),
            "sectors": sorted({s for q in deck for s in (q.filters.sectors or [])}),
            "coarse_groups": sorted({s for q in deck for s in (q.filters.coarse_groups or [])}),
            "languages": sorted({s for q in deck for s in (q.filters.languages or [])}),
            "question_languages": dict(collections.Counter("en" if q.question.isascii() else "other" for q in deck)),
            "replay": sum(q.filters.temporal_mode == "replay" for q in deck)}


# ---------- duplicate and leakage screen (flags only; the owner decides) ----------

STOP = set("a an the and or of in on at to for by with about from what which who how why is are was were be been "
           "being has have had do does did said saying say says published publish written write reported report "
           "coverage outlets outlet sources source items item ari3 this that these those it its their there "
           "fashion according recent right now could known week".split())


def normalize(text):
    t = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def content_words(text):
    return {w.rstrip("s") for w in normalize(text).split() if w not in STOP and len(w) > 2}


def prior_questions():
    seen = {}
    for path in PRIOR_SOURCES:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    q = json.loads(line)
                    seen.setdefault(q["question"], {"id": q["question_id"],
                                                    "filters": {k: v for k, v in (q.get("filters") or {}).items()
                                                                if v not in (None, [], "publication")}})
    return seen


def duplicate_report(deck, prior=None):
    prior = prior or prior_questions()
    out = []
    for q in deck:
        nq, cw = normalize(q.question), content_words(q.question)
        fkeys = set(q.filters.model_dump(exclude_none=True, exclude_defaults=True))
        best = []
        for text, meta in prior.items():
            ratio = difflib.SequenceMatcher(None, nq, normalize(text)).ratio()
            shared = sorted(cw & content_words(text))
            same_filter_shape = fkeys == set(meta["filters"]) and bool(fkeys)
            best.append((ratio, shared, same_filter_shape, meta["id"], text, meta["filters"]))
        best.sort(key=lambda b: (-len(b[1]), -b[0]))
        top = best[0]
        exact = any(normalize(t) == nq for t in prior)
        flag = exact or top[0] >= 0.75 or bool(top[1])
        out.append({"question_id": q.question_id, "question": q.question, "exact_duplicate": exact,
                    "closest_prior": {"id": top[3], "question": top[4], "filters": top[5],
                                      "text_similarity": round(top[0], 3), "shared_content_words": top[1],
                                      "same_filter_shape": top[2]},
                    "flag_for_owner": flag})
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sha256_json(obj):
    """The hash exp005_v2.answer_question records as context_sha256."""
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False).encode()).hexdigest()


# ---------- frozen store snapshot ----------

def snapshot_store(src=None, dst=SNAPSHOT):
    """Copy the item store once with SQLite's online backup, which stays consistent while
    ingestion runs. An existing snapshot is never overwritten."""
    from item_store import DEFAULT_DB
    src = src or DEFAULT_DB
    if os.path.exists(dst):
        raise FileExistsError(f"the C1 snapshot already exists and is never overwritten: {dst}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    source = sqlite3.connect(f"file:{os.path.abspath(src)}?mode=ro", uri=True)
    target = sqlite3.connect(dst)
    with target:
        source.backup(target)
    source.close()
    target.close()
    return {"path": os.path.relpath(dst, ROOT).replace(os.sep, "/"), "sha256": sha256_file(dst)}


# ---------- retrieval-only packets ----------

def app_question(q):
    from rag_answer import AppQuestion
    if q.retrieval_query != q.question:
        raise ValueError(f"{q.question_id}: retrieval_query differs from the question")
    return AppQuestion(q.question_id, q.question, q.retrieval_query, q.filters)


def build_packet(q, corpus, index, prompt_text):
    """Everything exp005_v2.answer_question does before its provider step, and nothing after:
    retrieval IDs, status, the exact context and the exact Prompt v2 messages."""
    import exp005 as v1
    from rag_corpus import get_items
    from rag_eval import run_method
    from rag_validate import check_items
    aq = app_question(q)
    ids, seconds = run_method(corpus, index, aq, "hybrid", "auto", v1.MAX_ITEMS)
    rec = {"question_id": q.question_id, "question": q.question, "retrieval_query": aq.query,
           "filters": q.filters.model_dump(mode="json", exclude_none=True), "item_ids": ids,
           "retrieval_latency_ms": round(1000 * seconds, 1)}
    bad = check_items(corpus, ids, q.filters)
    if bad:
        return {**rec, "status": "context_invalid", "context_violations": {str(k): v for k, v in bad.items()}}
    if not ids:
        return {**rec, "status": "system_abstention", "context": [], "messages": None}
    evidence = {e.item_id: e for e in get_items(corpus, ids)}
    context = v1.serialize_context([evidence[i] for i in ids], q.filters)
    messages = v1.build_messages(aq, context, prompt_text)
    return {**rec, "status": "packet_built", "context": context, "messages": messages,
            "context_sha256": sha256_json(context), "messages_sha256": sha256_json(messages),
            "context_chars": len(json.dumps(context, ensure_ascii=False))}


def parity_check(q, corpus, packet):
    """Run the question through ask_ari3 itself with a local ScriptedProvider that holds no
    response. The frozen pipeline computes its context hash, reaches its provider step, gets
    an immediate ProviderError and stops. Nothing is generated and nothing leaves the machine."""
    from llm_provider import ScriptedProvider
    from rag_answer import ask_ari3
    stub = ScriptedProvider([])
    out = ask_ari3(q.question, q.filters, provider=stub, corpus=corpus)
    same_messages = (stub.calls[0] == packet["messages"]) if stub.calls else packet.get("messages") is None
    return {"ids_match": out["retrieval"]["item_ids"] == packet["item_ids"],
            "context_sha256_match": out["context_sha256"] == packet.get("context_sha256"),
            "messages_match": same_messages,
            "retrieval_query_is_question": out["retrieval_query"] == q.question,
            "stopped_before_generation": out["answer"] is None and not out["audit"]["attempts"]}


def build_packets(deck, snapshot=SNAPSHOT):
    """All packets plus per-question integrity checks. The snapshot is opened read-only."""
    import exp005_v2 as v2
    from rag_answer import FROZEN_INDEX_DIR, verify_identity
    from rag_corpus import get_items, open_corpus
    from rag_index import Index
    if os.environ.get("ARI3_LIVE_LLM"):
        raise RuntimeError("ARI3_LIVE_LLM is set; packets are built only with live calls disabled")
    identity = verify_identity()
    snap_before = sha256_file(snapshot)
    corpus, index = open_corpus(snapshot), Index(FROZEN_INDEX_DIR)
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    cutoff = identity["index_cutoff_first_seen_at"]
    packets, checks = [], {}
    for q in deck:
        p = build_packet(q, corpus, index, prompt_text)
        again = build_packet(q, corpus, index, prompt_text)
        seen = {e.item_id: e.first_seen_at for e in get_items(corpus, p["item_ids"])}
        checks[q.question_id] = {
            "retrieval_query_is_question": p["retrieval_query"] == q.question,
            "deterministic": again["item_ids"] == p["item_ids"] and again.get("context_sha256") == p.get("context_sha256"),
            "at_most_10_items": len(p["item_ids"]) <= 10,
            "all_items_in_frozen_index": all(i in index.row for i in p["item_ids"]),
            "all_first_seen_before_cutoff": all(seen.get(i) and seen[i] < cutoff for i in p["item_ids"]),
            "context_valid": p["status"] != "context_invalid",
            **{f"ask_ari3_{k}": v for k, v in parity_check(q, corpus, p).items()}}
        packets.append(p)
    corpus.close()
    integrity = {"identity_verified": True, "snapshot_unchanged": sha256_file(snapshot) == snap_before,
                 "live_provider_module_loaded": "llm_deepseek" in sys.modules,
                 "questions_passing_every_check": sum(all(c.values()) for c in checks.values()),
                 "failures": {qid: sorted(k for k, v in c.items() if not v) for qid, c in checks.items()
                              if not all(c.values())}}
    return packets, checks, integrity, identity, snap_before


def manifest(packets, integrity, identity, snapshot_sha, built_at):
    """The committable record: item IDs and fingerprints, no headline or excerpt text."""
    rows = [{"question_id": p["question_id"], "status": p["status"], "item_ids": p["item_ids"],
             "n_items": len(p["item_ids"]), "context_sha256": p.get("context_sha256"),
             "messages_sha256": p.get("messages_sha256"), "context_chars": p.get("context_chars")} for p in packets]
    return {"version": "exp005-holdout-packets-v1", "built_at": built_at,
            "questions_sha256": sha256_file(FROZEN), "protocol_sha256": sha256_file(PROTOCOL),
            "store_snapshot": {"path": os.path.relpath(SNAPSHOT, ROOT).replace(os.sep, "/"), "sha256": snapshot_sha},
            "pipeline": {k: identity[k] for k in ("pipeline", "protocol_v2_sha256", "prompt_v2_sha256",
                                                  "schema_v2_sha256", "retriever_v1_sha256", "serializer",
                                                  "index_cutoff_first_seen_at")},
            "packets_sha256": sha256_json(rows), "integrity": integrity, "provider_calls": 0, "packets": rows}


# ---------- blind packet-sufficiency deck ----------

SUFFICIENCY_PROMPT = ("Does this evidence packet hold enough evidence to answer the question, within its "
                      "constraints? Judge only what is shown here.")
SUFFICIENCY_OPTIONS = [("s", "Sufficient", "SUFFICIENT"), ("i", "Insufficient", "INSUFFICIENT"),
                       ("u", "Unsure", "UNSURE")]


def packet_text(p):
    """The packet as the model would receive it, laid out for reading. A question's
    categories and probe text are never shown, so the reviewer stays blind to what it tests."""
    if p["status"] != "packet_built":
        return f"EMPTY PACKET ({p['status']}): no eligible evidence. The model would not be called.\n"
    payload = json.loads(p["messages"][1]["content"])
    head = (f"CONSTRAINTS\n{payload['constraints']['description']}\n\n"
            f"EVIDENCE PACKET ({len(p['context'])} items, ranking order)\n\n")
    items = []
    for n, e in enumerate(p["context"], 1):
        seen = f"  |  first seen {e['first_seen_at']}" if "first_seen_at" in e else ""
        items.append(f"[{n}] item {e['item_id']}  |  {e['outlet']}  |  {e['sector_group']}  |  published "
                     f"{e['published_at']}{seen}  |  {e['language']}\n{e['headline'] or '(no headline)'}\n"
                     f"{(e['excerpt'] or '').strip()}\n{e['url']}\n")
    return head + "\n".join(items)


def deck_tasks(packets, seed=DECK_SEED):
    """One card per question, in a fixed shuffled order (so categories do not arrive in blocks)."""
    order = list(packets)
    random.Random(seed).shuffle(order)
    return [{"task_id": f"{p['question_id']}:sufficiency", "question_id": p["question_id"], "question": p["question"],
             "kind": "packet_sufficiency", "target": "packet", "prompt": SUFFICIENCY_PROMPT, "body": packet_text(p),
             "options": [{"key": k, "label": label, "value": v} for k, label, v in SUFFICIENCY_OPTIONS]}
            for p in order]


def write_deck(packets, manifest_sha):
    """The ARI3 Review queue. Judgments append to REVIEWS (latest answer wins), with notes."""
    import label_tool
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": "Packet sufficiency (EXP-005 holdout)",
             "outputs_sha256": manifest_sha, "packets_manifest": os.path.relpath(MANIFEST, ROOT).replace(os.sep, "/"),
             "notes": True, "reviews_path": os.path.relpath(REVIEWS, ROOT).replace(os.sep, "/"),
             "seed": DECK_SEED, "tasks": deck_tasks(packets), "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue), queue


def load_packets(path=PACKETS):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "duplicates", "snapshot", "packets", "deck"])
    args = ap.parse_args(argv)
    if args.cmd == "snapshot":
        print(json.dumps(snapshot_store(), indent=1))
        return 0
    deck = load_deck()
    if args.cmd == "check":
        body = {"errors": deck_errors(deck), "coverage": coverage(deck)}
    elif args.cmd == "duplicates":
        body = duplicate_report(deck)
    elif args.cmd == "packets":
        from item_store import utc_now
        if os.path.exists(PACKETS) or os.path.exists(MANIFEST):
            raise FileExistsError("packets already built; C1 retrieval runs once")
        packets, checks, integrity, identity, snap_sha = build_packets(deck)
        m = manifest(packets, integrity, identity, snap_sha, utc_now())
        with open(PACKETS, "w", encoding="utf-8", newline="\n") as f:
            for p in packets:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
            json.dump(m, f, indent=1, ensure_ascii=False)
            f.write("\n")
        body = {"packets_sha256": m["packets_sha256"], "manifest_sha256": sha256_file(MANIFEST),
                "integrity": integrity, "statuses": dict(collections.Counter(p["status"] for p in packets))}
    else:
        path, queue = write_deck(load_packets(), sha256_file(MANIFEST))
        body = {"queue": path, "tasks": len(queue["tasks"]), "reviews_path": queue["reviews_path"]}
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 1 if args.cmd == "check" and body["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
