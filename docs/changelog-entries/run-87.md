[← back to index](../CHANGELOG.md)

## 2026-07-10 ~14:40 PDT — loop run 87, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **New report, precedent 4 correctly applied on its earning side**
  (`docs/agent-logs/real-report-2028-01-10.md`): added an 80th report
  (Jan 4-10, 2028). A Paris menswear FW28 calendar signal correctly earned
  "high" — unlike the 2027-09-06 precedent-4 case (an aggregator reprint held
  at medium), here WWD's corroboration adds genuinely new reported detail not
  in the institutional source's own release, so `high` is honestly earned
  rather than a case needing suppression. Clean application of an existing
  precedent on its opposite, non-triggering side.
- **Resale-platform source-seeding gap closed with a rigorous, honest "none
  pass" outcome** (`docs/agent-logs/resale-source-seeding-run87.md`): verified
  all 5 domains flagged by run 86 (therealreal.com, vestiairecollective.com,
  depop.com, grailed.com, poshmark.com) against the established source-
  diversity bar. All 5 rejected: two blocked by Cloudflare JS-challenges even
  on robots.txt, three serve real content only via client-side JS with no
  static heading tags this crawler's BeautifulSoup extraction can reach.
  Correctly did not force a weak addition just because the gap was flagged —
  `DOMAIN_SECTOR_MAP` classifications remain valid for when `summarize.py`'s
  WebSearch step surfaces them incidentally.
- **Manual-sampling cadence run on its due date, honest negative continues**
  (`docs/agent-logs/manual-sampling-check-run87.md`): ran on schedule (exactly
  run 87 as tracked). Same outcome as every prior check (runs 30, 32, 41, 52,
  69, 77): Pinterest/TikTok coverage traced back to platform PR or the same
  disqualified content-mill pattern, nothing cleared the corroboration bar.
  Cadence tracking updated in place — next due ~run 97.
- **Nav/build regression sweep — clean, explicitly re-confirms run 86's fix**
  (`docs/agent-logs/nav-build-regression-run87.md`): took the run-86 false-
  alarm lesson seriously, waited for a truly clean, fully-completed rebuild
  before checking anything, and reconfirmed the 2028 year header renders
  correctly with no lock-conflict interference this time.
- **Periodic audit — clean, one timing-race non-finding**
  (`docs/agent-logs/periodic-audit-run87.md`): schema validation, field
  coverage, signal-reuse, and confidence discipline all clean. Flagged the
  cadence-tracking doc as "not yet updated" — a simple timing race (it checked
  before the manual-sampling agent's update landed in the same run), not a
  real gap; confirmed updated correctly by the coordinator at consolidation.
- Coordinator's full independent suite: verified the cadence-tracking doc's
  actual updated values, spot-checked the new report's precedent-4 reasoning
  against its real JSON data, ran `py_compile`, `validate_all_reports.py`
  (80/80 valid), `check_field_coverage.py` (0 warnings), `check_signal_reuse_
  claims.py --all` (0 warnings), a clean `rm -rf web/.next web/out` + `npm run
  build` (80/80 report pages, zero glossary warnings, RSS confirmed at 50),
  `npx tsc --noEmit`/`npx eslint .` both clean.

### Known gaps carried forward
- Resale-platform sources remain unreachable by the crawler (confirmed
  unsuitable, not just unseeded) — `summarize.py`'s WebSearch step is the only
  path these domains are currently surfaced through; this is now a settled,
  documented limitation rather than an open gap.
- A candidate 14th precedent (forecast/speculative-content exclusion,
  flagged run 86) remains open — worth attention if the pattern recurs.
- Manual-sampling cadence next due ~run 97.
- Still awaiting a human-supervised live test of `crawler.py` against real
  sources — both fixes (runs 72, 73) remain implemented and locally proven only.
- `SITE_URL` remains a placeholder domain — correctly confirmed as needing only
  a human-supplied real domain, no further autonomous work possible here.
- The underlying human-in-the-loop process gap flagged in run 50 remains open.
- `gh` CLI/CI-status check next due at run 90.
