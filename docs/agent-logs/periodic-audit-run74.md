# Periodic audit — run 74

1. `python -m py_compile src/*.py` — PASS, no output.
2. `validate_all_reports.py` — 66 reports, all pass schema validation. 1 non-blocking confidence WARNING: 2027-05-17.json "Dior Cruise 2027 at LACMA" assigned 'high' but derive_confidence() supports only 'medium' (corroboration_count=6, source_sectors=['editorial']). Pre-existing, not new to this run — flagged for editor review as usual, not treated as a bug.
3. `check_field_coverage.py` — 35 fields scanned, 0 warnings (only `confidence_source` unrendered, documented as a legitimate backend-only field).
4. `check_signal_reuse_claims.py --all` — 4 warnings, dates match the known stable baseline exactly: 2026-09-14, 2026-09-28, 2026-10-05, 2027-06-28. All negation/precedent-mention pattern, previously verified non-bugs. No new or different warnings.
5. Confidence-discipline spot check (3 most recent reports: 2027-09-20, 2027-09-27, 2027-10-04): correctly applied both directions.
   - 2027-09-20 held the Margiela signal at manual 'medium' because 2 of 4 corroborating domains (papermag.com, thefashionlaw.com) map to 'unclear' — correctly not counted as real cross-sector corroboration.
   - 2027-09-27 raised the same signal_id to derived 'high' once all 3 corroborating domains (dazeddigital.com, highsnobiety.com, whowhatwear.com) were genuinely mapped sectors — no unclear-domain inflation.
   - 2027-10-04 correctly split two distinct signals: the runway/social signal earned derived 'high' (all three domains genuinely mapped, two distinct sectors), while the separate retail-buy signal was held at manual 'medium' because one of its two domains (thefashionlaw.com) maps 'unclear'.
   No naive inflation or reflexive suppression found in any of the three.
6. Manual-sampling cadence (`docs/manual-sampling-workflow.md` + `docs/changelog-entries/run-69.md`): reset at run 69, run 74 is 5 runs after — roughly halfway through the ~10-run cadence, not overdue.
7. Cross-checked every domain in `src/crawler.py`'s `FASHION_SOURCES` against `src/taxonomy.py`'s `DOMAIN_SECTOR_MAP`: vogue.com, whowhatwear.com, hypebeast.com, nataal.com, okayafrica.com, fashionunited.in, tokyofashion.com, vogue.mx, tribune.com.pk, savoirflair.com, dewimagazine.com, scmp.com, dieworkwear.com, ffw.com.br — all 14 seeded domains have an explicit, sensible sector classification (mostly `editorial`, plus `retail` for whowhatwear.com and `independent_criticism` for dieworkwear.com). No seeded source silently falls through to 'unclear'. Genuine clean result — no gap found in this new structural check.
8. `data/reports/*.json` file count: 66, matches `validate_all_reports.py`'s reported count of 66 exactly. No drift.

**Secret safety:** confirmed `bool(os.environ.get("ANTHROPIC_API_KEY"))` == `False` only; no `.env` contents or key values printed or inspected.

**Overall: genuine all-clean.** No new actionable findings. The only pre-existing item is the already-tracked 2027-05-17 confidence warning (check 2), unchanged from prior runs. Check 7 (new structural crawler/taxonomy cross-check) also came back clean — worth keeping in the standing rotation since it would have caught the fhcm.paris-style gap noted in run 69 if it existed again.
