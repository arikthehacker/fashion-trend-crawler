#############################################################
# run_ingest.py
# one scheduled collection run: ingest every feed in data/feeds.json into
# the item store, mark mirrored copies (mirrors.py), append a line to the run
# log, then save a consistent dated copy of the database and keep the newest
# KEEP_BACKUPS copies. While it runs, data/store/ingest.running holds its start
# time, so report preparation can wait for it to finish.
#
# scheduled every 4 hours (Windows Task Scheduler, task "ARI3LLA ingest").
#
# usage: python src/run_ingest.py [--db PATH]
#############################################################

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone

import mirrors
from ingest_rss import ingest_feed, load_feeds
from item_store import DEFAULT_DB, connect, migrate, stats

KEEP_BACKUPS = 14


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="one scheduled ingest run, with log and backup")
    ap.add_argument("--db", default=DEFAULT_DB)
    args = ap.parse_args(argv)

    store_dir = os.path.dirname(os.path.abspath(args.db))
    log_path = os.path.join(store_dir, "ingest-log.jsonl")
    backup_dir = os.path.join(store_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    started = datetime.now(timezone.utc)
    running = os.path.join(store_dir, "ingest.running")
    with open(running, "w", encoding="utf-8") as f:
        f.write(started.strftime("%Y-%m-%dT%H:%M:%SZ"))
    try:
        return _run(args, store_dir, log_path, backup_dir, started)
    finally:
        if os.path.exists(running):
            os.remove(running)


def _run(args, store_dir, log_path, backup_dir, started):
    con = connect(args.db)
    migrate(con)
    totals = {"inserted": 0, "updated": 0, "unchanged": 0, "undated": 0, "future": 0}
    failed = []
    for feed in load_feeds():
        c = ingest_feed(con, feed)
        for k in totals:
            totals[k] += c[k]
        if c["error"]:
            failed.append(f"{feed['domain']}: {c['error']}")
    marked = mirrors.mark(con)

    # VACUUM INTO writes a consistent snapshot even while the source is open.
    stamp = started.strftime("%Y-%m-%dT%H%MZ")
    backup = os.path.join(backup_dir, f"ari3lla-{stamp}.db")
    con.execute("VACUUM INTO ?", (backup,))
    for old in sorted(glob.glob(os.path.join(backup_dir, "ari3lla-*.db")))[:-KEEP_BACKUPS]:
        os.remove(old)

    entry = {
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **totals,
        "failed_feeds": failed,
        "mirror_copies_marked": marked,
        "items_total": stats(con)["items"],
        "backup": os.path.basename(backup),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
