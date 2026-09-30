"""Read-only access to the ARI3 evidence store for EXP-004.

The store (data/store/ari3lla.db) is opened with SQLite's read-only URI mode and
`PRAGMA query_only`, so retrieval code cannot change evidence. Every filter is a bound
parameter. Column names come from fixed strings in this file, never from input.

Temporal modes (Filters.temporal_mode):
  publication  published_at <= as_of. "What had been published by T?"
  replay       published_at <= as_of AND first_seen_at <= as_of. "What could ARI3 have
               known by T?" Reconstructed first_seen_at values can be later than the true
               first sighting, so replay can omit evidence ARI3 had, and never admits
               evidence it acquired later.

Sector filters use the outlet's sector valid on the item's publication day
(outlet_sector_history is versioned).
"""

import hashlib
import os
import sqlite3

from item_store import DEFAULT_DB
from rag_schema import Evidence, Filters, lower_bound, upper_bound

ITEM_COLUMNS = """i.item_id, i.url, i.title, i.text_excerpt, o.domain, h.sector_id, s.coarse_group,
    CASE WHEN i.lang IS NULL THEN NULL ELSE lower(substr(i.lang, 1, 2)) END,
    i.published_at, i.first_seen_at, i.first_seen_basis, i.fetched_at"""

ITEM_JOINS = """FROM items i
    JOIN outlets o ON o.outlet_id = i.outlet_id
    LEFT JOIN outlet_sector_history h ON h.outlet_id = i.outlet_id
         AND h.valid_from <= substr(i.published_at, 1, 10)
         AND (h.valid_to IS NULL OR substr(i.published_at, 1, 10) < h.valid_to)
    LEFT JOIN sectors s ON s.sector_id = h.sector_id"""


def open_corpus(path=DEFAULT_DB):
    """A read-only connection to the evidence store."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    con = sqlite3.connect(f"file:{os.path.abspath(path)}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = ON")
    if "first_seen_at" not in {r[1] for r in con.execute("PRAGMA table_info(items)")}:
        raise RuntimeError("the store has no first_seen_at column (migration 0004)")
    return con


def where_clause(filters: Filters):
    """(sql, params) selecting the items that satisfy every filter. Parameterized."""
    clauses = ["i.syndicated_of IS NULL"]
    params = []
    lo, hi = lower_bound(filters.start_date), upper_bound(filters.end_date)
    if lo:
        clauses.append("i.published_at >= ?")
        params.append(lo)
    if hi:
        clauses.append("i.published_at <= ?")
        params.append(hi)
    if filters.as_of:
        as_of = upper_bound(filters.as_of)
        clauses.append("i.published_at <= ?")
        params.append(as_of)
        if filters.temporal_mode == "replay":
            clauses.append("i.first_seen_at <= ?")
            params.append(as_of)
    for column, values in (("lower(substr(i.lang, 1, 2))", filters.languages), ("h.sector_id", filters.sectors),
                           ("s.coarse_group", filters.coarse_groups), ("o.domain", filters.outlets)):
        if values:
            clauses.append(f"{column} IN ({','.join('?' * len(values))})")
            params.extend(values)
    return " AND ".join(clauses), params


def eligible_ids(con, filters: Filters):
    sql, params = where_clause(filters)
    return [r[0] for r in con.execute(f"SELECT i.item_id {ITEM_JOINS} WHERE {sql} ORDER BY i.item_id", params)]


def _evidence(row):
    keys = ("item_id", "url", "title", "excerpt", "outlet", "sector", "coarse_group", "lang",
            "published_at", "first_seen_at", "first_seen_basis", "fetched_at")
    return Evidence(**dict(zip(keys, row)))


def get_items(con, item_ids):
    """Evidence records for the given IDs, in the order given. Missing IDs are omitted."""
    ids = list(dict.fromkeys(int(i) for i in item_ids))
    if not ids:
        return []
    rows = {r[0]: r for r in con.execute(
        f"SELECT {ITEM_COLUMNS} {ITEM_JOINS} WHERE i.item_id IN ({','.join('?' * len(ids))})", ids)}
    return [_evidence(rows[i]) for i in ids if i in rows]


def satisfies(con, item_ids, filters: Filters):
    """The subset of item_ids that satisfies every filter."""
    ids = list(dict.fromkeys(int(i) for i in item_ids))
    if not ids:
        return set()
    sql, params = where_clause(filters)
    return {r[0] for r in con.execute(
        f"SELECT i.item_id {ITEM_JOINS} WHERE {sql} AND i.item_id IN ({','.join('?' * len(ids))})", params + ids)}


def corpus_texts(con, cutoff=None):
    """(item_id, content_hash, text) for every original item, optionally only those ARI3
    had first seen by `cutoff`. The text is title + stored excerpt, the same text the
    ARI3 classifiers read (jev_spike.text)."""
    sql = "SELECT item_id, content_hash, title, text_excerpt FROM items WHERE syndicated_of IS NULL"
    params = []
    if cutoff:
        sql += " AND first_seen_at <= ?"
        params.append(cutoff)
    return [(i, h, f"{t or ''}. {e or ''}"[:1000]) for i, h, t, e in con.execute(sql + " ORDER BY item_id", params)]


def fingerprint(rows):
    """SHA-256 over sorted item_id:content_hash pairs. It changes when an item is added
    or its stored text changes."""
    body = "\n".join(f"{i}:{h}" for i, h, *_ in sorted(rows))
    return hashlib.sha256(body.encode()).hexdigest()
