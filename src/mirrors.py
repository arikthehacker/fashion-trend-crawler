"""Mirrored feeds: one publisher serving the same articles on more than one domain.

A mirror domain counts as the same source as its canonical domain, and an item on a mirror
domain whose content is identical to an item on the canonical domain is marked as a copy
(items.syndicated_of = the canonical item). Every count, view, draft and retrieval already
excludes items with syndicated_of set, so a mirrored article counts once.

Only measured mirrors go in MIRRORS. Evidence for each entry is kept next to it.

usage:
  python src/mirrors.py report      # how many copies would be marked, changes nothing
  python src/mirrors.py mark        # mark them (also run at the end of every ingest)
"""

import argparse
import json
import sys

from item_store import DEFAULT_DB, connect

# mirror domain -> canonical domain
MIRRORS = {
    # 2026-10-21: 483 of 564 fashionunited.uk items (86%) have a content hash identical to a
    # fashionunited.com item; no other outlet pair in the store shares more than 1%.
    "fashionunited.uk": "fashionunited.com",
}


def source_of(domain):
    """The source a domain counts as."""
    return MIRRORS.get(domain, domain)


def _copies(con):
    """(copy item_id, canonical item_id) for unmarked mirror-domain items with an identical
    content hash on the canonical domain. The earliest canonical item is the one kept."""
    out = []
    for mirror, canonical in MIRRORS.items():
        out += con.execute(
            """SELECT m.item_id, (SELECT c.item_id FROM items c JOIN outlets oc ON oc.outlet_id = c.outlet_id
                                  WHERE oc.domain = ? AND c.content_hash = m.content_hash AND c.syndicated_of IS NULL
                                  ORDER BY c.published_at, c.item_id LIMIT 1)
               FROM items m JOIN outlets om ON om.outlet_id = m.outlet_id
               WHERE om.domain = ? AND m.syndicated_of IS NULL""", (canonical, mirror)).fetchall()
    return [(i, c) for i, c in out if c is not None]


def mark(con):
    """Mark every unmarked mirror copy. Returns how many were marked. Idempotent."""
    pairs = _copies(con)
    con.executemany("UPDATE items SET syndicated_of = ? WHERE item_id = ? AND syndicated_of IS NULL",
                    [(c, i) for i, c in pairs])
    con.commit()
    return len(pairs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["report", "mark"])
    ap.add_argument("--db", default=DEFAULT_DB)
    args = ap.parse_args(argv)
    con = connect(args.db)
    already = con.execute("SELECT count(*) FROM items WHERE syndicated_of IS NOT NULL").fetchone()[0]
    if args.cmd == "report":
        body = {"would_mark": len(_copies(con)), "already_marked": already, "mirrors": MIRRORS}
    else:
        body = {"marked": mark(con), "already_marked": already, "mirrors": MIRRORS}
    print(json.dumps(body, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
