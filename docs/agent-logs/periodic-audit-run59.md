# Periodic confidence + coverage audit — run 59

Ran across 51 reports (2027-06-14.json added by a concurrent agent since
run 58). `gh` cadence check skipped per instructions (not due until run 60).

## Confidence audit

`audit_confidence.py`: 106 signals checked, 58 mismatches. All but one are
`assigned < derived` (editor conservatism — new entries this run include
"Beaded jewelry and accessory revival," "Bubble hem / balloon skirt
revival," "Royal purple as dominant seasonal color," and the newest
`met-gala-2027-coverage-gap` occurrence, all conservative undershoots, not
concerning). The single `assigned > derived` case is again 2027-05-17.json's
Dior Cruise at LACMA signal (`assigned='high'`, `derived='medium'`,
corroboration_count=6, single sector `editorial`). Re-confirmed the
`human_editor_note` reasoning is unchanged and still sound (discrete,
photographed, celebrity-attended event corroborated by 6 independent
editorial outlets; no institutional/retail sector expected to weigh in this
fast) — no change made.

## Field coverage

`check_field_coverage.py`: 35 fields scanned, 0 warnings. Clean.

## Dormancy / prolonged-silence check

`is_prolonged_silence()` over every signal_id that has ever appeared in
`top_signals` across all 51 reports flags the same four ids as run 58:
`cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `paris-post-show-coverage-gap`. All four still
carry their "untracked going forward pending new information" close-out
language. No new gap found. The latest report's own three signals
(`bubble-hem-revival`, `royal-purple-color-trend`, and
`met-gala-2027-coverage-gap`) are not yet past the prolonged-silence
threshold.

**Met Gala cross-report history re-verification**: `met-gala-2027-coverage-gap`
now appears as a structured `top_signals` entry in exactly 2 reports
(2027-05-31 first mint, 2027-06-14 second occurrence), with the intervening
2027-06-07 report continuing it correctly as prose-only (`limitations` +
`archive_tags`), matching the established Wales Bonner/CFDA convention. The
2027-06-14 entry's `index_note`/`human_editor_note` explicitly confirms it
reuses the 2027-05-31 signal_id and even documents that a prior draft had
minted a differently-named tag instead (the run-58 bug class) before being
corrected. Confirmed correctly reused — no fix needed.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 51 reports pass (one
  non-blocking confidence WARNING, expected: the documented Dior Cruise
  override)

No commits made, per instructions.
