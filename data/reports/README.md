# data/reports/ — the real archive

This is the live ARI3LLA INDEX archive: one file per collection window, named
`<report_date>.json` (`report_date` == `collection_window.end`, per the convention in
`src/report_schema.py`), validated against `validate_report()`.

As of 2026-07-06 PDT this directory is **empty and being rebuilt from genuine
backdated research** — the archive's original 95 files (fictional forward dates,
2026-05-07 through 2028-04-24) were synthetic placeholder/methodology-development
content, not real trend research, and have been moved to
`data/examples/synthetic-reports/` (see that folder's README and
`docs/CHANGELOG.md` for the full reasoning).

Going forward, every file here should represent a real week, researched with real
sources (via `WebSearch`/`WebFetch` or the crawler pipeline), honestly marked
`collection_status: "thin"` when no genuine coverage exists for a window rather than
having anything fabricated to fill it — the same discipline the synthetic reports
already demonstrated, just now applied to real historical dates instead of a fictional
forward calendar.
