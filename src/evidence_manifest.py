"""Evidence manifests and frozen review snapshots for new reports. No article text.

Two artifacts with two meanings:

  evidence-manifest-v1 (data/evidence/<date>.json): current-store membership. "Do these
    evidence identities exist in the store?" Checked against the live store on the fields
    that never change.

  evidence-review-snapshot-v1 (data/evidence/<date>.snapshot.json): the frozen evidence
    state the editor reviewed. Every recorded field, including fetched_at and content_hash
    as observed when the snapshot was built, is verified against the store at build time.
    A deterministic SHA-256 covers the snapshot, and a publishable report carries that
    fingerprint in evidence_snapshot_sha256. Later feed refreshes may change fetched_at or
    content_hash in the live store. That never rewrites or invalidates the snapshot.

The publish gate requires the snapshot for new reports (src/validate_all_reports.py).

  local:  report -> snapshot (fingerprint, coverage) -> live store (identity fields)
  CI:     report -> committed snapshot (fingerprint, coverage)

usage:
  python src/evidence_manifest.py build data/reports/<report_date>.json      # v1 membership manifest
  python src/evidence_manifest.py snapshot <report.json> [--bind]           # frozen review snapshot
"""

import hashlib
import json
import os
import sqlite3
import sys

from item_store import DEFAULT_DB, ROOT, canonical_url

EVIDENCE_DIR = os.path.join(ROOT, "data", "evidence")
MANIFEST_VERSION = "evidence-manifest-v1"
SNAPSHOT_VERSION = "evidence-review-snapshot-v1"
SNAPSHOT_FINGERPRINTED = ("snapshot_version", "report_date", "collection_window", "items")
ENTRY_KEYS = ("item_id", "url", "published_at", "retrieved_at", "first_seen_at", "first_seen_basis", "content_hash")
# Fields that never change once an item is stored. fetched_at (retrieved_at) and
# content_hash can change when a feed updates an item, so they are recorded, not re-checked.
IMMUTABLE = ("item_id", "url", "published_at", "first_seen_at", "first_seen_basis")


def manifest_path(report_date):
    return os.path.join(EVIDENCE_DIR, f"{report_date}.json")


def snapshot_path(report_date):
    return os.path.join(EVIDENCE_DIR, f"{report_date}.snapshot.json")


def report_evidence(report):
    """Every evidence item in a report: report level and per signal."""
    items = list(report.get("evidence_items") or [])
    for signal in report.get("top_signals", []):
        items += signal.get("evidence_items") or []
    return [e for e in items if isinstance(e, dict)]


def load_store_index(db_path=DEFAULT_DB):
    """{canonical url: entry} for every stored item, read-only. None when the store is missing."""
    if not os.path.exists(db_path):
        return None
    con = sqlite3.connect(f"file:{os.path.abspath(db_path)}?mode=ro", uri=True)
    try:
        return {r[1]: dict(zip(ENTRY_KEYS, r)) for r in con.execute(
            "SELECT item_id, url, published_at, fetched_at, first_seen_at, first_seen_basis, content_hash FROM items")}
    finally:
        con.close()


def build_manifest(report, store_index):
    """The manifest for a report, from the store. Raises if any evidence URL is not stored."""
    entries, missing = {}, []
    for e in report_evidence(report):
        url = canonical_url(e["url"])
        hit = store_index.get(url)
        if hit is None:
            missing.append(e["url"])
        else:
            entries[url] = hit
    if missing:
        raise ValueError(f"evidence URLs not in the item store: {missing}")
    return {"manifest_version": MANIFEST_VERSION, "report_date": report["report_date"],
            "collection_window": report.get("collection_window"),
            "items": sorted(entries.values(), key=lambda x: x["item_id"])}


def shape_errors(manifest, report, version_key="manifest_version", version=MANIFEST_VERSION):
    """Checks that need no store: the manifest is well formed and covers the report exactly."""
    if manifest is None:
        return [f"evidence manifest missing (data/evidence/{report.get('report_date')}.json)"]
    errors = []
    if manifest.get(version_key) != version:
        errors.append(f"evidence manifest version {manifest.get(version_key)!r} is not {version!r}")
    if manifest.get("report_date") != report.get("report_date"):
        errors.append("evidence manifest report_date does not match the report")
    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        return errors + ["evidence manifest has no items"]
    by_url = {}
    seen_ids = set()
    for k, entry in enumerate(items):
        if not isinstance(entry, dict) or any(key not in entry for key in ENTRY_KEYS):
            errors.append(f"evidence manifest item {k} is malformed")
            continue
        if not isinstance(entry["item_id"], int) or not str(entry["url"]).startswith(("http://", "https://")):
            errors.append(f"evidence manifest item {k} has a bad item_id or url")
            continue
        if entry["url"] != canonical_url(entry["url"]):
            errors.append(f"evidence manifest item {k} url is not in canonical form")
        if entry["item_id"] in seen_ids or entry["url"] in by_url:
            errors.append(f"evidence manifest repeats item {entry['item_id']} or {entry['url']}")
        seen_ids.add(entry["item_id"])
        by_url[entry["url"]] = entry
    for e in report_evidence(report):
        url = canonical_url(e.get("url", ""))
        entry = by_url.get(url)
        if entry is None:
            errors.append(f"evidence URL is not in the evidence manifest: {e.get('url')!r}")
        elif "item_id" in e and e["item_id"] != entry["item_id"]:
            errors.append(f"report and evidence manifest disagree on the item for {url!r}")
        elif e.get("published_at") and e["published_at"][:10] != str(entry["published_at"])[:10]:
            errors.append(f"report and evidence manifest disagree on published_at for {url!r}")
    return errors


