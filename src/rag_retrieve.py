"""Deterministic retrieval for EXP-004: BM25, dense, and hybrid by reciprocal rank fusion.

Filters are applied first, in SQL (rag_corpus.where_clause). Every method then ranks only
the items that passed, so similarity can never admit an item that fails a filter.

  bm25    SQLite FTS5 bm25() over title + stored excerpt (Robertson and Zaragoza 2009).
          `lexical` picks the tokenizer: "words" (unicode61), "trigram", or "auto",
          which uses trigrams when the query contains CJK characters.
  dense   cosine similarity between the query and item embeddings from the frozen
          ARI3 encoder (paraphrase-multilingual-MiniLM-L12-v2), brute force.
  hybrid  reciprocal rank fusion of the bm25 and dense rankings,
          score = sum over methods of 1 / (60 + rank) (Cormack, Clarke and Buettcher 2009).
Ties break by item_id, so the same inputs always give the same ranking.
"""

import json
import re

from rag_corpus import eligible_ids, get_items
from rag_schema import Hit, SearchArgs, SearchResult

RRF_K = 60
FUSION_DEPTH = 100
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")


def lexical_mode(query, lexical="auto"):
    if lexical not in ("auto", "words", "trigram"):
        raise ValueError(f"unknown lexical mode {lexical!r}")
    return ("trigram" if CJK.search(query) else "words") if lexical == "auto" else lexical


def fts_query(query, mode):
    """An FTS5 MATCH expression built only from quoted terms, so query text can never
    be read as FTS5 syntax. Returns None when no usable term remains."""
    tokens = re.findall(r"\w+", query.lower())
    if mode == "trigram":
        terms = sorted({t[n:n + 3] for t in tokens if len(t) >= 3 for n in range(len(t) - 2)})
    else:
        terms = sorted({t for t in tokens if len(t) >= 2})
    return " OR ".join('"' + t.replace('"', '""') + '"' for t in terms) or None


def bm25(index, query, candidates, k, lexical="auto"):
    mode = lexical_mode(query, lexical)
    match = fts_query(query, mode)
    if not match or not candidates:
        return [], mode
    table = {"words": "words", "trigram": "trigram"}[mode]
    rows = index.fts.execute(
        f"SELECT rowid, -bm25({table}) FROM {table} WHERE {table} MATCH ? "
        f"AND rowid IN (SELECT value FROM json_each(?))",
        (match, json.dumps(sorted(candidates)))).fetchall()
    rows.sort(key=lambda r: (-r[1], r[0]))
    return [(int(i), float(s)) for i, s in rows[:k]], mode


def dense(index, query, candidates, k):
    import numpy as np
    rows = [(i, index.row[i]) for i in sorted(candidates) if i in index.row]
    if not rows:
        return []
    q = np.asarray(index.encode_query(query), dtype="float32")
    scores = index.vectors[[r for _, r in rows]] @ q
    ranked = sorted(zip([i for i, _ in rows], scores.tolist()), key=lambda r: (-r[1], r[0]))
    return [(int(i), float(s)) for i, s in ranked[:k]]


def rrf(rankings, k, depth=FUSION_DEPTH):
    scores = {}
    for ranking in rankings:
        for rank, (item_id, _) in enumerate(ranking[:depth], 1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (RRF_K + rank)
    return sorted(scores.items(), key=lambda r: (-r[1], r[0]))[:k]


def rank(index, query, candidates, method, k, lexical="auto"):
    """(ranking, per-method rankings, lexical mode used). Each ranking is [(item_id, score)]."""
    candidates = set(candidates) & set(index.row)
    per, mode = {}, None
    if method in ("bm25", "hybrid"):
        per["bm25"], mode = bm25(index, query, candidates, max(k, FUSION_DEPTH), lexical)
    if method in ("dense", "hybrid"):
        per["dense"] = dense(index, query, candidates, max(k, FUSION_DEPTH))
    ranking = rrf(list(per.values()), k) if method == "hybrid" else per[method][:k]
    return ranking, per, mode


def search(corpus_con, index, args: SearchArgs, lexical="auto"):
    """Run one validated search and return hits with full provenance."""
    candidates = set(eligible_ids(corpus_con, args.filters)) & set(index.row)
    ranking, per, mode = rank(index, args.query, candidates, args.method, args.k, lexical)
    positions = {m: {i: n for n, (i, _) in enumerate(r, 1)} for m, r in per.items()}
    evidence = {e.item_id: e for e in get_items(corpus_con, [i for i, _ in ranking])}
    hits = [Hit(rank=n, score=s, evidence=evidence[i],
                ranks_by_method={m: p.get(i) for m, p in positions.items()})
            for n, (i, s) in enumerate(ranking, 1)]
    manifest = dict(index.manifest, lexical_mode_used=mode)
    return SearchResult(query=args.query, filters=args.filters, method=args.method, k=args.k,
                        eligible_items=len(candidates), hits=hits,
                        corpus_fingerprint=index.manifest["corpus_fingerprint"], index_manifest=manifest)
