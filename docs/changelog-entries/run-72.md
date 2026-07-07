[← back to index](../CHANGELOG.md)

## 2026-07-09 ~20:30 PDT — loop run 72, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **Crawler hang fix implemented and locally proven, still not human-tested against
  real sites** (`docs/agent-logs/crawler-hang-fix-run72.md`): applied run 71's
  drafted `ThreadPoolExecutor`-based hard-deadline wrapper to both `requests.get()`
  call sites in `src/crawler.py`, correcting one flaw in the original draft (using
  `with ThreadPoolExecutor(...)` would have re-hung on `shutdown(wait=True)`; fixed
  to `shutdown(wait=False)`). Proved it works with a new, safe, localhost-only unit
  test (`src/test_crawler_timeout.py`) that trickles bytes forever and asserts the
  wrapper aborts near its configured deadline — passed, independently re-run by the
  coordinator (~3.0s abort against a 3s deadline). **Real finding from independent
  verification**: the fix's leaked worker thread is non-daemon, so a process that
  hits even one timeout won't exit cleanly on its own — this is exactly the kind of
  stray-python.exe pattern this project has hit before (runs 55, 66), now traced to
  a specific cause. `crawler.py` is still NOT to be run autonomously — this is a
  code-level fix awaiting a human-supervised live test against real sources, not a
  green light to resume automated crawling.
- **New report, confidence discipline correctly NOT over-applied**
  (`docs/agent-logs/real-report-2027-09-27.md`): added a 65th report (Sept 21-27,
  2027, Paris SS28 opens). Confidence adopted at the derived "high" as-is for both
  signals since all corroborating domains map to real sectors this time — the
  discipline is to hold confidence down only when it's actually earned by an
  unclear-sector inflation, not reflexively every week.
- **Retroactive confidence review for 2027-09-06 — reviewed, correctly left
  unchanged** (`docs/agent-logs/confidence-recompute-2027-09-06-run72.md`): run 70's
  taxonomy fix (`fhcm.paris`→institutional, `laforma.club`→editorial) would
  mechanically raise `derive_confidence()`'s output for this report from medium to
  high, but the agent found the underlying fact pattern doesn't support it —
  laforma.club's coverage is an aggregator reprint of fhcm.paris's own announcement,
  not independent corroboration, regardless of correct sector labels. A sound
  "reviewed, no change needed" outcome, closing this carried-forward item without
  forcing an unearned edit.
- **Nav/build regression sweep — clean, with one real build-hygiene finding**
  (`docs/agent-logs/nav-build-regression-run72.md`): 65 report pages/157 routes
  generated; a first build without wiping `web/out` was missing the newest report
  page (stale artifact, not a code bug) — resolved with a clean wipe, and the
  coordinator's own independent rebuild confirmed all 65 report dates present.
  Recommend future sweeps default to a clean wipe before trusting build
  completeness.
- **Periodic audit — clean, plus a new CHANGELOG-integrity check**
  (`docs/agent-logs/periodic-audit-run72.md`): schema validation, field coverage,
  and signal-reuse checks unchanged from baseline; confidence discipline confirmed
  followed; manual-sampling cadence not yet overdue; new check confirmed every
  CHANGELOG.md index entry has a matching, existing changelog-entries file with
  correct descending order and no gaps/duplicates.
- Coordinator independently re-verified rather than trusting self-reports: killed a
  stray `python.exe test_crawler_timeout.py` process left running by the fix agent,
  re-ran the localhost timeout test personally, cross-checked the confidence-
  recompute agent's domain-sector claims, and did a clean `rm -rf web/.next web/out`
  rebuild to confirm the regression-sweep agent's stale-build finding. Full backend
  suite (`py_compile`, `validate_all_reports.py` — 65/65 valid — `check_field_
  coverage.py` — 0 warnings — `check_signal_reuse_claims.py --all` — 4 known false
  positives, unchanged) and frontend suite (`npx tsc --noEmit`, `npx eslint .`,
  `npm run build`) all clean.

### Known gaps carried forward
- `crawler.py`'s hard-deadline fix is implemented and locally proven safe, but
  leaked worker threads are non-daemon and can prevent the crawler process from
  exiting cleanly after any single-source timeout — worth a small follow-up
  (daemon threads, or an explicit `sys.exit()` after `crawl_all_sources()`
  completes) before a human live-tests it.
- Still awaiting a human-supervised live test of `crawler.py` against real sources
  — the standing "no autonomous execution" rule remains in force regardless of this
  fix.
- The manual-sampling cadence has no enforcement mechanism beyond documentation —
  worth a periodic spot-check to catch future lapses earlier.
- `SITE_URL` remains a placeholder domain, blocking self-archival/citation
  correctness — still awaiting a human decision (run 50).
- The underlying human-in-the-loop process gap flagged in run 50 remains open.
- `gh` CLI/CI-status check next due at run 80.
