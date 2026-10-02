"""Lexicon v1 sense check (directive 037): one card per stored mention of a term flagged
"needs sense check", asking whether the highlighted use is the fashion sense.

The review answers only that question about one mention. It does not decide whether a
term belongs in the lexicon, and it changes nothing in Lexicon v1. Judgments go to an
append-only log, latest answer wins. Each card's task ID binds the term, the item, the
match position and a fingerprint of the stored text the match was found in.

usage:
  python src/lexicon_sense.py inventory    # read-only count and alignment check
  python src/lexicon_sense.py make-deck    # writes the deck and, once, its manifest
"""

import argparse
import collections
import hashlib
import json
import os
import re
import sys

import lexicon
from item_store import ROOT

OUT = os.path.join(ROOT, "lexicon", "v1")
MANIFEST = os.path.join(OUT, "sense_check_v1.manifest.json")
LOG = os.path.join(OUT, "sense_check_v1_reviews.jsonl")
QUEUE_NAME = "lexicon_sense_check_v1"
TITLE = "Lexicon sense check — v1"
OPTIONS = [("y", "Yes, fashion sense", "YES"), ("n", "No", "NO"), ("u", "Unsure", "UNSURE")]


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inventory(con):
    """Every stored mention of a flagged term, re-matched against the current stored text."""
    flagged = [r[0] for r in con.execute("SELECT term_id FROM term_rules WHERE needs_sense_check=1 ORDER BY term_id")]
    lex = dict(lexicon.compile_lexicon(con))
    rows = con.execute(
        f"""SELECT m.mention_id, m.term_id, m.item_id, m.span_start, m.extractor_version, t.canonical,
                   i.title, i.text_excerpt, i.published_at, o.domain
            FROM mentions m JOIN terms t USING (term_id) JOIN items i USING (item_id)
            LEFT JOIN outlets o ON o.outlet_id = i.outlet_id
            WHERE m.term_id IN ({','.join('?' * len(flagged))})
            ORDER BY m.term_id, m.item_id, m.span_start""", flagged).fetchall()
    cards, misaligned = [], []
    for mid, term, item, span, ext, canonical, title, excerpt, published, domain in rows:
        text = lexicon.item_text(title, excerpt)
        m = lex[term].match(text, span)
        if not m:
            misaligned.append({"mention_id": mid, "term": term, "item_id": item, "span_start": span})
            continue
        cards.append({"mention_id": mid, "term": term, "canonical": canonical, "item_id": item, "span_start": span,
                      "span_end": m.end(), "matched": m.group(0), "extractor_version": ext,
                      "context_sha256": _sha(text), "published_at": published, "outlet": domain or "unknown",
                      "_text": text})
    return flagged, cards, misaligned


def _body(c):
    t = c["_text"]
    marked = t[:c["span_start"]] + "«" + t[c["span_start"]:c["span_end"]] + "»" + t[c["span_end"]:]
    head, _, rest = marked.partition("\n")
    return (f"TERM: {c['canonical']}    MATCHED: \"{c['matched']}\" (marked «like this» below)\n\n"
            f"item {c['item_id']}  |  {c['outlet']}  |  {(c['published_at'] or '')[:10]}\n\n"
            f"HEADLINE\n{head}\n\nSTORED EXCERPT\n{rest.strip() or '(empty)'}\n\n"
            "Judge from ARI3's stored text only. Do not open the article.")


def task_id(c):
    return f"{c['term']}|{c['item_id']}|{c['span_start']}|{c['context_sha256'][:12]}"


def build_tasks(cards):
    return [{"task_id": task_id(c), "question_id": c["term"], "kind": "lexicon_sense", "target": f"item {c['item_id']}",
             "question": "Is this the fashion sense of the highlighted term?",
             "prompt": f"Term: {c['canonical']}. Is the marked use the fashion sense?",
             "options": [{"key": k, "label": label, "value": v} for k, label, v in OPTIONS], "body": _body(c)}
            for c in cards]


def inventory_sha(cards):
    return _sha(json.dumps(sorted(task_id(c) for c in cards)))


def make_deck(con):
    import label_tool
    flagged, cards, misaligned = inventory(con)
    if misaligned:
        raise RuntimeError(f"{len(misaligned)} stored mentions no longer match their item text: {misaligned[:10]}")
    sha = inventory_sha(cards)
    body = {"deck": TITLE, "lexicon_version": lexicon.LEXICON_VERSION, "flagged_terms": flagged,
            "mentions": len(cards), "by_term": {t: sum(c["term"] == t for c in cards) for t in flagged},
            "items": len({c["item_id"] for c in cards}), "inventory_sha256": sha,
            "question": "Is this the fashion sense of the highlighted term?", "judgments": [o[2] for o in OPTIONS],
            "unit": "one stored mention (term, item, match position) in ARI3's stored headline and excerpt",
            "task_id": "term|item_id|span_start|first 12 hex of the SHA-256 of the stored text matched",
            "log": os.path.relpath(LOG, ROOT).replace(os.sep, "/"), "convention": "append-only, latest answer wins",
            "not_decided_here": "whether a term stays in the lexicon; no keep or drop threshold; no Lexicon v2",
            "cards": [{k: v for k, v in c.items() if not k.startswith("_") and k not in ("matched",)} for c in cards]}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            if json.load(f)["inventory_sha256"] != sha:
                raise RuntimeError("the mention inventory changed since the deck was frozen")
    else:
        os.makedirs(OUT, exist_ok=True)
        with open(MANIFEST, "x", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=1, ensure_ascii=False)
    queue = {"kind": "gen_review", "task": QUEUE_NAME, "title": TITLE, "notes": True, "outputs_sha256": sha,
             "reviews_path": body["log"], "tasks": build_tasks(cards), "item_ids": []}
    return label_tool._write_queue(QUEUE_NAME, queue), body


def main(argv=None):
    from rag_corpus import open_corpus
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["inventory", "make-deck"])
    args = ap.parse_args(argv)
    con = open_corpus()  # read-only: Lexicon v1 is never modified here
    try:
        if args.cmd == "inventory":
            flagged, cards, misaligned = inventory(con)
            body = {"flagged_terms": flagged, "mentions": len(cards) + len(misaligned), "aligned": len(cards),
                    "misaligned": misaligned, "by_term": dict(collections.Counter(c["term"] for c in cards)),
                    "items": len({c["item_id"] for c in cards})}
        else:
            path, manifest = make_deck(con)
            body = {"queue": path, **{k: manifest[k] for k in ("deck", "mentions", "by_term", "items",
                                                               "inventory_sha256", "log")}}
    except RuntimeError as e:
        print(f"not run: {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
