[← back to index](../CHANGELOG.md)

## 2026-07-07 ~11:10 PDT — loop run 28, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **New report** (`docs/agent-logs/real-report-2026-11-16.md`): added a 21st report. The
  CFDA Fashion Fund winner question is now open a 4th window — instead of repeating the
  same caveat, this report explicitly named the unusual duration and offered two
  non-asserted explanations rather than either giving up or fabricating a resolution.
- **Manual sampling diversified for the first time** (`docs/agent-logs/manual-sample-exercised-3.md`):
  third exercise of the workflow, first to move beyond Pinterest — used TikTok's public
  hashtag page directly (compliant per doc §31, not scraped) with independent editorial
  coverage as corroboration.
- **A documented-but-never-fixed drift, finally fixed** (`docs/agent-logs/garment-terminology-verification-run28.md`):
  `peplum-waist-revival`'s garment terminology drift, found back in run 19, was written
  up but never actually corrected. Fixed now via `revision_history`. The run-20 prompt
  fix itself has no new drift to report, but hasn't been genuinely exercised since
  post-fashion-month reports have all been scheduling signals, not garment-description
  ones.
- **Continuity research finds README's run instructions were actually broken**
  (`docs/agent-logs/continuity-planning-research.md`): `bash run.sh` fails from repo
  root since the pipeline scripts assume running from inside `src/`; the doc also never
  mentioned the `--revision-reason`/`--corrected-at` flags required to re-run against an
  existing date. Fixed by the coordinator.
- **RSS/sitemap verification finds and fixes a real bug** (`docs/agent-logs/rss-sitemap-verification-run28.md`):
  `/glossary` and `/search` were completely absent from `sitemap.xml`. RSS feed itself
  was already correct — well-formed, properly escaped, all 20 reports included.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (21/21 valid), `python src/check_field_coverage.py` (0 warnings), `npx tsc --noEmit`,
  `npx eslint .` (0 errors), `npx next build` — all clean.

### Known gaps carried forward
- The run-19 confidence-gate fix remains untested.
- `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
- Both open CFDA questions (Fashion Fund winner, Fashion Awards) remain unresolved after
  multiple windows — worth considering a different treatment for prolonged silence.
- README's operational accuracy is now fixed but worth periodically re-verifying as the
  pipeline evolves further.
