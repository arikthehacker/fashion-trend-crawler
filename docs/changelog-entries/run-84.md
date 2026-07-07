[← back to index](../CHANGELOG.md)

## 2026-07-10 ~11:00 PDT — loop run 84, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **Both run-83 flagged confidence-precedent inconsistencies resolved — as
  corrections, not new precedents** (`docs/agent-logs/confidence-precedent-resolution-run84.md`):
  made an actual, evidenced decision rather than deferring further. For
  `dior-cruise-2027-lacma-debut` (2027-05-17), found precedent 2's own worked-
  example list already contains a directly on-point counter-case
  (`chanel-cruise-2027-biarritz-debut`, 2027-05-03 — a materially identical
  discrete single-day Cruise debut) held at medium without exception two weeks
  earlier; formalizing the proposed exception would let any well-covered
  single event retroactively exempt itself from precedent 2. For
  `couture-fw27-debuts-reception` (2027-07-12), found the "backward-looking
  confirmed vs. forward-looking anticipation" argument doesn't actually engage
  precedent 3's mechanism (the unmapped domains stay `unclear` regardless of
  event timing), and is directly inconsistent with the immediately preceding
  week's identical sector mix held at medium. Both corrected `high` → `medium`
  via `save_report()`, exercising run 82's `changed_signals` provenance
  feature for real for the first time — coordinator independently confirmed
  both revision entries correctly recorded `modified: {signal_id: ["confidence",
  "human_editor_note"]}`.
- **New report, a genuinely novel case correctly not forced into an existing
  precedent** (`docs/agent-logs/real-report-2027-12-20.md`): added a 77th
  report (Dec 14-20, 2027). A cross-sector Dior/Vogue signal correctly earned
  "high" mechanically; a single-source resale-platform signal (The RealReal)
  didn't cleanly match any of the 12 documented precedents, so the agent left
  the mechanical "low" output as-is and flagged the resale-platform-reliability
  question as a candidate for future precedent formalization rather than
  inventing a silent exception — exactly the discipline run 83's audit was
  looking for.
- **Archive year-grouping change independently re-verified — clean**
  (`docs/agent-logs/archive-regression-check-run84.md`): confirmed all 76 (at
  the time) reports appear exactly once with correct year-boundary placement
  and strict newest-first ordering; confirmed `lib/reports.ts` (shared by
  glossary/RSS) was untouched by the UI-only change, so no downstream impact
  possible.
- **Nav/build regression sweep — clean** (`docs/agent-logs/nav-build-regression-run84.md`):
  187 routes; all prior fixes including run 83's year-grouping headers intact.
- **Periodic audit — clean** (`docs/agent-logs/periodic-audit-run84.md`):
  correctly recognized the confidence-resolution work hadn't landed yet at the
  moment it ran rather than treating that as a gap; all other checks clean.
- Coordinator's full independent suite: read both corrected reports' actual
  JSON and confirmed the `changed_signals` diff populated correctly, ran
  `py_compile`, `validate_all_reports.py` (77/77 valid — **the long-standing
  2027-05-17 confidence warning is now fully resolved**), `check_field_
  coverage.py` (0 warnings), `check_signal_reuse_claims.py --all` (0 warnings),
  a clean `rm -rf web/.next web/out` + `npm run build` (77/77 report pages,
  zero glossary warnings, RSS confirmed at 50), and confirmed the corrections
  banner now renders on 2027-05-17's built page reflecting the new revision.

### Known gaps carried forward
- A candidate 13th precedent (resale-platform corroboration reliability) was
  flagged by run 84's report agent but not formalized — worth a future run's
  attention if the pattern recurs enough to generalize.
- `archive_tags` remains unsurfaced as a filter on the archive page — future
  scope if the archive grows enough to need it, not a current gap.
- Manual-sampling cadence next due ~run 87 (tracked in
  `docs/manual-sampling-workflow.md`).
- Still awaiting a human-supervised live test of `crawler.py` against real
  sources — both fixes (runs 72, 73) remain implemented and locally proven only.
- `SITE_URL` remains a placeholder domain — correctly confirmed as needing only
  a human-supplied real domain, no further autonomous work possible here.
- The underlying human-in-the-loop process gap flagged in run 50 remains open.
- `gh` CLI/CI-status check next due at run 90.
