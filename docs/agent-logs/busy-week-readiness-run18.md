# Busy-week readiness (run 18)

**Question:** is `summarize.py`'s `max_tokens=4000` (raised from 2000 in run 8)
enough for a genuinely busy fashion-week report (NYFW Sept 8, 2026 onward, per
`docs/EDITORIAL_CALENDAR.md`) with 10-15+ signals, vs. the 1-8 signals seen so far?

**Method:** measured the two largest existing reports.

- `2026-07-20.json`: 8 signals, full JSON 17,316 bytes; `top_signals` array
  alone is 13,136 bytes (~1,642 bytes/signal average).
- `2026-08-31.json`: 3 signals, 9,631 bytes.

At a conservative ~4.5 chars/token for punctuation-heavy JSON, the 8-signal
report's model-generated content (stripping post-hoc fields like
`content_hash`) lands close to ~3,800-3,900 tokens of completion -- already
near the 4000 ceiling with almost no headroom, despite only 8 signals.

**Extrapolation to 15 signals:** ~15 x 1,642 bytes = ~24,600 bytes for
`top_signals` alone, plus ~3,000-4,000 bytes of fixed overhead (executive
summary, keyword/garment/color lists, limitations) = ~28,000 bytes total,
which is roughly **6,000-6,500 tokens** at the same ratio. That's 50-60% over
the current 4000 limit and would very plausibly truncate mid-JSON during
fashion month, exactly the failure mode run 8 already fixed once at lower volume.

**Conclusion:** the current 4000 limit is not safely enough headroom for a
busy fashion-week window. Raised `max_tokens` from 4000 to 8000 in
`src/summarize.py` (comment added at the call site explaining the math).
8000 gives ~2x margin over the 15-signal extrapolation.

**Schema cap check:** `report_schema.py::validate_report()` has no hard cap
on `len(top_signals)` -- it only validates required keys and enum values
per-signal. A busy week producing 15+ signals will not be rejected by schema
validation. No change needed there.

Verified with `python -m py_compile src/*.py` (passes).
