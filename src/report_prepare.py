"""Weekly report preparation, run unattended after a collection window closes (Windows task
"ARI3LLA report prep"). No model call beyond the frozen style classifier, no network, no AI.

For the most recent closed Monday-to-Sunday window it:
  1. refuses unless the window has closed and an ingest run has finished after the close;
  2. backs up the item store and checks its health;
  3. scores and extracts only the window's remaining items (append-only);
  4. verifies nothing existing was rewritten and nothing outside the window was touched;
  5. drafts the report from scratch (draft_report.py: exact {yes} only, no prose, no decisions);
  6. builds the frozen evidence review snapshot and binds the draft to it (the cutoff);
  7. audits the candidates' evidence for mirrored and possibly duplicated publications;
  8. writes the review package and the "Report decisions" deck for ARI3 Review.

It never publishes, never commits, never writes to data/reports/ and never decides keep or drop.
If the store changes while it runs (an ingest was active), it removes what it wrote and exits so a
later run can start clean. A window that is already prepared is left alone.

usage:
  python src/report_prepare.py                 # the most recent closed window
  python src/report_prepare.py --start 2026-10-05 --end 2026-10-11
  python src/report_prepare.py --check         # say what would happen, change nothing
"""

import argparse
import collections
import difflib
import hashlib
import itertools
import json
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone

import report_review as rr

STYLE_SQL = "model_version='ari3-v0.0.2' and task='is_style_signal'"
ITEM_COLS = ("item_id,url,title,text_excerpt,published_at,fetched_at,first_seen_at,first_seen_basis,content_hash,"
             "syndicated_of,outlet_id,lang")


def now_utc():
    return datetime.now(timezone.utc)


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def default_window(now):
    """The most recent Monday-to-Sunday window that has fully closed (UTC)."""
    d = now.date()
    end = d - timedelta(days=(d.weekday() + 1) % 7 or 7)
    return (end - timedelta(days=6)).isoformat(), end.isoformat()


def bounds(start, end):
    return f"{start}T00:00:00Z", f"{(date.fromisoformat(end) + timedelta(days=1)).isoformat()}T00:00:00Z"


