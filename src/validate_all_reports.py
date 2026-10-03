#############################################################
# validate_all_reports.py
# standalone check that every archived report in data/reports/
# still conforms to the schema in report_schema.py. Added after
# data/reports/2026-05-07.json was found to have silently failed
# validation (bad vocab values) with nobody noticing until a
# subagent happened to check. Run manually or in CI so a bad
# report fails loudly instead of sitting in the archive unnoticed.
#
# usage: python src/validate_all_reports.py [--store-optional]
# exit code 0 = all reports valid, 1 = at least one failed.
#
# Reports dated after HISTORICAL_CUTOFF (every report from the item-store
# pipeline on) must also be reviewed, carry an editor note on every signal,
# and cite only items in the item store (owner decision Q21, 2026-10-03).
# Proof of the last rule is a committed evidence manifest
# (data/evidence/<report_date>.json, src/evidence_manifest.py). CI checks the
# report against the manifest. Locally, the manifest is also checked against
# the real store. --store-optional never waives the manifest.
#############################################################

import argparse
import os
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

import json

from evidence_manifest import load_store_index, manifest_path, shape_errors, store_errors

from report_schema import (
    SchemaValidationError,
    derive_confidence,
    list_report_dates,
    load_report,
    validate_report,
)


def find_high_confidence_warnings(report_date, data):
    """Non-blocking check: flag signals assigned 'high' confidence that
    derive_confidence() would only support at 'medium' or 'low', per
    docs/agent-logs/confidence-audit.md. Never affects exit code."""
    warnings = []
    for signal in data.get("top_signals", []):
        assigned = signal.get("confidence")
        if assigned != "high":
            continue
        derived = derive_confidence(signal)
        if derived in ("medium", "low"):
            warnings.append(
                f"{report_date}.json: {signal.get('name')!r} assigned "
                f"'high' confidence but derive_confidence() supports only "
                f"'{derived}' (corroboration_count="
                f"{signal.get('source_corroboration_count', 1)}, "
                f"source_sectors={signal.get('source_sectors', [])}) — "
                f"consider editor re-review."
            )
    return warnings


# The last report published before the item-store pipeline. Reports dated on or
# before it are checked under the rules they were published under.
HISTORICAL_CUTOFF = "2026-05-18"
SKIP_STORE = object()  # the item store is knowingly unavailable (CI): the manifest is still required


def load_manifest(report_date):
    path = manifest_path(report_date)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def new_report_errors(data, store, manifest):
    """Owner decision Q21 and the step-3 review: rules for reports dated after
    HISTORICAL_CUTOFF. The committed evidence manifest is required everywhere. Where the
    item store exists, the manifest is also checked against it."""
    errors = []
    if data.get("review_status") != "reviewed":
        errors.append(f"review_status is {data.get('review_status')!r}, and a new report needs 'reviewed' to publish")
    for i, signal in enumerate(data.get("top_signals", [])):
        if not (signal.get("human_editor_note") or "").strip():
            errors.append(f"top_signals[{i}] {signal.get('name', '')!r} has no human_editor_note")
    errors.extend(shape_errors(manifest, data))
    if store is SKIP_STORE or manifest is None:
        return errors
    if store is None:
        errors.append("the item store is not available, so the evidence manifest could not be checked against it")
        return errors
    errors.extend(store_errors(manifest, store))
    return errors


def publish_gate_errors(data, today, store=None, manifest=None):
    """Integrity rules for anything in data/reports/ (the published archive).
    Schema validity is not enough: a report may exist only if it describes a
    week that has happened and every claim links to a specific fetched item.
    Added 2026-09-22 after an agent loop published 94 simulated reports
    (see data/archive/simulated/README.md). `today` is YYYY-MM-DD (UTC)."""
    errors = []
    report_date = data.get("report_date", "")
    if report_date > today:
        errors.append(f"report_date {report_date} is after today ({today})")
    signals = data.get("top_signals", [])
    if not signals and not data.get("evidence_items"):
        errors.append("report has no signals and no report-level evidence_items "
                      "(a thin-week summary still states facts that need links)")
    groups = [("report", data.get("evidence_items") or [], False)]
    for i, signal in enumerate(signals):
        groups.append((f"top_signals[{i}] {signal.get('name', '')!r}",
                       signal.get("evidence_items") or [], True))
    for label, items, required in groups:
        if required and not items:
            errors.append(f"{label} has no evidence_items (every claim needs an article URL)")
        for j, item in enumerate(items):
            url = item.get("url", "") if isinstance(item, dict) else ""
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                errors.append(f"{label} evidence_items[{j}] is not a full URL: {url!r}")
            elif parsed.path.strip("/") == "" and not parsed.query:
                errors.append(f"{label} evidence_items[{j}] is a homepage, not an article: {url!r}")
            published = (item.get("published_at") or "")[:10] if isinstance(item, dict) else ""
            if published and report_date and published > report_date:
                errors.append(f"{label} evidence_items[{j}] published {published}, after the report date")
    if report_date > HISTORICAL_CUTOFF:
        errors.extend(new_report_errors(data, store, manifest))
    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate every report in data/reports/.")
    ap.add_argument("--store-optional", action="store_true",
                    help="when the item store is missing (CI), skip only the store check; new reports still "
                         "need a committed evidence manifest that covers their evidence")
    args = ap.parse_args(argv)
    dates = list_report_dates()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    store = load_store_index()
    if store is None and args.store_optional:
        store = SKIP_STORE
        if any(d > HISTORICAL_CUTOFF for d in dates):
            print("NOTE: item store not available. New reports were checked against their committed evidence "
                  "manifests only.")

    if not dates:
        print("No reports found in data/reports/ — nothing to validate.")
        return 0

    failures = []
    warnings = []

    for report_date in dates:
        try:
            data = load_report(report_date)
        except (OSError, ValueError) as exc:
            failures.append((report_date, f"could not load/parse JSON: {exc}"))
            continue

        try:
            validate_report(data)
        except SchemaValidationError as exc:
            failures.append((report_date, str(exc)))
            continue

        gate = publish_gate_errors(data, today, store, load_manifest(report_date))
        if gate:
            failures.append((report_date, "publish gate: " + "; ".join(gate)))
            continue

        warnings.extend(find_high_confidence_warnings(report_date, data))

    if failures:
        print(f"FAILED: {len(failures)} of {len(dates)} report(s) failed validation:\n")
        for report_date, reason in failures:
            print(f"  - {report_date}.json: {reason}")
        return 1

    print(f"OK: all {len(dates)} report(s) in data/reports/ passed schema validation and the publish gate.")

    if warnings:
        print(f"\n{len(warnings)} non-blocking confidence WARNING(s) — editor review suggested, not a failure:")
        for w in warnings:
            print(f"  WARNING: {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
