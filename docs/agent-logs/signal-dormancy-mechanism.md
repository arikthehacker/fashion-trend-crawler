# Signal dormancy mechanism

`off-duty-varsity` has been flagged dormant twice (2026-07-27, 2026-08-03) with no schema
way to record that. Considered adding `signal_status: str = "active"` ("active" /
"declining" / "dormant" / "retired") to `Signal`.

Checked `taxonomy.py` first: `VOLATILITY_LABELS` already includes `"declining"`, and the
existing vocab (`stable`, `emerging`, `seasonal`, `volatile`, `flash`, `microtrend`,
`recurring`, `revival`, `long_tail`, `saturated`, `declining`) covers trend lifecycle. But
"dormant"/"retired" aren't really properties of a single signal *entry* the way volatility
is — they're observations about a *gap in recurrence* across reports (has this signal_id
stopped showing up?). A static field on one report's Signal can't express "hasn't appeared
in N reports" — it would just be a human/LLM guess re-asserted by hand each week, which is
exactly the kind of parallel, easily-desynced field the task asked to avoid.

**Decision: no new field.** Added `get_signal_status_history(signal_id, all_reports)` to
`src/report_schema.py` instead. It walks a list of report dicts, collects every
`top_signals` entry matching `signal_id`, and returns a chronological list of
`{report_date, volatility, confidence, confidence_source}`. That trend — e.g. `volatility`
going `emerging -> stable -> declining` then simply not appearing in the last two reports —
is what an editor actually needs to decide whether to mark something dormant/retired,
rather than trusting a label that could go stale the moment nobody updates it.

This keeps `Signal`'s schema unchanged (no `validate_report()` changes needed) and is fully
backward compatible: it's a pure read-side helper over existing fields, doesn't mutate
reports, and returns `[]` if a signal_id never recurs.

Verified: `python -m py_compile src/*.py` and `python src/validate_all_reports.py` (6/6
reports pass, unchanged since no schema fields were touched).
