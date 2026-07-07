#############################################################
# generate_archive_manifest.py
#
# Produces a manifest of this site's own /reports/[date] pages
# (URL + report_date + content_hash) for a HUMAN OPERATOR to feed
# into archive.org's Save Page Now UI or API, once the site has a
# real deployed URL.
#
# Why this exists (see docs/agent-logs/self-archival-decision-run43.md):
# CJR's "A Public Record at Risk" documents newsrooms wrongly
# assuming the Wayback Machine already covers their own published
# content, when Wayback coverage is incomplete/non-guaranteed. This
# site's dated report pages ARE its permanent record, and currently
# nothing self-archives them.
#
# This script deliberately does NOT call any Wayback/Save-Page-Now
# API. `web/lib/site.ts`'s SITE_URL is still a placeholder
# (https://ari3lla-index.example.com) -- there is no real deployed
# domain yet, and no CI/CD pipeline to run automated snapshotting
# from. Automating the actual API call now would snapshot a domain
# that doesn't resolve, which is worse than doing nothing. Once a
# real SITE_URL is set, wire this manifest into a scheduled job that
# POSTs each URL to https://web.archive.org/save/<url> (see the
# recommendation doc for exact next steps).
#
# Usage: python src/generate_archive_manifest.py [--out PATH]
# Output: JSON list of {report_date, url, content_hash} for every
# report in data/reports/, written to
# docs/agent-logs/archive-manifest.json by default.
#############################################################

import argparse
import json
import os

from report_schema import list_report_dates, load_report

DEFAULT_SITE_URL_PLACEHOLDER = "https://ari3lla-index.example.com"
DEFAULT_OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "agent-logs", "archive-manifest.json",
)


def build_manifest(site_url: str = DEFAULT_SITE_URL_PLACEHOLDER) -> list:
    """Build the manifest list. Does not fetch or POST anything --
    pure local read of data/reports/*.json."""
    manifest = []
    for report_date in list_report_dates():
        report = load_report(report_date)
        manifest.append({
            "report_date": report_date,
            "url": f"{site_url.rstrip('/')}/reports/{report_date}",
            "content_hash": report.get("content_hash"),
        })
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a manifest of this site's own /reports/[date] pages "
            "for manual Wayback Save-Page-Now submission once a real "
            "SITE_URL is deployed. Does not call any archival API itself."
        )
    )
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL_PLACEHOLDER,
        help=(
            "Base site URL to build report page links from. Defaults to "
            "the placeholder in web/lib/site.ts -- pass the real deployed "
            "domain once one exists."
        ),
    )
    parser.add_argument("--out", default=DEFAULT_OUT_PATH, help="Output JSON path.")
    args = parser.parse_args()

    manifest = build_manifest(args.site_url)

    is_placeholder = args.site_url == DEFAULT_SITE_URL_PLACEHOLDER
    output = {
        "note": (
            "PLACEHOLDER SITE_URL -- these links do not resolve. Re-run with "
            "--site-url once the site has a real deployed domain, then feed "
            "each url below to https://web.archive.org/save/<url> or "
            "https://web.archive.org/save manually (or a scheduled job)."
            if is_placeholder
            else "Feed each url below to archive.org's Save Page Now."
        ),
        "site_url_is_placeholder": is_placeholder,
        "reports": manifest,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote manifest for {len(manifest)} report(s) to {args.out}")
    if is_placeholder:
        print(
            "WARNING: site_url is still the example.com placeholder -- "
            "this manifest is not yet actionable."
        )


if __name__ == "__main__":
    main()
