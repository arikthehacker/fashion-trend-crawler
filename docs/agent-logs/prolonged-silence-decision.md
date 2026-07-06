# Prolonged-silence decision

TODO.md asked whether repeated carry-forward of an unresolved question (CFDA
Fashion Fund winner, 4 windows now) should eventually get different treatment
than mechanically restating "still open."

## Decision

No new schema field or status enum. `human_editor_note`/`index_note` free
text already carries this content fine, as run-21's report demonstrates.

Added one helper to `src/report_schema.py`: `is_prolonged_silence(signal_id,
all_reports, threshold=4) -> bool`. Same shape/spirit as
`get_signal_status_history()`: it's a thin wrapper computing an on-demand
observation across report history, not a stored property of a single
signal entry. It just counts how many entries `get_signal_status_history()`
returns and compares to `threshold`, so report-writing agents get an
explicit yes/no instead of eyeballing "is this the 4th window" by hand
each time.

Explicitly did not add a status field because:
- "awaiting resolution" is exactly the kind of cross-report-derived label
  `get_signal_status_history()`'s docstring already argues against
  hardcoding (see the dormancy precedent) — it'd desync from reality the
  same way a static field would.
- `VOLATILITY_LABELS` isn't the right vocab for this either: volatility
  describes trend direction/noise of the signal's *content*, not the
  age of an unresolved open question — conflating them would blur two
  different things validate_report() currently keeps separate.
- The distinction from dormancy is real and worth keeping explicit:
  dormancy = a signal stopped appearing; prolonged silence = a signal
  keeps appearing, explicitly re-asserted as still open. Docstring on the
  new function calls this out directly so future readers don't conflate
  the two mechanisms.

## Verification

- `python -m py_compile src/*.py` — passed.
- Ran `is_prolonged_silence()` against real `data/reports/*.json`:
  `cfda-vogue-fashion-fund-2026-winner` has 4 history entries → returns
  `True`. Two other CFDA-related signal_ids (`cfda-fur-free-policy-in-effect`,
  `cfda-vogue-fashion-fund-2026-finalists`) have only 1 entry each →
  correctly `False`.

Only `src/report_schema.py` was touched. Not committed, per instructions.
