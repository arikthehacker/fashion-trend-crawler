# Periodic confidence + coverage audit — run 60

Ran across 52 reports (2027-06-21.json added by a concurrent agent since
run 59). `gh` cadence check explicitly skipped this run — covered by a
concurrent agent per instructions.

## Confidence audit

`audit_confidence.py`: 109 signals checked, 61 mismatches. All but one are
`assigned < derived` (editor conservatism — new entries this run include
"Blokecore / soccer jersey styling wave," "Tomato red as dominant seasonal
color," and the third `met-gala-2027-coverage-gap` occurrence, all
conservative undershoots, not concerning). The single `assigned > derived`
case is again 2027-05-17.json's Dior Cruise at LACMA signal (`assigned='high'`,
`derived='medium'`, corroboration_count=6, single sector `editorial`).
Re-confirmed the `human_editor_note` reasoning is unchanged and still sound
(discrete, photographed, celebrity-attended event corroborated by 6
independent editorial outlets; no institutional/retail sector expected to
weigh in this fast) — no change made, no `save_report()` revision needed.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean, unchanged
from run 59.

## Dormancy / prolonged-silence check

Focused check on `met-gala-2027-coverage-gap` per instructions, using
`get_signal_status_history()`/`is_prolonged_silence()`:

```
2027-05-31  volatility=declining  confidence=low
2027-06-14  volatility=declining  confidence=low
2027-06-21  volatility=declining  confidence=low
is_prolonged_silence(...) -> False
```

It now has 3 structured `top_signals` occurrences (2027-05-31, 2027-06-14,
new this run 2027-06-21). `is_prolonged_silence()`'s threshold is 4
consecutive structured occurrences, so this signal has **not yet** crossed
the threshold — still one occurrence short. Noting clearly per instructions,
but no "untracked going forward" transition is warranted yet; that decision
is for whichever run first sees a 4th occurrence.

The other four previously-flagged prolonged-silence ids
(`cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `paris-post-show-coverage-gap`) are unchanged
from run 59, still carrying their close-out language. No new gap found.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 52 reports pass (one
  non-blocking confidence WARNING, expected: the documented Dior Cruise
  override)

No commits made, per instructions.
