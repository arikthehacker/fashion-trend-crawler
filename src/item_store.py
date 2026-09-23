#############################################################
# item_store.py
# the dated, linked item store every report and model reads from
# (docs/MOONSHOTS_2026-09-22.md sections 3 and 19; schema in
# db/migrations/). rule: no store row, no claim.
#
# the database file is local data, not repo content: it lives in
# data/store/ (never committed). a published dataset release is a
# separate, deliberate export.
#
# usage:
#   python src/item_store.py init  [--db PATH]   create / migrate
#   python src/item_store.py stats [--db PATH]   row counts
#############################################################

import argparse
import glob
import hashlib
import os
import sqlite3
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from taxonomy import classify_source

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(ROOT, "db", "migrations")
DEFAULT_DB = os.path.join(ROOT, "data", "store", "ari3lla.db")

# sector mappings apply from this date unless a later mapping supersedes
# them (outlet_sector_history is a type-2 dimension).
SECTOR_HISTORY_START = "1900-01-01"

TRACKING_PARAMS = ("utm_", "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "cmpid")

SOURCE_METHODS = ("rss", "wayback", "commoncrawl", "api", "manual")
TS_PRECISIONS = ("exact", "day", "week", "snapshot_upper_bound")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path: str = DEFAULT_DB) -> sqlite3.Connection:
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def applied_versions(con: sqlite3.Connection) -> set:
    exists = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    if not exists:
        return set()
    return {v for (v,) in con.execute("SELECT version FROM schema_version")}


def migrate(con: sqlite3.Connection) -> list:
    """apply every db/migrations/NNNN_*.sql not yet applied, in order, each
    in its own transaction. returns the versions applied now."""
    done = applied_versions(con)
    applied = []
    for path in sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "[0-9][0-9][0-9][0-9]_*.sql"))):
        version = int(os.path.basename(path)[:4])
        if version in done:
            continue
        with open(path, encoding="utf-8") as f:
            sql = f.read()
        # executescript commits first and runs outside a transaction, so wrap it.
        con.executescript("BEGIN;\n" + sql + f"\nINSERT INTO schema_version VALUES ({version}, '{utc_now()}');\nCOMMIT;")
        applied.append(version)
    return applied


def canonical_url(url: str) -> str:
    """drop fragments and tracking parameters, lowercase the host, and strip
    a trailing slash, so the same article fetched twice is one row."""
    p = urlparse(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                       if not k.lower().startswith(TRACKING_PARAMS)])
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), p.netloc.lower(), path, "", query, ""))


def outlet_domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower().split(":")[0]
    return netloc[4:] if netloc.startswith("www.") else netloc


def upsert_outlet(con: sqlite3.Connection, domain: str) -> int:
    """return outlet_id, creating the outlet and its sector mapping
    (from taxonomy.classify_source; unmapped domains get 'unclear')."""
    row = con.execute("SELECT outlet_id FROM outlets WHERE domain = ?", (domain,)).fetchone()
    if row:
        return row[0]
    outlet_id = con.execute("INSERT INTO outlets (domain) VALUES (?)", (domain,)).lastrowid
    sector = classify_source(domain)
    con.execute(
        "INSERT INTO outlet_sector_history (outlet_id, sector_id, valid_from, valid_to, rationale) "
        "VALUES (?, ?, ?, NULL, ?)",
        (outlet_id, sector, SECTOR_HISTORY_START,
         f"taxonomy.classify_source() as of {utc_now()[:10]}"
         + ("; domain not in DOMAIN_SECTOR_MAP" if sector == "unclear" else "")),
    )
    return outlet_id


def content_hash(*parts: str) -> str:
    return hashlib.sha256("\n".join(p or "" for p in parts).encode("utf-8")).hexdigest()


def upsert_item(con: sqlite3.Connection, *, url: str, published_at: str, source_method: str,
                ts_precision: str = "exact", title: str = "", fetched_at: str = "",
                hash_basis: str = "", wayback_url: str = None) -> tuple:
    """insert or refresh one fetched item. idempotent on the canonical URL:
    re-fetching unchanged content changes nothing; changed content updates
    title, fetched_at and content_hash. returns (item_id, status) where status
    is 'inserted', 'updated' or 'unchanged'."""
    if source_method not in SOURCE_METHODS:
        raise ValueError(f"source_method {source_method!r} not in {SOURCE_METHODS}")
    if ts_precision not in TS_PRECISIONS:
        raise ValueError(f"ts_precision {ts_precision!r} not in {TS_PRECISIONS}")
    url = canonical_url(url)
    fetched_at = fetched_at or utc_now()
    digest = content_hash(title, hash_basis)
    outlet_id = upsert_outlet(con, outlet_domain(url))

    before = con.execute("SELECT item_id, content_hash FROM items WHERE url = ?", (url,)).fetchone()
    con.execute(
        """INSERT INTO items (outlet_id, url, title, published_at, ts_precision, fetched_at,
                              content_hash, wayback_url, source_method)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(url) DO UPDATE SET
             title = excluded.title,
             fetched_at = excluded.fetched_at,
             content_hash = excluded.content_hash
           WHERE excluded.content_hash <> items.content_hash""",
        (outlet_id, url, title, published_at, ts_precision, fetched_at, digest, wayback_url, source_method),
    )
    if before is None:
        item_id = con.execute("SELECT item_id FROM items WHERE url = ?", (url,)).fetchone()[0]
        return item_id, "inserted"
    return before[0], ("unchanged" if before[1] == digest else "updated")


def stats(con: sqlite3.Connection) -> dict:
    out = {"schema_versions": sorted(applied_versions(con))}
    for table in ("outlets", "items", "terms", "mentions", "reports"):
        out[table] = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    out["items_by_coarse_sector"] = dict(con.execute(
        "SELECT coarse_group, SUM(items) FROM v_exposure_weekly GROUP BY 1 ORDER BY 2 DESC"
    ).fetchall())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["init", "stats"])
    ap.add_argument("--db", default=DEFAULT_DB)
    args = ap.parse_args(argv)
    con = connect(args.db)
    applied = migrate(con)
    if args.command == "init":
        print(f"{args.db}: applied migrations {applied or 'none (up to date)'}")
    else:
        for k, v in stats(con).items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
