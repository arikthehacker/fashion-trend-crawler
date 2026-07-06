[← back to index](../CHANGELOG.md)

## 2026-07-10 ~06:50 PDT — loop run 81, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **New report, a synthesis signal held to the same discipline as its
  precedent** (`docs/agent-logs/real-report-2027-11-29.md`): added a 74th
  report (Nov 23-29, 2027). A Dieworkwear essay synthesizing the opera-gloves
  thread and coining "restraint dressing" was logged as its own signal_id, with
  `derive_confidence()`'s mechanical "medium" manually overridden to "low"
  since the essay introduces no new primary sourcing — the same discipline
  established for the Bogotá thread's 2027-11-08 Dieworkwear precedent.
- **Real 5-item false-positive burden eliminated with a conservative, recall-
  preserving fix** (`docs/agent-logs/signal-reuse-checker-improvement-run81.md`):
  identified the exact literal negation/precedent-phrase pattern shared by all
  5 known false positives and added a bounded proximity-window exclusion to
  `check_signal_reuse_claims.py`. Deliberately a short, literal phrase list
  rather than general negation detection, erring toward false positives over
  risking a masked real bug. Coordinator independently re-ran the checker
  (0 warnings, down from 5) and independently simulated a genuine reuse-claim
  bug to confirm it's still caught — recall preserved, not just precision
  gained.
- **Taxonomy/sources pages: two real staleness gaps found and fixed**
  (`docs/agent-logs/taxonomy-sources-freshness-audit-run81.md`): the Sources
  page's Runway/Editorial list was frozen at the old seed set, missing 13
  currently-crawled outlets including all three recently-flagged additions
  (ffw.com.br, inexmoda.org.co, voguearabia.com); its Institutional/Historical
  framing omitted governing bodies/trade institutes that make up over half
  that sector's actual domains. The Taxonomy page was missing the entire
  Origin Classification dimension — a live schema field rendered on every
  signal card but never documented anywhere. Both fixed. Confidence/Volatility/
  Source Sector tables confirmed already accurate, no change needed there.
- **Nav/build regression sweep — clean** (`docs/agent-logs/nav-build-regression-run81.md`):
  181 routes; all prior fixes (RSS cap, JSON-LD, `<h3>` wrap, recency-status
  line) confirmed intact; correctly distinguished a concurrent agent's
  in-progress glossary gap from a real regression.
- **Periodic audit — clean, API-key check confirmed fixed**
  (`docs/agent-logs/periodic-audit-run81.md`): schema validation, field
  coverage, source/taxonomy cross-check, and confidence discipline (including
  run 80's same-week-co-occurrence discipline) all clean. `ANTHROPIC_API_KEY`
  check via the run-80-established single-invocation method correctly returned
  `True` — the fix holds on first re-use.
- Coordinator's full independent suite: read the signal-reuse checker diff in
  full before accepting it, independently re-ran the checker (0 warnings) and
  wrote a standalone recall test (a simulated reuse-claim bug with no negation
  phrase nearby, still correctly flagged), reviewed the sources/taxonomy page
  diffs, ran `py_compile`, `validate_all_reports.py` (74/74 valid),
  `check_field_coverage.py` (0 warnings), a clean `rm -rf web/.next web/out` +
  `npm run build` (74/74 report pages, zero glossary warnings, RSS confirmed
  still capped at 50), `npx tsc --noEmit`/`npx eslint .` both clean.

### Known gaps carried forward
- The signal-reuse checker's known false-positive baseline is now 0 (previously
  5) — future runs should expect a clean run by default and treat ANY new
  warning as worth reading carefully, since the safety net for genuine bugs is
  now more sensitive with fewer known-noise entries to filter out mentally.
- Manual-sampling cadence next due ~run 87.
- Still awaiting a human-supervised live test of `crawler.py` against real
  sources — both fixes (runs 72, 73) remain implemented and locally proven only.
- `SITE_URL` remains a placeholder domain — correctly confirmed as needing only
  a human-supplied real domain, no further autonomous work possible here.
- The underlying human-in-the-loop process gap flagged in run 50 remains open.
- `gh` CLI/CI-status check next due at run 90.
