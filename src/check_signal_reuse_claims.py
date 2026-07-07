#############################################################
# check_signal_reuse_claims.py
# standalone, read-only heuristic check for one specific, already-recurring
# failure pattern: a report's own prose (index_note / human_editor_note /
# limitations) claims a signal_id was "reused" or "continued" from a prior
# report, but the signal_id it names does not actually appear in that same
# report's own top_signals list.
#
# Why this exists: this exact bug happened for real at least twice --
#   - run 57/58: docs/agent-logs (see CHANGELOG run 58) -- a new report's
#     prose claimed the Met Gala signal_id was reused, but the saved report
#     did not actually carry that signal_id in top_signals.
#   - flagged again as a named, unaddressed process gap in
#     docs/agent-logs/gap-analysis-60-run-milestone-run60.md section 3:
#     "no lightweight, repeatable check ... that diffs 'what the agent's
#     log claims it did' against 'what the file actually contains' for
#     process claims like signal_id reuse."
#
# This is intentionally NARROW, like check_heading_patterns.py -- it does
# NOT attempt to verify agent claims in general (too broad/speculative,
# per the run-61 task scoping this was built under). It only checks one
# specific, mechanical thing:
#
#   1. Find "long-running tracked" signal_ids: any signal_id that appears
#      in top_signals across 2 or more reports in data/reports/.
#   2. For the single most-recently-modified report file, scan its prose
#      fields (top_signals[].index_note, top_signals[].human_editor_note,
#      limitations[]) for a reuse/continuation claim (regex on
#      "reus-"/"continu-"/"same signal_id") that also names one of those
#      known signal_id slugs as a literal substring.
#   3. If such a claim is found, verify that signal_id literally appears
#      as a signal_id in that report's OWN top_signals list. If it
#      doesn't, print a warning.
#
# Known limitations (heuristic, not exhaustive):
#   - Only checks the literal signal_id slug string appearing in prose --
#     a report that describes reuse by signal NAME instead of by slug
#     (e.g. "the Met Gala coverage gap" without the hyphenated id) will
#     not be caught. This mirrors how the real run-57/58 bug manifested
#     (the slug itself was named in prose) but is not a general claim
#     -vs-artifact verifier.
#   - Only checks the most-recently-modified report by default (pass
#     --all to check every report against every other report, which is
#     slower and noisier, since older reports' prose predates ids that
#     didn't exist yet -- default is scoped to what a single agent run
#     would want to self-check before finishing).
#   - Understands only a short, literal list of negation/precedent phrases
#     (see NEGATION_EXCLUSION_PHRASES), checked within a proximity window
#     around each named signal_id mention -- not general negation
#     detection. Added in run 81 after 5 confirmed false positives all
#     followed this exact pattern (naming a prior signal_id to explain why
#     it is NOT being carried forward, or as precedent for an unrelated
#     classification/confidence decision). A human still reviews warnings
#     before acting on them, same spirit as
#     check_field_coverage.py/audit_confidence.py.
#
# Exit code is always 0 -- informational only, not a CI gate. Not wired
# into CI or run.sh this run; can be run standalone.
#
# usage: python src/check_signal_reuse_claims.py [--all]
#############################################################

import os
import re
import sys

from report_schema import list_report_dates, load_report

REUSE_CLAIM_PATTERN = re.compile(
    r"\b(reuse[sd]?|reusing|continu(?:e[sd]?|ing|ation)|same signal_id)\b",
    re.IGNORECASE,
)

# Negation/precedent phrases that, when found close to a named signal_id,
# indicate the prose is explaining why that signal_id is NOT being carried
# forward / reused (or is being cited as precedent for an unrelated
# decision) rather than actually claiming reuse of it. Confirmed against 5
# known false positives (2026-09-14, 2026-09-28, 2026-10-05, 2027-06-28,
# 2027-10-11 -- see docs/agent-logs/signal-reuse-checker-improvement-run81.md).
# Deliberately a short, literal, high-precision list rather than general
# negation detection -- if a named signal_id is NOT near one of these exact
# phrases, the mismatch is still flagged, erring toward false positives
# over risking a masked real bug.
NEGATION_EXCLUSION_PHRASES = (
    "not carried forward",
    "not re-asserted",
    "not reused",
    "not being reused",
    "precedent set for",
    "rather than merged into",
    "not merged into",
)

