[← back to index](../CHANGELOG.md)

## 2026-07-06 ~22:45 PDT — loop run 18, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **Crawler bug found and fixed** (`docs/agent-logs/source-crawlability-check.md`):
  verifying run 17's new sources actually work found `tokyofashion.com`
  (Cloudflare-fronted) was falsely blocked — `get_robots_parser()` used Python's default
  urllib user-agent, which Cloudflare 403s on `/robots.txt`, and the parser treated that
  403 as "disallow all." Fixed to fetch robots.txt with the crawler's real user-agent —
  a general robustness fix that protects against any Cloudflare-fronted source, not just
  this one.
- **Proactive fix** (`docs/agent-logs/busy-week-readiness-run18.md`): the largest existing
  report was already close to the 4000-token response ceiling; raised `max_tokens` to
  8000 in `summarize.py` before fashion month causes a real truncation, rather than after.
- **New report** (`docs/agent-logs/real-report-2026-09-07.md`): added an 11th report
  (pre-NYFW week). Correctly declined to force-continue a prior signal once its news hook
  was exhausted.
- **Second bias-audit pass** (`docs/PROMPT_CHANGELOG.md`, `docs/agent-logs/bias-audit-run18.md`):
  confirmed with real production data that `independent_criticism` signals get "low"
  confidence far more often than `editorial` at equal corroboration counts. Clarified
  during consolidation: run 16 already fixed the formula-level gate, so this residual
  pattern is the LLM's own conservative assignment — a prompt-tuning question, not an
  unfixed bug. Also flagged that Pinterest's self-promotional trend-report pages get
  tagged identically to organic social content.
- **Doc-sync** (`docs/agent-logs/doc-sync-run18.md`): found README/PROJECT_STRUCTURE
  claimed only 7 reports when 10 actually existed — fixed to the real count (11 as of
  this run).
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (11/11 valid), `npx tsc --noEmit`, `npx next build` — all clean.

### Known gaps carried forward
- LLM confidence conservatism on `independent_criticism` may need a prompt adjustment if
  it persists — the schema-level fix already landed in run 16.
- No documentation-level distinction yet between platform-marketing and organic social
  content in the manual-sampling workflow.
- Source diversity still only partially addressed.
- Fashion month approaching — watch whether the `max_tokens=8000` increase and the
  uncapped signal count hold up under real high-volume weeks.
