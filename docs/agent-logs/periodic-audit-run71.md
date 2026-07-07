# Periodic audit — run 71

## 1. `python -m py_compile src/*.py`
OK — clean compile, no errors.

## 2. `python src/validate_all_reports.py`
OK: all 63 reports in `data/reports/` pass schema validation. One
non-blocking confidence WARNING (expected/recurring): 2027-05-17.json's
Dior Cruise/LACMA signal assigned `high` vs. `derive_confidence()`'s
`medium` (corroboration_count=6, single sector `editorial`) — this is the
documented deliberate editor override (discrete photographed
celebrity-attended event, re-confirmed run 70), not a bug.

## 3. `python src/check_field_coverage.py`
Clean — 0 warnings. All Report/Signal fields typed in `reports.ts` are
referenced in a `.tsx` file (only backend-only `confidence_source` is
legitimately unreferenced, as expected).

## 4. `python src/check_signal_reuse_claims.py --all`
63 reports scanned, 17 signal_ids appear in 2+ reports, 4 warnings —
count and dates match the established baseline exactly: 2026-09-14,
2026-09-28, 2026-10-05, 2027-06-28. Spot-read all four: same documented
negation/precedent-mention pattern ("is not carried forward" /
"not re-asserted" / citing a prior signal_id as precedent, not reuse).
No new or different warning. Baseline holds.

## 5. Confidence-discipline spot check (3 most recent reports)
Checked 2027-08-30 (`gucci-demna-debut-reception`), 2027-09-06
(`pfw-ss28-calendar-confirmed`), 2027-09-13
(`nyfw-ss28-schedule-still-unannounced`):

- 2027-08-30: `source_sectors=['editorial','unclear']`, assigned `medium`.
  If 'unclear' were treated as a genuine second corroborating sector,
  `derive_confidence()` would compute `high` (count>=2, 2+ distinct
  sectors) — discipline correctly holds it at `medium`.
- 2027-09-06: `source_sectors=['unclear','unclear']`, assigned `medium`,
  not upgraded to `high` despite two sectors nominally present.
- 2027-09-13: `source_sectors=['institutional','editorial']` (both real
  sectors, no 'unclear'), assigned `low` — conservative, no issue.

Discipline is being followed: none of the three naively adopt a
`derive_confidence()`-implied `high` when 'unclear' sectors (from domains
not yet in `DOMAIN_SECTOR_MAP`, e.g. imfirenzedigest.com, fhcm.paris,
laforma.club) would otherwise inflate cross-sector diversity. Consistent
with the pattern documented in runs 61-70.

## 6. Manual-sampling cadence check
`docs/manual-sampling-workflow.md`: "opportunistic" = checked at least
once every ~10 runs (cheap WebSearch pass), reset each time it's
exercised. Last exercised at run 69
(`docs/agent-logs/journalism-standards-check-run69.md` — Pinterest
Predicts / TikTok July 2026 pass, nothing cleared the independent-source
bar, a valid "checked, nothing cleared" outcome). Current run is 71, i.e.
2 runs since reset — well within the ~10-run window. Not overdue.

## Summary
All 6 checks pass. Nothing here is a new actionable finding — every
result (1 non-blocking confidence WARNING, 4 signal-reuse warnings,
0 field-coverage warnings, confidence discipline intact, cadence not
overdue) matches the previously-established, expected-clean baseline.
`ANTHROPIC_API_KEY` present: False (bool check only, no value exposed).
No files changed other than this log. No commits made.
