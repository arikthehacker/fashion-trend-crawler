# Manual-sampling workflow exercised a second time (2026-07-06)

Second exercise of the compliant manual social-sampling path (doc §31), proving
`docs/manual-sampling-template.md` -> `build_manual_signal()`
(`src/manual_sample.py`) -> `report_schema.save_report()` is repeatable, not a
one-off — the July 6 log (`docs/agent-logs/manual-sample-exercised.md`) had
only been exercised once per the run 8 TODO note.

**Signal**: "Poetcore" literary/dark-academia-adjacent aesthetic, sourced from
Pinterest's official Pinterest Predicts 2026 trend page
([business.pinterest.com/pinterest-predicts/2026/poetcore](https://business.pinterest.com/pinterest-predicts/2026/poetcore/)),
corroborated independently by
[WWD's coverage of the same report](https://wwd.com/fashion-news/fashion-trends/pinterest-2026-trends-cool-blue-glamoratti-poetcore-fashion-1238385199/).
Deliberately a different signal from "Off-Duty Varsity" (World Cup jersey
styling) already logged. Cited Pinterest search-growth figures: "the poet
aesthetic" +175%, "poet core" +75%, "tie accessories" +85%, "cape outfit"
+65% — Pinterest's own aggregate percentages, not independently verified
volume.

Appended to `data/reports/2026-07-20.json` (the most recent report, no
manually-sampled social signal yet), not `2026-07-13.json`. Tagged
`source_sectors: ["social"]`, `confidence: "low"`, `volatility: "emerging"`,
`origin_classification: "platform_native"`, `source_corroboration_count: 2`,
`signal_id: "poetcore-aesthetic"`.

`human_editor_note` (real judgment call): flags that "poetcore" reads more
like a relabeling of pre-existing dark-academia/grandmillennial aesthetics
under a new marketing-friendly name than a genuinely new discourse item, and
that WWD's coverage restates rather than independently verifies Pinterest's
own percentages. Recommends holding at low confidence and re-checking next
quarter for use outside Pinterest-adjacent coverage.

**Note on concurrent work**: `src/report_schema.py`'s `save_report()` was
changed mid-task by another agent (added an explicit `corrected_at` parameter
replacing the prior `data["_corrected_at"]` convention). Adjusted the call
site accordingly rather than editing the file.

**Verification**: `python -m py_compile src/*.py` passed.
`python src/validate_all_reports.py` passed for all 4 files in
`data/reports/` after the append and `content_hash` recomputation.

**Sources**: [Pinterest Predicts 2026 — Poetcore](https://business.pinterest.com/pinterest-predicts/2026/poetcore/), [WWD: Pinterest Predicts 2026: Cool Blue, Glamoratti, Poetcore & More Trends](https://wwd.com/fashion-news/fashion-trends/pinterest-2026-trends-cool-blue-glamoratti-poetcore-fashion-1238385199/)
