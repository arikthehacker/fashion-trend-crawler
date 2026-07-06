#############################################################
# audit_confidence.py
# standalone, read-only audit comparing each signal's assigned
# `confidence` (LLM/hand-set) against derive_confidence()'s
# formula-based value across every report in data/reports/.
# Does not mutate report_schema.py, summarize.py, or any data
# files — derive_confidence() is opt-in and not wired into the
# save/validate pipeline (see
# docs/agent-logs/confidence-derivation-impl.md), so this script
# exists to surface where the two disagree without changing
# behavior. See docs/agent-logs/confidence-audit.md for findings.
#
# usage: python src/audit_confidence.py
# exit code is always 0 — this is a report, not a gate.
#############################################################

from report_schema import derive_confidence, list_report_dates, load_report


def main() -> int:
    dates = list_report_dates()
    total = 0
    mismatches = []

    for report_date in dates:
        report = load_report(report_date)
        for signal in report.get("top_signals", []):
            total += 1
            assigned = signal.get("confidence")
            derived = derive_confidence(signal)
            if assigned != derived:
                mismatches.append(
                    {
                        "date": report_date,
                        "name": signal.get("name"),
                        "assigned": assigned,
                        "derived": derived,
                        "corroboration_count": signal.get(
                            "source_corroboration_count", 1
                        ),
                        "source_sectors": signal.get("source_sectors", []),
                    }
                )

    print(f"Total signals checked: {total}")
    print(f"Mismatches: {len(mismatches)}\n")
    for m in mismatches:
        print(
            f"[{m['date']}] {m['name']!r}: assigned={m['assigned']!r} "
            f"derived={m['derived']!r} "
            f"corroboration_count={m['corroboration_count']} "
            f"source_sectors={m['source_sectors']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
