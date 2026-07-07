#############################################################
# check_field_coverage.py
# standalone, read-only heuristic check that enumerates every field
# name declared on the Report and Signal dataclasses (report_schema.py)
# and greps the Next.js frontend to see whether each field is (a) typed
# in web/lib/reports.ts and (b) referenced anywhere in a web/app/**/*.tsx
# file.
#
# Why this exists: three consecutive agent-log sweeps (runs 21, 23, 24 --
# see docs/agent-logs/transparency-field-sweep-run24.md) independently
# found schema fields that were populated with real data and had a
# transparency claim made about them on the site, but were never actually
# rendered anywhere. TODO.md flagged that this needed a structural,
# automatable check instead of relying on someone remembering to sweep
# again by hand.
#
# This is a rough heuristic, not a precise static analysis:
#   - "typed in TS" is a plain substring/regex search for the field name
#     inside web/lib/reports.ts -- it doesn't parse the TS AST.
#   - "referenced in .tsx" is a plain substring search across every
#     web/app/**/*.tsx file -- it will count a field as "referenced" even
#     if it only appears in a comment, a different field with the same
#     name, or JS that reads but never renders it. It will also correctly
#     have false negatives for fields that are legitimately backend-only
#     (e.g. confidence_source, content_hash) -- those are NOT bugs, they
#     are deliberate internal/provenance metadata. A human (or an agent
#     doing a periodic sweep) still has to look at the warning list and
#     decide which flagged fields are real gaps vs. legitimate
#     backend-only fields.
#
# Does not mutate report_schema.py or any frontend file. Exit code is
# always 0 -- this is an informational report, not a CI gate, same spirit
# as audit_confidence.py.
#
# usage: python src/check_field_coverage.py
#############################################################

import dataclasses
import os
import re

from report_schema import Report, Signal

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_TS_PATH = os.path.join(REPO_ROOT, "web", "lib", "reports.ts")
APP_DIR = os.path.join(REPO_ROOT, "web", "app")

# fields confirmed backend-only by prior manual sweeps -- excluded from the
# warning list so this script doesn't re-flag known-good decisions every
# time it runs. see docs/agent-logs/transparency-field-sweep-run24.md and
# earlier sweep logs for the rationale behind each entry.
KNOWN_BACKEND_ONLY_FIELDS = {
    "confidence_source",  # internal provenance: manual vs. derive_confidence()
    "content_hash",       # fixity checksum, not editorial content
}


def collect_dataclass_fields() -> list:
    names = []
    for dc in (Report, Signal):
        for f in dataclasses.fields(dc):
            names.append((dc.__name__, f.name))
    return names


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def find_tsx_files(app_dir: str) -> list:
    tsx_files = []
    for root, _dirs, files in os.walk(app_dir):
        for fname in files:
            if fname.endswith(".tsx"):
                tsx_files.append(os.path.join(root, fname))
    return sorted(tsx_files)


def field_pattern(field_name: str) -> re.Pattern:
    # word-boundary match so e.g. "type" doesn't match inside "prototype"
    return re.compile(r"\b" + re.escape(field_name) + r"\b")


def main() -> int:
    fields = collect_dataclass_fields()

    reports_ts_text = read_text(REPORTS_TS_PATH) if os.path.exists(REPORTS_TS_PATH) else ""
    tsx_paths = find_tsx_files(APP_DIR)
    tsx_texts = {p: read_text(p) for p in tsx_paths}

    results = []
    for dc_name, field_name in fields:
        pattern = field_pattern(field_name)

        typed_in_ts = bool(pattern.search(reports_ts_text))

        referenced_files = [
            os.path.relpath(p, REPO_ROOT).replace("\\", "/")
            for p, text in tsx_texts.items()
            if pattern.search(text)
        ]
        referenced_in_tsx = bool(referenced_files)

        results.append({
            "dataclass": dc_name,
            "field": field_name,
            "typed_in_ts": typed_in_ts,
            "referenced_in_tsx": referenced_in_tsx,
            "referenced_files": referenced_files,
        })

    print("Field coverage check (heuristic, not a CI gate)")
    print(f"Scanned {len(fields)} fields across Report/Signal against:")
    print(f"  - {os.path.relpath(REPORTS_TS_PATH, REPO_ROOT)}")
    print(f"  - {len(tsx_paths)} .tsx files under web/app/")
    print()

    header = f"{'dataclass':<10} {'field':<28} {'typed in TS':<13} {'referenced in .tsx':<20}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['dataclass']:<10} {r['field']:<28} "
            f"{'yes' if r['typed_in_ts'] else 'no':<13} "
            f"{'yes' if r['referenced_in_tsx'] else 'no':<20}"
        )

    warnings = [
        r for r in results
        if r["typed_in_ts"] and not r["referenced_in_tsx"]
        and r["field"] not in KNOWN_BACKEND_ONLY_FIELDS
    ]

    known_backend_only_hits = [
        r for r in results
        if r["field"] in KNOWN_BACKEND_ONLY_FIELDS and r["typed_in_ts"] and not r["referenced_in_tsx"]
    ]

    print()
    print(f"Warnings: {len(warnings)} field(s) typed in TS but never referenced in any .tsx")
    print("(candidates for the same 'populated but unrendered' bug pattern -- review by hand;")
    print(" some backend-only fields are legitimate, e.g. confidence_source, content_hash)")
    print()
    for r in warnings:
        print(f"  - {r['dataclass']}.{r['field']}")

    if known_backend_only_hits:
        print()
        print(
            f"({len(known_backend_only_hits)} known backend-only field(s) suppressed from "
            "warnings: " + ", ".join(sorted(r["field"] for r in known_backend_only_hits)) + ")"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
