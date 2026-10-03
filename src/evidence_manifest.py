"""Evidence manifests: committed proof that a new report's evidence exists in the item store.

The item store is local and never committed, so CI cannot read it. When a new report is
promoted toward publication, this module writes data/evidence/<report_date>.json from the
local store: one entry per evidence item with its identity and dates, and no article text.

  local:  report -> evidence manifest -> real item store   (validate_all_reports.py)
  CI:     report -> committed evidence manifest            (validate_all_reports.py --store-optional)

usage:
  python src/evidence_manifest.py build data/reports/<report_date>.json
"""

import json
import os
import sqlite3
import sys

from item_store import DEFAULT_DB, ROOT, canonical_url

EVIDENCE_DIR = os.path.join(ROOT, "data", "evidence")
MANIFEST_VERSION = "evidence-manifest-v1"
ENTRY_KEYS = ("item_id", "url", "published_at", "retrieved_at", "first_seen_at", "first_seen_basis", "content_hash")
# Fields that never change once an item is stored. fetched_at (retrieved_at) and
# content_hash can change when a feed updates an item, so they are recorded, not re-checked.
IMMUTABLE = ("item_id", "url", "published_at", "first_seen_at", "first_seen_basis")


def manifest_path(report_date):
    return os.path.join(EVIDENCE_DIR, f"{report_date}.json")


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


def shape_errors(manifest, report):
    """Checks that need no store: the manifest is well formed and covers the report exactly."""
    if manifest is None:
        return [f"evidence manifest missing (data/evidence/{report.get('report_date')}.json)"]
    errors = []
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        errors.append(f"evidence manifest version {manifest.get('manifest_version')!r} is not {MANIFEST_VERSION!r}")
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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] != "build":
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        report = json.load(f)
    store = load_store_index()
    if store is None:
        print("not built: the item store is not available", file=sys.stderr)
        return 1
    try:
        manifest = build_manifest(report, store)
    except ValueError as e:
        print(f"not built: {e}", file=sys.stderr)
        return 1
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    path = manifest_path(report["report_date"])
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False, sort_keys=True)
    print(f"wrote {path}: {len(manifest['items'])} evidence items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