def store_errors(manifest, store_index):
    """Local check: every manifest entry still matches the real item store."""
    errors = []
    for entry in (manifest or {}).get("items") or []:
        if not isinstance(entry, dict):
            continue
        stored = store_index.get(entry.get("url"))
        if stored is None:
            errors.append(f"evidence manifest item {entry.get('item_id')} is not in the item store")
            continue
        changed = [k for k in IMMUTABLE if stored[k] != entry.get(k)]
        if changed:
            errors.append(f"evidence manifest item {entry.get('item_id')} differs from the item store in {changed}")
    return errors


# ---------- frozen review snapshot ----------

def snapshot_fingerprint(snapshot):
    """Deterministic SHA-256 of the evidence state (build time excluded)."""
    body = {k: snapshot.get(k) for k in SNAPSHOT_FINGERPRINTED}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def build_snapshot(report, store_index, frozen_at=None):
    """The frozen review snapshot for a report, from the store as it is now. Every field the
    report's evidence records (item_id, published_at, retrieved_at, content_hash, first-seen)
    must still match the store, so the snapshot is the state the draft was generated from."""
    v1 = build_manifest(report, store_index)  # raises if any evidence URL is not stored
    drift = []
    for e in report_evidence(report):
        stored = store_index[canonical_url(e["url"])]
        for key in ("item_id", "published_at", "retrieved_at", "content_hash", "first_seen_at", "first_seen_basis"):
            if key not in e:
                continue
            day_only = key in ("published_at", "retrieved_at") and isinstance(e[key], str) and len(e[key]) == 10
            if (str(stored[key])[:10] if day_only else stored[key]) != e[key]:
                drift.append(f"{e['url']} {key}")
    if drift:
        raise ValueError(f"the store changed since the draft was generated (regenerate the draft): {drift[:10]}")
    snapshot = {"snapshot_version": SNAPSHOT_VERSION, "report_date": report["report_date"],
                "collection_window": report.get("collection_window"), "items": v1["items"],
                "frozen_at": frozen_at}
    for entry in snapshot["items"]:  # every recorded field, verified against the store at build time
        if store_index.get(entry["url"]) != entry:
            raise ValueError(f"snapshot entry {entry['item_id']} does not match the store")
    snapshot["snapshot_sha256"] = snapshot_fingerprint(snapshot)
    return snapshot


def snapshot_errors(snapshot, report):
    """Checks that need no store: the snapshot is intact, bound to the report, covers its
    evidence exactly, and has no duplicate identities."""
    if snapshot is None:
        return [f"evidence review snapshot missing (data/evidence/{report.get('report_date')}.snapshot.json)"]
    errors = []
    recomputed = snapshot_fingerprint(snapshot)
    if snapshot.get("snapshot_sha256") != recomputed:
        errors.append("evidence review snapshot does not match its own fingerprint (it changed after freezing)")
    if report.get("evidence_snapshot_sha256") != recomputed:
        errors.append("report is not bound to this evidence review snapshot (evidence_snapshot_sha256 differs)")
    if snapshot.get("collection_window") != report.get("collection_window"):
        errors.append("evidence review snapshot and report disagree on the collection window")
    errors += shape_errors(snapshot, report, "snapshot_version", SNAPSHOT_VERSION)
    return errors


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ok = (len(argv) == 2 and argv[0] in ("build", "snapshot")) or (len(argv) == 3 and argv[0] == "snapshot"
                                                                   and argv[2] == "--bind")
    if not ok:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        report = json.load(f)
    store = load_store_index()
    if store is None:
        print("not built: the item store is not available", file=sys.stderr)
        return 1
    try:
        if argv[0] == "build":
            out, path, mode = build_manifest(report, store), manifest_path(report["report_date"]), "w"
        else:
            from datetime import datetime, timezone
            path, mode = snapshot_path(report["report_date"]), "x"
            if os.path.exists(path):
                print(f"not built: {path} already exists. A new review needs a new report version.", file=sys.stderr)
                return 1
            out = build_snapshot(report, store, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    except ValueError as e:
        print(f"not built: {e}", file=sys.stderr)
        return 1
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, sort_keys=True)
    print(f"wrote {path}: {len(out['items'])} evidence items")
    if argv[0] == "snapshot":
        print(f"snapshot_sha256 {out['snapshot_sha256']}")
        if len(argv) == 3:
            report["evidence_snapshot_sha256"] = out["snapshot_sha256"]
            with open(argv[1], "w", encoding="utf-8", newline="\n") as f:
                json.dump(report, f, indent=1, ensure_ascii=False)
            print(f"bound {argv[1]} to it")
    return 0

if __name__ == "__main__":
    sys.exit(main())
