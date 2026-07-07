[← back to index](../CHANGELOG.md)

## 2026-07-07 ~23:00 PDT — loop run 36, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **Source-citation tension resolved for real** (`docs/agent-logs/source-citation-resolution-run36.md`):
  added `Signal.source_domains` (bare homepage domains only) — satisfies run 35's
  citation need while structurally avoiding run 33's per-article pile-on risk, enforced
  by schema validation rather than convention alone. Deliberately schema-only this run;
  not populated or rendered yet.
- **New report, convention holding** (`docs/agent-logs/real-report-2027-01-11.md`):
  added a 29th report. Correctly stopped weekly-relitigating the untracked CFDA
  questions, and honestly logged a real Golden Globes calendar-date fact without
  fabricating coverage that doesn't exist yet.
- **Dedicated slug-curation pass** (`docs/agent-logs/slug-curation-batch-run36.md`): all
  12 over-length signal_ids from run 35 renamed across 19 files, safety-checked first
  (no hardcoded slug references anywhere).
- **IPTC metadata check finds and fixes a real bug** (`docs/agent-logs/iptc-metadata-check-run36.md`):
  `dateModified` in report JSON-LD was hardcoded equal to `datePublished`, silently
  misrepresenting corrected reports as never-modified — now correctly sourced from the
  latest `revision_history` entry.
- **Fresh CI environment verification, clean** (`docs/agent-logs/ci-fresh-verification-run36.md`):
  a genuinely fresh venv + wiped `node_modules` reinstall found no environment-assumption
  bugs. `gh` CLI still unavailable. Also incidentally caused a transient TypeScript
  hiccup for a concurrent agent (node_modules race), resolved on reverification.
- Coordinator also cleaned up a stale `eslint-disable` comment flagged in 2 consecutive
  runs, then re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (29/29 valid), `python src/check_field_coverage.py` (1 expected warning —
  `source_domains`, deliberately unreferenced this run), `npx tsc --noEmit`,
  `npx eslint .` (0 errors, 0 warnings now), `npx next build` — all clean.

### Known gaps carried forward
- The run-19 confidence-gate fix remains untested.
- `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
- `source_domains` exists but isn't populated or rendered yet — a deliberately separate
  smaller follow-up.
