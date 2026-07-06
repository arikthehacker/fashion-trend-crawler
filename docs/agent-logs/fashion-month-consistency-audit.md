# Fashion month cross-report consistency audit (runs 19-21)

Read all five reports (2026-08-31, 09-07, 09-14, 09-21, 09-28) together, plus
`get_signal_status_history()`'s exact-match-on-`signal_id` behavior in
`report_schema.py`.

## Findings

**(a) signal_id continuity:** Deliberately non-continuous by design, not
drift. The NYFW thread renames itself at each structural change —
`nyfw-ss27-schedule-finalization` -> `nyfw-ss27-week-underway` ->
`nyfw-ss27-close` — with each report's `index_note` explicitly stating it
"resolves"/"supersedes" the prior id because the underlying fact changed
(planning -> execution -> completion), not because the same fact repeated.
Same pattern for LFW. This means `get_signal_status_history()` on any single
id only returns a partial slice of the story, but every report says so
outright, so this is a documented convention, not an inconsistency.

**(b) factual contradictions:** None found. The Pantone/"Devil Wears Prada 2"
drop (09-07), the "pending" resolutions for Thom Browne/Sabyasachi (09-14 ->
09-21), and the Milan date-range ambiguity (09-28) are all handled the same
way: state what's confirmed, state what isn't, and never backfill a
resolution from a later report into an earlier date. No date or fact asserted
in one report is contradicted by another.

**(c) confidence/volatility progression:** Coherent story in every thread
(schedule: stable -> stable -> stable through execution; DVF/Zankov:
emerging, correctly left there since no critical reception exists yet; Milan
date ambiguity: correctly low/flash rather than resolved). One real gap
found: the `back-to-school-2026-y2k-preppy` signal (08-31, medium/seasonal ->
09-07, medium/declining, explicitly flagged "close this out if it doesn't
reappear") simply vanished from the 09-14 report with no acknowledgment —
breaking the explicit non-carry-forward-note convention that the 09-21 and
09-28 reports use for every other retired signal (DVF succession, first-timer
cohort, fur-free policy, LFW eligibility change). **Fixed**: added a
`limitations` entry to `data/reports/2026-09-14.json` noting the signal's
resolution, via `save_report(revision_reason=..., corrected_at="2026-07-06")`.
This is the one substantive correction from this audit.

**(d) voice/tone:** Consistent across all five despite different authoring
agents — no first person, no hype language, systematic hedging ("pending,
not reported," "do not backfill a style verdict"), and a shared, recurring
media-integrity framing (templated trend-forecast copy in 09-14, Milan date
ambiguity in 09-28) applied the same way each time. No blog/influencer voice
slip detected.

## Verification
- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 14 reports pass schema
  validation after the fix.