def last_ingest(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = [line for line in f if line.strip()]
    return json.loads(lines[-1]) if lines else None


def readiness(paths, start, end, now):
    """(ready, reason). Ready means the window is closed and a later ingest run has finished."""
    close = bounds(start, end)[1]
    if stamp(now) < close:
        return False, f"the window closes at {close}"
    run = last_ingest(paths.ingest_log)
    if run is None or run.get("started_at", "") < close:
        return False, f"no ingest run has started and finished since the window closed at {close}"
    return True, f"last ingest finished {run['finished_at']}"


def _sha(con, sql, params=()):
    h, n = hashlib.sha256(), 0
    for row in con.execute(sql, params):
        h.update(json.dumps(row, ensure_ascii=False, default=str).encode())
        n += 1
    return n, h.hexdigest()


def store_state(con, lo, hi):
    s = {"items": con.execute("select count(*) from items").fetchone()[0],
         "items_sha256": _sha(con, f"select {ITEM_COLS} from items order by item_id")[1],
         "predictions_max_rowid": con.execute("select coalesce(max(rowid),0) from label_predictions").fetchone()[0],
         "mentions_max_rowid": con.execute("select coalesce(max(rowid),0) from mentions").fetchone()[0],
         "labels_sha256": _sha(con, "select rowid,* from labels order by rowid")[1],
         "terms_sha256": _sha(con, "select * from terms order by term_id")[1],
         "term_rules_sha256": _sha(con, "select * from term_rules order by term_id")[1],
         "window_items": con.execute("select count(*) from items where published_at>=? and published_at<?", (lo, hi)).fetchone()[0],
         "window_unscored": con.execute(f"""select count(*) from items where published_at>=? and published_at<? and item_id not in
             (select item_id from label_predictions where {STYLE_SQL})""", (lo, hi)).fetchone()[0],
         "outside_unscored": con.execute(f"""select count(*) from items where not (published_at>=? and published_at<?) and item_id not in
             (select item_id from label_predictions where {STYLE_SQL})""", (lo, hi)).fetchone()[0]}
    s["predictions"], s["predictions_sha256"] = _sha(con, "select rowid,* from label_predictions order by rowid")
    s["mentions"], s["mentions_sha256"] = _sha(con, "select rowid,* from mentions order by rowid")
    return s


def append_only_checks(pre, con, lo, hi):
    """Every check that scoring and extraction only added rows, and only for window items."""
    new_p = con.execute("""select p.item_id, i.published_at, p.task, p.model_version from label_predictions p
                           join items i using (item_id) where p.rowid>?""", (pre["predictions_max_rowid"],)).fetchall()
    new_m = con.execute("""select m.item_id, i.published_at from mentions m join items i using (item_id)
                           where m.rowid>?""", (pre["mentions_max_rowid"],)).fetchall()
    old = lambda table, top: _sha(con, f"select rowid,* from {table} where rowid<=? order by rowid", (top,))
    return {
        "existing_predictions_unchanged": old("label_predictions", pre["predictions_max_rowid"]) == (pre["predictions"], pre["predictions_sha256"]),
        "existing_mentions_unchanged": old("mentions", pre["mentions_max_rowid"]) == (pre["mentions"], pre["mentions_sha256"]),
        "labels_unchanged": _sha(con, "select rowid,* from labels order by rowid")[1] == pre["labels_sha256"],
        "items_unchanged": _sha(con, f"select {ITEM_COLS} from items order by item_id")[1] == pre["items_sha256"],
        "lexicon_unchanged": _sha(con, "select * from terms order by term_id")[1] == pre["terms_sha256"]
                             and _sha(con, "select * from term_rules order by term_id")[1] == pre["term_rules_sha256"],
        "new_predictions_equal_pre_unscored": len(new_p) == pre["window_unscored"] == len({r[0] for r in new_p}),
        "new_predictions_in_window": all(lo <= r[1] < hi for r in new_p),
        "new_predictions_are_frozen_style_model": all(r[2] == "is_style_signal" and r[3] == "ari3-v0.0.2" for r in new_p),
        "new_mentions_in_window": all(lo <= r[1] < hi for r in new_m),
        "window_fully_scored": con.execute(f"""select count(*) from items where published_at>=? and published_at<? and item_id not in
            (select item_id from label_predictions where {STYLE_SQL})""", (lo, hi)).fetchone()[0] == 0,
        "outside_window_untouched": con.execute(f"""select count(*) from items where not (published_at>=? and published_at<?) and
            item_id not in (select item_id from label_predictions where {STYLE_SQL})""", (lo, hi)).fetchone()[0] == pre["outside_unscored"],
        "integrity_ok": [r[0] for r in con.execute("pragma integrity_check")] == ["ok"],
    }, {"new_predictions": len(new_p), "new_mentions": len(new_m)}


# ---------- duplicate audit ----------

def _norm(text):
    t = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def _brand(domain):
    return domain.split(".")[0]


def duplicate_audit(report, db):
    """Exact mirrors (collapsed automatically later) and possible duplicates (the editor decides).

    exact:    same normalized headline, one publisher brand on two domains, same feed excerpt.
    possible: one publisher brand on two domains with a similar headline or a near-identical excerpt.
    Translations across languages are not detectable by this rule and are checked when the text is drafted."""
    items, where = {}, collections.defaultdict(list)
    for s in report["top_signals"]:
        for e in s["evidence_items"]:
            items[e["item_id"]] = e
            where[e["item_id"]].append(s["signal_id"])
    con = sqlite3.connect(f"file:{os.path.abspath(db)}?mode=ro", uri=True)
    excerpt = {}
    ids = sorted(items)
    for k in range(0, len(ids), 500):
        chunk = ids[k:k + 500]
        excerpt.update(con.execute(f"select item_id, text_excerpt from items where item_id in ({','.join('?' * len(chunk))})", chunk))
    con.close()
    ratio = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0
    pairs = {"exact": [], "possible": []}
    for a, b in itertools.combinations(ids, 2):
        da, db_ = items[a]["outlet_domain"], items[b]["outlet_domain"]
        if da == db_ or _brand(da) != _brand(db_):
            continue
        ta, tb = _norm(items[a]["title"]), _norm(items[b]["title"])
        x = ratio(_norm(excerpt.get(a)), _norm(excerpt.get(b)))
        if ta == tb and x >= 0.9:
            pairs["exact"].append((a, b, "identical headline and feed excerpt, one publisher on two domains"))
        elif x >= 0.8 or ratio(ta, tb) >= 0.55:
            pairs["possible"].append((a, b, "one publisher brand on two domains with a similar headline or the same excerpt"))
    out = {}
    for kind, found in pairs.items():
        parent = {}
        find = lambda i: i if parent.setdefault(i, i) == i else find(parent[i])
        for a, b, _ in found:
            parent[find(a)] = find(b)
        groups = collections.defaultdict(set)
        for a, b, _ in found:
            groups[find(a)] |= {a, b}
        out[kind] = [{"why": found[0][2], "items": [{"item_id": i, "outlet": items[i]["outlet_domain"], "published": items[i]["published_at"],
                                                     "title": items[i]["title"], "signals": where[i]} for i in sorted(g)]}
                     for g in sorted(groups.values(), key=min)]
    return out


# ---------- the run ----------

def prepare(paths, start, end, now=None):
    import draft_report
    import evidence_manifest as em
    import lexicon
    from rag_corpus import open_corpus
    now = now or now_utc()
    lo, hi = bounds(start, end)
    draft_path, snap_path = paths.draft(end), paths.snapshot(end)
    if os.path.exists(draft_path) or os.path.exists(snap_path) or os.path.exists(paths.published(end)):
        return {"status": "already_prepared", "window": [start, end], "draft": draft_path}
    ready, reason = readiness(paths, start, end, now)
    if not ready:
        return {"status": "not_ready", "window": [start, end], "reason": reason}

    # backup, health, pre-run state
    backup_dir = os.path.join(paths.backups, f"report-prep-{end}-{now.strftime('%Y-%m-%dT%H%MZ')}")
    os.makedirs(backup_dir)
    src = sqlite3.connect(f"file:{os.path.abspath(paths.db)}?mode=ro", uri=True)
    health = {"integrity_check": [r[0] for r in src.execute("pragma integrity_check")],
              "foreign_key_violations": len(src.execute("pragma foreign_key_check").fetchall())}
    pre = store_state(src, lo, hi)
    dst = sqlite3.connect(os.path.join(backup_dir, "ari3lla.db"))
    with dst:
        src.backup(dst)
    dst.close()
    src.close()
    with open(os.path.join(backup_dir, "MANIFEST.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"made_at": stamp(now), "purpose": f"before report preparation for {start}..{end}", "health": health, "pre": pre}, f, indent=1)
    if health["integrity_check"] != ["ok"] or health["foreign_key_violations"]:
        return {"status": "failed", "reason": "the store failed its health check", "health": health, "backup": backup_dir}

    # score and extract the window (append-only), then verify
    lexicon.main(["--db", paths.db, "score", "--from", start, "--to", end])
    lexicon.main(["--db", paths.db, "extract", "--from", start, "--to", end])
    con = sqlite3.connect(f"file:{os.path.abspath(paths.db)}?mode=ro", uri=True)
    checks, info = append_only_checks(pre, con, lo, hi)
    con.close()
    if not all(checks.values()):
        return {"status": "failed", "reason": "append-only verification failed (was an ingest running?)",
                "failed_checks": sorted(k for k, v in checks.items() if not v), "backup": backup_dir}

    # draft from scratch, snapshot, bind
    corpus = open_corpus(paths.db)
    report = draft_report.build_draft(corpus, start, end)
    corpus.close()
    if not report["draft_meta"]["window_complete"] or report["draft_meta"]["unscored_items"]:
        return {"status": "failed", "reason": "the draft is incomplete or has unscored items", "backup": backup_dir}
    written = []
    try:
        for d in (paths.drafts, paths.evidence, paths.queues, paths.editing, paths.app):
            os.makedirs(d, exist_ok=True)
        if report["top_signals"]:
            snapshot = em.build_snapshot(report, em.load_store_index(paths.db), stamp(now_utc()))
            with open(snap_path, "x", encoding="utf-8", newline="\n") as f:
                json.dump(snapshot, f, indent=1, ensure_ascii=False, sort_keys=True)
            written.append(snap_path)
            report["evidence_snapshot_sha256"] = snapshot["snapshot_sha256"]
        else:
            snapshot = None
        with open(draft_path, "x", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=1, ensure_ascii=False)
        written.append(draft_path)
        audit = duplicate_audit(report, paths.db)
        with open(paths.audit(end), "w", encoding="utf-8", newline="\n") as f:
            json.dump(audit, f, indent=1, ensure_ascii=False)
        written.append(paths.audit(end))
        reviews = paths.decisions(end)
        rel = os.path.relpath(reviews, rr.ROOT).replace(os.sep, "/") if os.path.splitdrive(reviews)[0] == os.path.splitdrive(rr.ROOT)[0] else reviews
        queue = rr.build_decision_queue(report, audit, rel)
        with open(paths.queue(end), "w", encoding="utf-8", newline="\n") as f:
            json.dump(queue, f, indent=1, ensure_ascii=False)
        written.append(paths.queue(end))
        review_md = os.path.join(paths.editing, f"{end}-REVIEW.md")
        with open(review_md, "w", encoding="utf-8", newline="\n") as f:
            f.write(draft_report.review_markdown(report))
        written.append(review_md)
        con = sqlite3.connect(f"file:{os.path.abspath(paths.db)}?mode=ro", uri=True)
        still = _sha(con, f"select {ITEM_COLS} from items order by item_id")[1] == pre["items_sha256"]
        latest_seen = con.execute("select max(first_seen_at) from items where published_at>=? and published_at<?", (lo, hi)).fetchone()[0]
        con.close()
        if not still:
            raise RuntimeError("the item store changed during preparation (an ingest was running)")
    except Exception as e:
        for p in written:
            if os.path.exists(p):
                os.remove(p)
        return {"status": "failed", "reason": f"{type(e).__name__}: {e}"[:300], "backup": backup_dir, "removed": written}

    comp = report["draft_meta"]["composition"]
    sets = comp["prediction_sets"]
    result = {"status": "prepared", "window": [start, end], "cutoff": snapshot["frozen_at"] if snapshot else report["draft_meta"]["generated_at"],
              "last_ingest": last_ingest(paths.ingest_log)["finished_at"], "latest_first_seen_in_window": latest_seen,
              "backup": backup_dir, "draft": draft_path, "draft_sha256": rr.sha256_file(draft_path),
              "snapshot": snap_path if snapshot else None, "evidence_snapshot_sha256": snapshot["snapshot_sha256"] if snapshot else None,
              "snapshot_items": len(snapshot["items"]) if snapshot else 0,
              "items": comp["items"], "outlets": comp["outlets"], "style_positive": comp["style_positive_items"],
              "no": sets.get('["no"]', 0), "not_sure": sets.get('["yes", "no"]', 0),
              "candidates": [s["signal_id"] for s in report["top_signals"]],
              "exact_mirror_groups": len(audit["exact"]), "possible_duplicate_groups": len(audit["possible"]),
              "append_only": info, "checks_passed": len(checks), "queue": paths.queue(end), "review_package": review_md}
    record = os.path.join(paths.editing, f"{end}-PREPARED.md")
    with open(record, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join([
            f"# Prepared for review: report {start} to {end}", "",
            "**Status:** DRAFT. Not published, not committed. No candidate has been kept or dropped and no report prose exists.", "",
            f"- Cutoff (evidence snapshot frozen): **{result['cutoff']}**. Window items first seen later are not part of this report. Do not regenerate the draft.",
            f"- Last ingest before the cutoff finished {result['last_ingest']}. Latest first-seen time in the window: {latest_seen}.",
            f"- {comp['items']:,} raw source records from {comp['outlets']} outlet domains. Exact yes {comp['style_positive_items']:,}, "
            f"no {result['no']:,}, not sure {result['not_sure']:,} ({result['not_sure'] / comp['items']:.1%}, excluded).",
            f"- {len(report['top_signals'])} candidates: {', '.join(result['candidates']) or 'none'}.",
            f"- Evidence snapshot SHA-256 `{result['evidence_snapshot_sha256']}` ({result['snapshot_items']} items). Draft `{result['draft_sha256']}`.",
            f"- Scoring wrote {info['new_predictions']} predictions and extraction {info['new_mentions']} mention rows. All {len(checks)} append-only checks passed.",
            f"- Duplicate audit: {len(audit['exact'])} exact mirror groups (collapsed automatically when decisions are applied), "
            f"{len(audit['possible'])} possible groups (in the deck for the editor).",
            f"- Store backup: `{os.path.relpath(backup_dir, rr.ROOT).replace(os.sep, '/') if backup_dir.startswith(rr.ROOT) else backup_dir}`.", "",
            "## Next", "",
            f"Open ARI3 Review and work through **{queue['title']}**. Then tell Claude the report decisions are in.", ""]))
    result["record"] = record
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--db")
    ap.add_argument("--base", help="write everything under this folder (dry runs and tests)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if bool(args.start) != bool(args.end):
        ap.error("give both --start and --end, or neither")
    paths = rr.Paths(args.base, args.db)
    now = now_utc()
    start, end = (args.start, args.end) if args.start else default_window(now)
    if args.check:
        ready, reason = readiness(paths, start, end, now)
        result = {"status": "check", "window": [start, end], "ready": ready, "reason": reason,
                  "already_prepared": os.path.exists(paths.draft(end))}
    else:
        result = prepare(paths, start, end, now)
    result["ran_at"] = stamp(now)
    if not args.check:
        os.makedirs(os.path.dirname(paths.log), exist_ok=True)
        with open(paths.log, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return {"prepared": 0, "already_prepared": 0, "check": 0, "not_ready": 2}.get(result["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
