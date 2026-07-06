# Met Gala 2027 structured signal tracking — run 57

Per run 56's finding: Met Gala 2027's five-window coverage gap
(2027-05-03 through 2027-05-31) was tracked only as free text
(`limitations`/`archive_tags`), never as a `top_signals` entry with a
`signal_id`, so dormancy tooling structurally couldn't see it.

## What was done

Added a real `Signal` to `data/reports/2027-05-31.json` (the most
recent/fifth window) with `signal_id: "met-gala-2027-coverage-gap"`,
`confidence: "low"`, `volatility: "declining"`,
`origin_classification: "editorial_amplified"`, `evidence`/`index_note`
summarizing the actual five-window search history, and a
`human_editor_note` stating explicitly what this does and doesn't fix
(see below). Saved via `save_report(revision_reason=..., corrected_at=
"2027-06-01")`, which correctly required and recorded a
`revision_history` entry since the file's content_hash changed.

The four earlier reports (2027-05-03 through 2027-05-24) were
deliberately left untouched — no `signal_id` backfilled — per
instructions, so the archive doesn't misrepresent when structured
tracking actually began.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 49 reports pass (same
  one pre-existing non-blocking Dior Cruise confidence WARNING as prior
  runs, unrelated to this change)
- `get_signal_status_history("met-gala-2027-coverage-gap", all_reports)`
  → **1 entry** (2027-05-31 only)
- `is_prolonged_silence("met-gala-2027-coverage-gap", all_reports)` →
  **False**

## Does this achieve the stated goal? Honest answer: partially, not fully

This makes the gap *structurally trackable going forward* — it's now a
real signal_id that future reports can reuse, and any future agent
reading this report sees a proper Signal object instead of buried
prose. That part is a genuine improvement.

But it does **not** make `is_prolonged_silence()` detect the historical
five-window pattern. That function (and `get_signal_status_history()`
underneath it) counts occurrences of a `signal_id` *across reports*,
by design (see their docstrings in `src/report_schema.py`) — dormancy/
prolonged-silence is treated as a cross-report recurrence property, not
something a single report's signal can assert on its own. Since only
one report now carries this signal_id, the history has length 1, and
`is_prolonged_silence()` (threshold=4) correctly returns `False` — even
though the real-world gap is already five windows long and would
clearly qualify if the id had existed from the start.

This is the direct, expected consequence of the "don't backfill the
four earlier reports" instruction, and that instruction is correct:
retroactively injecting the same signal_id into 2027-05-03 through
2027-05-24 would fabricate the appearance that structured tracking
existed from window one, which it didn't. The honest fix instead is
prose (now in this report's `human_editor_note`/`evidence`/
`index_note`, and in this log) stating the five-window pattern plainly,
plus reusing `met-gala-2027-coverage-gap` in subsequent reports so the
tooling accumulates real history from this point forward. No further
schema change is needed — this is the same shape of gap CFDA Fashion
Awards had before it got a real entry, and CFDA's own history also
only started accumulating from the report where it was first added.

## Follow-up for future runs

Reuse `met-gala-2027-coverage-gap` as the `signal_id` in the next
report (2027-06-07 or whenever the following window lands), whether the
gap continues or resolves, so `get_signal_status_history()` starts
building real cross-report history. Once it's present in 4+ reports and
still unresolved, `is_prolonged_silence()` will correctly flag it and
the section-10 "untracked going forward" convention can be applied on
its own merits at that point, rather than being asserted prematurely
here.

No commits made, per instructions.