# how many characters before/after a named signal_id mention to scan for one
# of the negation/precedent phrases above. Sized to comfortably span the
# single sentence/clause the signal_id appears in, per the 5 known false
# positives (largest observed distance was ~180 chars).
NEGATION_PROXIMITY_WINDOW = 220


def collect_signal_id_counts(all_reports: dict) -> dict:
    """report_date -> data. returns {signal_id: set(report_dates it appears in)}"""
    counts = {}
    for report_date, data in all_reports.items():
        for signal in data.get("top_signals", []):
            sid = signal.get("signal_id", "")
            if sid:
                counts.setdefault(sid, set()).add(report_date)
    return counts


def long_running_signal_ids(counts: dict, exclude_date: str = None) -> set:
    """signal_ids that have appeared in 2+ reports, optionally excluding one date
    (so a report can't count as evidence of its own signal being 'long-running')."""
    result = set()
    for sid, dates in counts.items():
        relevant = dates - {exclude_date} if exclude_date else dates
        if len(relevant) >= 2:
            result.add(sid)
    return result


def prose_fields_with_source(data: dict) -> list:
    """[(source_label, text), ...] for every prose field worth scanning."""
    fields = []
    for i, signal in enumerate(data.get("top_signals", [])):
        for key in ("index_note", "human_editor_note"):
            text = signal.get(key, "")
            if text:
                fields.append((f"top_signals[{i}].{key}", text))
    for i, text in enumerate(data.get("limitations", [])):
        if text:
            fields.append((f"limitations[{i}]", text))
    return fields


def check_report(report_date: str, data: dict, known_signal_ids: set) -> list:
    """returns a list of warning strings for this report."""
    warnings = []
    own_signal_ids = {
        s.get("signal_id", "") for s in data.get("top_signals", []) if s.get("signal_id")
    }

    for source_label, text in prose_fields_with_source(data):
        if not REUSE_CLAIM_PATTERN.search(text):
            continue
        for sid in known_signal_ids:
            if sid not in text or sid in own_signal_ids:
                continue
            idx = text.find(sid)
            window = text[max(0, idx - NEGATION_PROXIMITY_WINDOW):idx + len(sid) + NEGATION_PROXIMITY_WINDOW]
            window_lower = window.lower()
            if any(phrase in window_lower for phrase in NEGATION_EXCLUSION_PHRASES):
                # named for precedent / explicitly-not-carried-forward reasons,
                # not an actual reuse claim -- skip.
                continue
            warnings.append(
                f"{report_date}: {source_label} claims reuse/continuation and "
                f"names signal_id '{sid}', but '{sid}' does not appear in this "
                f"report's own top_signals list. Text: {text[:200]!r}"
            )
    return warnings


def main() -> int:
    check_all = "--all" in sys.argv[1:]

    dates = list_report_dates()
    if not dates:
        print("No reports found in data/reports/ -- nothing to check.")
        return 0

    all_reports = {}
    for d in dates:
        try:
            all_reports[d] = load_report(d)
        except (OSError, ValueError) as exc:
            print(f"Skipping {d}: could not load ({exc})")

    counts = collect_signal_id_counts(all_reports)

    print("Signal reuse claim check (heuristic, not a CI gate)")
    print(
        f"Scanned {len(all_reports)} reports; "
        f"{len(long_running_signal_ids(counts))} signal_id(s) appear in 2+ reports overall."
    )
    print()

    if check_all:
        targets = dates
    else:
        # most-recently-modified report file, by filesystem mtime
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(repo_root, "data", "reports")
        by_mtime = sorted(
            dates,
            key=lambda d: os.path.getmtime(os.path.join(reports_dir, f"{d}.json")),
            reverse=True,
        )
        targets = by_mtime[:1]
        print(f"Checking most-recently-modified report only: {targets[0]} (use --all for every report)")
        print()

    all_warnings = []
    for report_date in targets:
        data = all_reports.get(report_date)
        if data is None:
            continue
        # exclude the target report itself from "long-running" evidence so a
        # signal can't be considered long-running solely because of its own
        # appearance in this report.
        known = long_running_signal_ids(counts, exclude_date=report_date)
        all_warnings.extend(check_report(report_date, data, known))

    if not all_warnings:
        print("No signal-reuse-claim mismatches found in the checked report(s).")
    else:
        print(f"Warnings: {len(all_warnings)} possible mismatch(es) between reuse claims and actual top_signals:")
        for w in all_warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
