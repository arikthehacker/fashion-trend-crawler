[← back to index](../CHANGELOG.md)

## 2026-07-08 ~00:15 PDT — loop run 37, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **`source_domains` fully wired** (`docs/agent-logs/source-domains-wiring-run37.md`):
  `summarize.py`'s prompt now populates it, reusing the existing domain-extraction
  convention; report pages render it per-signal. Confirmed typed+referenced by
  `check_field_coverage.py`.
- **New report catches a false lead** (`docs/agent-logs/real-report-2027-01-18.md`):
  added a 30th report. Found genuine, corroborated pre-show discourse (a real designer
  succession announcement) while catching and excluding previously-occurred debuts that
  search results had mislabeled as new January 2027 news.
- **RSS feed had the same freshness bug as report pages** (`docs/agent-logs/rss-freshness-check-run37.md`):
  the `<pubDate>` never checked `revision_history` for corrections, same pattern just
  fixed run 36 — now consistent across both surfaces.
- **A genuinely new glossary failure mode found** (`docs/agent-logs/glossary-freshness-check-run37.md`):
  terms without a curated definition were silently dropped entirely, rather than shown
  with any fallback — distinct from the "populated but unrendered" bug class (this was
  "present in data but invisible due to missing curation"). Fixed for the specific term
  found.
- **Periodic audit catches a real regression from last run's own work** (`docs/agent-logs/periodic-audit-run37.md`):
  run 36's slug-shortening left 2 stale long-form signal_id references in report prose,
  which would have silently broken `get_signal_status_history()` lookups. Fixed.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (30/30 valid), `python src/check_field_coverage.py` (0 warnings), `npx tsc --noEmit`,
  `npx eslint .` (0 errors), `npx next build` — all clean.

### Known gaps carried forward
- The run-19 confidence-gate fix remains untested.
- `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
- Future slug renames should include a dedicated grep-for-old-name pass across all prose
  fields, not just `signal_id` values, given this run's regression finding.
- Consider a build-time warning for glossary terms with no curated definition, rather
  than relying on periodic manual checks.
