# Periodic audit — run 72

1. `py_compile src/*.py` — PASS, no errors.
2. `validate_all_reports.py` — PASS. 64/64 reports valid. 1 non-blocking confidence WARNING: `2027-05-17.json` Dior Cruise 2027 signal assigned `high` but `derive_confidence()` suggests `medium` (corroboration_count=6, single sector `editorial`) — flagged for editor review, consistent with prior runs' single-sector-corroboration caution pattern, not a new bug.
3. `check_field_coverage.py` — PASS, 0 warnings. All 35 scanned fields typed/referenced except `confidence_source` (backend-only by design, expected).
4. `check_signal_reuse_claims.py --all` — Matches the known stable baseline exactly: 4 warnings, dated 2026-09-14, 2026-09-28, 2026-10-05, 2027-06-28. All are the documented negation/precedent-mention false-positive pattern ("is not carried forward," "continuing-but-quiet... not re-asserted," "reuses the signal_id introduced on..."). No new or different warning. No action needed.
5. Confidence-discipline spot check — reviewed the 3 most recent reports (2027-09-06 thin, 2027-09-13 thin, 2027-09-20 normal). Cross-checked every top_signal's `source_domains` against `taxonomy.py`'s `DOMAIN_SECTOR_MAP`: no signal with a domain mapping to `unclear` was assigned `high`/`medium` confidence. Clean.
6. Manual-sampling cadence — doc states cadence is "checked" every ~10 runs, last reset at run 69. Run 72 is 3 runs past reset — not overdue (7 runs of headroom remain).
7. CHANGELOG index vs changelog-entries — all linked index entries (run-00 through run-71) have a matching existing file in `docs/changelog-entries/`. Run 13's index entry deliberately has no link (its changelog was folded inline into the index itself, per its own entry text — no `run-13.md` file exists, and none is expected). Index order is correctly descending (71 → 00), no duplicate or skipped run numbers found.

Secret safety: confirmed `bool(os.environ.get("ANTHROPIC_API_KEY"))` = False; no key/`.env` contents printed.

## Summary
All 7 checks pass. No genuine new findings — everything observed matches expected/known baselines (the single derive_confidence WARNING and the 4 signal-reuse false positives are both previously-documented, stable patterns, not regressions).
