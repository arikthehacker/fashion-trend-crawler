# Confidence + dormancy review — run 15

Ran `python src/validate_all_reports.py` (all 8 reports pass) and
`python src/audit_confidence.py` fresh across all 8 reports.

## Confidence audit

28 signals checked, 19 mismatches, **all formula-higher-than-assigned** (editors
being conservative) — none in the concerning `assigned=high, derived=low/medium`
direction. Checked the three new reports specifically:

- **2026-08-03**: 2 mismatches (`sheer-layering`, `soft-tailoring` dormancy
  checks), both assigned=low/derived=medium — not concerning.
- **2026-08-10**: 1 mismatch, `peplum-waist-revival` (assigned=low,
  derived=high, corroboration=3, 3 sectors) — editor conservatism on a
  freshly emerging signal, not concerning.
- **2026-08-17**: 1 mismatch, `peplum-waist-revival` follow-up (assigned=low,
  derived=high) — same pattern, editor still holding "low" pending
  Copenhagen-specific confirmation. Not concerning.

No corrections made; no genuinely concerning cases found.

## Dormancy check via `get_signal_status_history()`

- **sheer-layering**: 2026-05-07 (medium) -> 2026-07-06 (medium) -> 2026-08-03
  (low/declining, explicit dormancy check, human_editor_note flags it for a
  judgment call). Quiet again in 2026-08-10 and 2026-08-17 — **2 quiet windows
  since the dormancy check**, not yet the 3-window threshold used for
  off-duty-varsity's close-out.
- **soft-tailoring**: same shape — high (07-06) -> low/declining dormancy
  check (08-03) -> quiet through 08-10 and 08-17. Also 2 quiet windows, one
  short of the precedent threshold.
- **peplum-waist-revival**: only 2 appearances total (08-10 emerging, 08-17
  already declining) — too new to be a dormancy candidate.

## Conclusion

Neither a new concerning confidence case nor a signal ready for the
off-duty-varsity-style close-out exists yet. `sheer-layering` and
`soft-tailoring` are one quiet report away from meeting the 3-window
no-corroboration bar — worth checking again next run/pass. No report files or
source files were modified.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 8 reports pass, 0 failures
