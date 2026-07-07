# Dormancy / prolonged-silence audit — run 91

## Purpose

Follow-up periodic audit (SKILL.md convention #10) covering the 9 reports
added to the archive since run 82 (`docs/agent-logs/dormancy-audit-run82.md`),
which last covered 74 reports. The full archive is now 83 reports. This run
checks: (a) whether any signal_id crosses `is_prolonged_silence()`'s
threshold for the first time in one of the 9 new reports without a
subsequent "untracked going forward pending new information" transition, and
(b) whether the 5 signal_ids run 82 found correctly transitioned
(`cfda-fashion-fund-winner`, `cfda-fashion-awards-2026`,
`wales-bonner-hermes-debut`, `met-gala-2027-coverage-gap`,
`paris-post-show-coverage-gap`) are still correctly marked, not regressed.

## Methodology

1. Read `docs/agent-logs/dormancy-audit-run82.md` in full for the prior
   methodology (real `get_signal_status_history()`/`is_prolonged_silence()`
   from `src/report_schema.py`, threshold=4, word-boundary regexes for
   transition/resolution language, plus manual verification of any keyword
   hit against the actual text rather than trusting the hit blindly).
2. Loaded all 83 files under `data/reports/*.json`, sorted by `report_date`.
   The 9 reports added since run 82 (report_date order 75-83) are:
   `2027-12-06, 2027-12-13, 2027-12-20, 2027-12-27, 2028-01-03, 2028-01-10,
   2028-01-17, 2028-01-24, 2028-01-31`. Run 82's coverage ended at
   `2027-11-29` (its 74th report).
3. Collected every distinct `signal_id` across the archive (100 distinct
   ids, up from 90 at run 82).
4. For each signal_id, called the real `is_prolonged_silence()` /
   `get_signal_status_history()` (threshold=4) and found the report_date of
   its 4th appearance (the crossing point). Filtered to ids whose crossing
   date falls within the 9 new reports (i.e. genuinely new crossings, not
   ones that already crossed under run 82's window).
5. Result: **zero** signal_ids cross the threshold for the first time within
   the 9 new reports. Only 10 distinct signal_ids appear in `top_signals` at
   all across the 9 new reports, and none of them reaches a 3rd (let alone
   4th) appearance within the full archive history — i.e. no signal is even
   approaching the threshold yet in this window.
6. Spot-checked the 5 previously-transitioned signal_ids across all 9 new
   reports: confirmed none of them re-appear in `top_signals` (they remain
   untracked, not re-opened), and checked `archive_tags` for their carried
   status tag.
7. Re-ran the same word-boundary regex scan used in run 82
   (`untracked going forward|untracked pending|pending new information|
   deprioritiz` for transition; `\bresolved\b|editorial close-out|
   \bclose-out\b|closed out|\bfaded\b` for resolution) across limitations,
   archive_tags, index_note, human_editor_note, and revision_history reasons
   for each new report, then manually read every hit to rule out
   false positives — repeating run 82's caution that a blob-level keyword
   match can land on a *different* signal_id's text in the same report. This
   caution paid off: an apparent "resolution" hit in `2028-01-31` on
   `cfda-fashion-fund-winner`/`cfda-fashion-awards-2026` turned out, on
   manual inspection, to be the word "faded"-adjacent language belonging to
   an unrelated signal (`dior-couture-ss28-bias-cut-column-dress`)'s
   `index_note`, not anything about the CFDA signals — a false positive of
   exactly the kind run 82 warned about, confirmed not a real hit.

Script used: `scratch_dormancy_audit_run91.py` at repo root (not committed —
temporary scratch script, left in place per task instructions; safe to
delete).

Data audited was report JSON only; no `.env` or API key values were read,
printed, or referenced at any point.

## Findings: new crossings in reports 75-83

**None.** No signal_id crosses `is_prolonged_silence()`'s threshold for the
first time anywhere in the 9 new reports. There is therefore no new
dormancy-convention question to adjudicate in this window.

## Findings: the 5 previously-transitioned signals

All 5 remain correctly marked as untracked through report 83
(`2028-01-31`), with no regression (no re-opening, no re-litigation, no
stray "still open" language):

| signal_id | status in reports 75-83 |
|---|---|
| `cfda-fashion-fund-winner` | not present in any `top_signals`; `cfda-fashion-fund-winner-untracked` tag present in `archive_tags` through `2028-01-31` |
| `cfda-fashion-awards-2026` | not present in any `top_signals`; `cfda-fashion-awards-2026-untracked` tag present through `2028-01-31` |
| `wales-bonner-hermes-debut` | not present in any `top_signals`; `wales-bonner-hermes-debut-untracked` tag carried through `2028-01-31`, unchanged since first appearing in run 82's window (2027-10-18) |
| `met-gala-2027-coverage-gap` | not present in `top_signals` or `archive_tags`/`limitations` in any of the 9 new reports — drops out cleanly, no re-litigation |
| `paris-post-show-coverage-gap` | not present in `top_signals` or `archive_tags`/`limitations` in any of the 9 new reports — drops out cleanly, no re-litigation |

## Conclusion

**No unaddressed violation of convention #10 exists in reports 75-83, and no
regression on the 5 previously-transitioned signals.** No signal_id newly
crossed the prolonged-silence threshold in this window, so there was nothing
requiring a fresh "untracked going forward pending new information"
transition. The 5 signals flagged and verified transitioned as of run 82
remain correctly untracked, with their status tags carried forward
consistently and no re-opening.

## No fix applied

Since no genuine unaddressed case was found and no regression was found, no
`save_report(revision_reason=..., corrected_at=...)` correction was made in
this run, and `python src/validate_all_reports.py` was not run for a data
change (repository report data was not modified).
`scratch_dormancy_audit_run91.py` was left at the repo root, uncommitted, as
a reusable methodology artifact for the next periodic audit. TODO.md and
CHANGELOG.md were not touched per task instructions.
