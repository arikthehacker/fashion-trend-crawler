# Confidence review — run 11

Ran `python src/validate_all_reports.py` (all 5 reports pass, no WARNING lines
printed) and `python src/audit_confidence.py` fresh against all 5 reports in
`data/reports/` (added since the last audit: 2026-07-20, 2026-07-27).

## Result

15 mismatches total, all in the **formula-says-higher-than-assigned** direction
(same pattern as `confidence-audit.md`'s "not concerning" bucket). None are in
the concerning direction (assigned="high", derived="medium"/"low").

Specifically checked the two new reports named in the task:
- **2026-07-20** (includes the Poetcore addition): 7 mismatches, all
  formula-higher-than-assigned, including the new `"Poetcore" literary/
  dark-academia-adjacent aesthetic` signal (assigned "low", derived "medium" —
  single-sector social signal, editor was appropriately conservative, not
  concerning).
- **2026-07-27**: 1 mismatch, `"Off-Duty Varsity" jersey styling, post-
  tournament check` (assigned "low", derived "medium") — same pattern, not
  concerning.

The one previously-concerning case, `Resale/secondhand retail growth`
(2026-07-13), does not reappear — it was resolved in the prior pass
(`confidence-resolution.md`) and remains resolved.

## Conclusion

No new "assigned high, derived low/medium" cases exist. No corrections were
needed. No report files were modified in this pass.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 5 reports pass, 0 failures
