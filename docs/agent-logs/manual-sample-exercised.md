# Manual-sampling workflow exercised (2026-07-06)

Filled out `docs/manual-sampling-template.md` by hand for one real, current
social signal and used `build_manual_signal()` (`src/manual_sample.py`) to
construct a valid `Signal`, then appended it to the existing
`data/reports/2026-07-13.json` report's `top_signals` array (no new report file
created — signal falls inside that report's collection window).

**Signal**: "Off-Duty Varsity" sports-luxe summer uniform (jerseys + cargo
bottoms) — sourced from Pinterest's official Summer 2026 Trend Report
(newsroom.pinterest.com, dated May 26, 2026, framed as covering the season
currently underway), not a TikTok scrape, per the compliant manual-sampling
path (doc §31). Cited search-index growth figures: "World Cup jerseys" +840%,
"cargo jeans" +366%, "denim jorts outfit" +330%, "Brazil jersey outfits" +302%,
"bedazzled jorts" +212% — Pinterest's own aggregate percentages, not
independently verified.

Tagged `source_sectors: ["social"]`, `confidence: "low"`, `volatility: "flash"`,
`origin_classification: "platform_native"`, `source_corroboration_count: 1`,
`signal_id: "off-duty-varsity-sports-luxe-summer-uniform"`.

The `human_editor_note` (real judgment call, doc §18/19): flags this as
search-behavior tracking a live external event (the 2026 World Cup) rather
than a confirmed organic aesthetic shift — a percentage surge can sit on a
small base, and Pinterest doesn't publish absolute volume. Recommends holding
at low confidence, single-source, until a post-tournament re-check confirms
whether jersey-as-daily-top interest persists (real shift) or collapses
immediately after the event (event-driven noise, not a fashion trend).

**Verification**: `python -m py_compile src/*.py` passed. Loaded
`data/reports/2026-07-13.json` via `report_schema.load_report()` and ran
`validate_report()` against the full 8-signal file both before and after
`save_report()` rewrote it (which recomputed `content_hash`) — both passed.

**Source cited**: [Pinterest Summer 2026 Trend Report](https://newsroom.pinterest.com/news/summer-trend-report-2026/)
