"""One-time reconstruction of items.first_seen_at for rows stored before migration 0004.

For every item, the earliest surviving record that shows ARI3 held it is taken as its
first-seen time. That value is an upper bound: ARI3 may have held the item earlier, and
no record of that survives. Rows get first_seen_basis = 'reconstructed' and
first_seen_evidence naming the winning record. New rows are stamped 'live_insert' by the
database itself (migration 0004), so this script never touches them.

Evidence, in tie-break order:
  current_fetched_at       the row's fetched_at now (fetched_at only moves later)
  backup:<file>            fetched_at in a store backup, matched by item_id AND url
  prediction_ledger:<ver>  earliest label_predictions.created_at (append-only table)
  label:<task>             earliest labels.created_at
Ledger and label evidence carries only an item_id. It is rejected when any backup shows
that item_id with a different url. Any evidence earlier than the item's published_at, or
not an ISO UTC timestamp, is rejected and reported.

Usage:
  python src/backfill_first_seen.py --backups DIR [--backups DIR ...]            # dry run
  python src/backfill_first_seen.py --backups DIR --apply --expect-fingerprint SHA

The dry run opens every database read-only and writes a JSON report and a JSONL plan.
--apply needs migration 0004, the exact fingerprint of a reviewed dry run, and runs in a
single transaction that rolls back if any post-condition fails.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sqlite3
import statistics
import sys
from datetime import datetime, timezone

from item_store import DEFAULT_DB, ROOT

V002_FREEZE = "2026-09-26T19:25:40Z"
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
SOURCE_ORDER = {"current_fetched_at": 0, "backup": 1, "prediction_ledger": 2, "label": 3}
MIGRATION_PATHS = [os.path.join(ROOT, "db", "migrations", "0004_first_seen.sql"),
                   os.path.join(ROOT, "design", "0004_first_seen_PROPOSED.sql.txt")]


def migration_sql():
    """Text of migration 0004, wherever it currently lives."""
    for path in MIGRATION_PATHS:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
    raise FileNotFoundError("migration 0004 not found")


def has_first_seen(con):
    return "first_seen_at" in {r[1] for r in con.execute("PRAGMA table_info(items)")}


def _hours(a, b):
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 3600


def science_counts(con):
    """Counts the backfill must leave unchanged."""
    labels = con.execute("SELECT item_id, task, label, source, labeler, split, created_at FROM labels "
                         "ORDER BY label_id").fetchall()
    return {"items": con.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            "style_events": con.execute("SELECT COUNT(*) FROM v_events_style").fetchone()[0],
            "mentions": con.execute("SELECT COUNT(*) FROM mentions").fetchone()[0],
            "labels": len(labels),
            "labels_sha256": hashlib.sha256(json.dumps(labels).encode()).hexdigest(),
            "label_predictions": con.execute("SELECT COUNT(*) FROM label_predictions").fetchone()[0]}


def build_plan(con, backup_paths, freeze=V002_FREEZE):
    """Return (plan, report). plan is [(item_id, first_seen_at, evidence)] for every row that
    still needs a value. The report counts sources, rejections and anomalies."""
    rows = {i: (url, pub, fet) for i, url, pub, fet in
            con.execute("SELECT item_id, url, published_at, fetched_at FROM items")}
    todo = (set(rows) if not has_first_seen(con) else
            {r[0] for r in con.execute("SELECT item_id FROM items WHERE first_seen_at IS NULL")})
    evidence = {i: [(fet, "current_fetched_at")] for i, (_, _, fet) in rows.items()}
    rejected, anomalies = {}, {"backup_later_than_current": 0}
    backup_urls = {}

    def reject(reason):
        rejected[reason] = rejected.get(reason, 0) + 1

    for path in sorted(backup_paths):
        b = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            for iid, url, fet in b.execute("SELECT item_id, url, fetched_at FROM items"):
                backup_urls.setdefault(iid, set()).add(url)
                if iid not in rows or rows[iid][0] != url:
                    reject("backup_row_not_in_store_or_url_differs")
                    continue
                if fet > rows[iid][2]:
                    anomalies["backup_later_than_current"] += 1
                evidence[iid].append((fet, f"backup:{os.path.basename(path)}"))
        finally:
            b.close()

    id_only = [("prediction_ledger", "SELECT item_id, model_version, MIN(created_at) FROM label_predictions "
                                     "GROUP BY item_id, model_version"),
               ("label", "SELECT item_id, task, MIN(created_at) FROM labels GROUP BY item_id, task")]
    for kind, sql in id_only:
        for iid, tag, ts in con.execute(sql):
            if iid not in rows:
                reject(f"{kind}_item_missing")
            elif backup_urls.get(iid, {rows[iid][0]}) != {rows[iid][0]}:
                reject(f"{kind}_url_conflict")
            else:
                evidence[iid].append((ts, f"{kind}:{tag}"))

    plan, source_counts, id_only_wins, earlier = [], {}, 0, []
    failures = []
    for iid in sorted(todo):
        url, pub, fet = rows[iid]
        valid = []
        for ts, src in evidence[iid]:
            if not ISO.match(ts or ""):
                reject("bad_timestamp_format")
            elif ts < pub:
                reject("before_published_at")
            else:
                valid.append((ts, SOURCE_ORDER[src.split(":")[0]], src))
        ts, _, src = min(valid)
        if not (pub <= ts <= fet):
            failures.append(iid)
        plan.append((iid, ts, src))
        kind = src.split(":")[0]
        source_counts[kind] = source_counts.get(kind, 0) + 1
        id_only_wins += kind in ("prediction_ledger", "label")
        if ts < fet:
            earlier.append(_hours(ts, fet))

    pre_freeze_after = sum(1 for iid, ts, _ in plan if ts <= freeze < rows[iid][2])
    report = {
        "rows_in_store": len(rows),
        "rows_to_backfill": len(plan),
        "backups_read": [os.path.basename(p) for p in sorted(backup_paths)],
        "winning_source_counts": source_counts,
        "id_only_evidence_wins": id_only_wins,
        "earlier_than_current_fetched_at": {
            "items": len(earlier),
            "median_hours": round(statistics.median(earlier), 2) if earlier else 0,
            "max_hours": round(max(earlier), 2) if earlier else 0},
        "rejected_evidence": rejected,
        "anomalies": anomalies,
        "invariant_failures": failures,
        "first_seen_at_or_before_freeze_but_fetched_after": {"freeze": freeze, "items": pre_freeze_after},
        "range": {"min": min((t for _, t, _ in plan), default=None), "max": max((t for _, t, _ in plan), default=None)},
        "fingerprint": fingerprint(plan),
        "science_counts": science_counts(con),
    }
    return plan, report


def fingerprint(plan):
    body = "\n".join(json.dumps([i, t, s]) for i, t, s in sorted(plan))
    return hashlib.sha256(body.encode()).hexdigest()


def apply_plan(con, plan, expected_fingerprint, before_counts):
    """Write the plan in one transaction and check every post-condition. Rolls back and
    raises on any failure."""
    if not has_first_seen(con):
        raise RuntimeError("items.first_seen_at does not exist. Apply migration 0004 first.")
    if fingerprint(plan) != expected_fingerprint:
        raise RuntimeError("plan fingerprint differs from the reviewed dry run")
    ids = [i for i, _, _ in plan]
    try:
        con.execute("BEGIN IMMEDIATE")
        cur = con.executemany(
            "UPDATE items SET first_seen_at = ?, first_seen_basis = 'reconstructed', first_seen_evidence = ? "
            "WHERE item_id = ? AND first_seen_at IS NULL", [(t, s, i) for i, t, s in plan])
        checks = {
            "rows_updated": cur.rowcount == len(plan),
            "no_null_first_seen": con.execute("SELECT COUNT(*) FROM items WHERE first_seen_at IS NULL")
                                     .fetchone()[0] == 0,
            "ordering": con.execute("SELECT COUNT(*) FROM items WHERE first_seen_at < published_at "
                                    "OR first_seen_at > fetched_at").fetchone()[0] == 0,
            "science_counts_unchanged": science_counts(con) == before_counts,
        }
        planned = set(ids)
        basis = dict(con.execute("SELECT item_id, first_seen_basis FROM items"))
        checks["planned_rows_reconstructed"] = all(basis[i] == "reconstructed" for i in planned)
        checks["other_rows_live_insert"] = all(b == "live_insert" for i, b in basis.items() if i not in planned)
        failed = [k for k, ok in checks.items() if not ok]
        if failed:
            raise RuntimeError(f"post-conditions failed: {failed}")
        con.execute("COMMIT")
        return checks
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--backups", action="append", required=True, help="folder of store backups (repeatable)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(DEFAULT_DB), "first_seen_backfill"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--expect-fingerprint")
    args = ap.parse_args(argv)

    paths = sorted(p for d in args.backups for p in glob.glob(os.path.join(d, "*.db")))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    os.makedirs(args.out, exist_ok=True)
    if args.apply:
        if not args.expect_fingerprint:
            ap.error("--apply needs --expect-fingerprint from a reviewed dry run")
        con = sqlite3.connect(args.db, isolation_level=None)
        con.execute("PRAGMA foreign_keys = ON")
    else:
        con = sqlite3.connect(f"file:{os.path.abspath(args.db)}?mode=ro", uri=True)
    plan, report = build_plan(con, paths)
    report["mode"] = "apply" if args.apply else "dry-run"
    report["run_at"] = stamp
    if args.apply:
        report["post_conditions"] = apply_plan(con, plan, args.expect_fingerprint, report["science_counts"])
    with open(os.path.join(args.out, f"{report['mode']}-{stamp}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(args.out, f"{report['mode']}-{stamp}.plan.jsonl"), "w", encoding="utf-8") as f:
        for row in plan:
            f.write(json.dumps(row) + "\n")
    print(json.dumps(report, indent=1))
    return 1 if report["invariant_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
