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
    list_report_dates,
    load_report,
    validate_report,
)


def main() -> int:
    dates = list_report_dates()

    if not dates:
        print("No reports found in data/reports/ — nothing to validate.")
        return 0

    failures = []

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

    if failures:
        print(f"FAILED: {len(failures)} of {len(dates)} report(s) failed schema validation:\n")
        for report_date, reason in failures:
            print(f"  - {report_date}.json: {reason}")
        return 1

    print(f"OK: all {len(dates)} report(s) in data/reports/ passed schema validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
