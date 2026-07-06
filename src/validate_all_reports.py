#############################################################
# validate_all_reports.py
# standalone check that every archived report in data/reports/
# still conforms to the schema in report_schema.py. Added after
# data/reports/2026-05-07.json was found to have silently failed
# validation (bad vocab values) with nobody noticing until a
# subagent happened to check. Run manually or in CI so a bad
# report fails loudly instead of sitting in the archive unnoticed.
#
# usage: python src/validate_all_reports.py
# exit code 0 = all reports valid, 1 = at least one failed.
#############################################################

import sys

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


def main() -> int:
    dates = list_report_dates()

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

        warnings.extend(find_high_confidence_warnings(report_date, data))

    if failures:
        print(f"FAILED: {len(failures)} of {len(dates)} report(s) failed schema validation:\n")
        for report_date, reason in failures:
            print(f"  - {report_date}.json: {reason}")
        return 1

    print(f"OK: all {len(dates)} report(s) in data/reports/ passed schema validation.")

    if warnings:
        print(f"\n{len(warnings)} non-blocking confidence WARNING(s) — editor review suggested, not a failure:")
        for w in warnings:
            print(f"  WARNING: {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
