# Skill doc refresh 2 (post run-12)

Updated `.claude/skills/ari3lla-index/SKILL.md` only.

## File map corrections
- Added `web/app/search/page.tsx` + `SearchClient.tsx` (facet filter over source sector,
  confidence, volatility; Pagefind full-text deferred).
- Noted `reports.ts` now exposes `getSearchIndex()` for `/search`.
- Noted `report_schema.py`'s new `get_signal_status_history(signal_id, all_reports)`
  helper (trend lookup, not a static dormancy label).
- Noted `taxonomy.py`'s run-12 domain-coverage expansion for designer_origin,
  visual_archive, independent_criticism, institutional.
Verified against actual tree via `web/app/`, `src/*.py`, `docs/` globs — no other gaps
found.

## Common next steps
Rewrote to point at `TODO.md` as authoritative and surface run-12 status:
1. `trends.ts` retirement/homepage rebuild — still pending human sign-off
   (`docs/agent-logs/trends-ts-fate-proposal.md`), 2 runs old, genuinely blocked not
   neglected.
2. `off-duty-varsity` dormancy — checked `data/reports/2026-07-20.json` directly: **a
   concurrent agent this run already resolved it**, appending a `revision_history` entry
   (`corrected_at: 2026-08-10`) that closes the signal out using
   `get_signal_status_history()` to confirm the quiet trend. Updated the skill doc to
   reflect resolution rather than repeating the stale "still open" framing from the
   health check.
3. Surfacing "N consecutive thin weeks" as its own pattern, per the run-12 health check —
   still open, noted as preferred over mechanically adding an 8th report.

No other files touched; no commit made.
