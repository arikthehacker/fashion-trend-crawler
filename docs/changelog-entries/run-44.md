[← back to index](../CHANGELOG.md)

## 2026-07-08 ~09:00 PDT — loop run 44, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **New report makes the checkpoint decision, not another deferral** (`docs/agent-logs/real-report-2027-03-08.md`):
  added a 37th report (Mar 2-8, 2027). Wales Bonner/Hermès hits its 8th consecutive
  unresolved window — the exact checkpoint flagged since run 41 — and this time the
  transition was actually made: marked "untracked going forward pending new
  information" per SKILL.md convention #10, with full reasoning documented. Haute
  Couture SS27 correctly kept under normal tracking (a different shape of question,
  not moved to untracked).
- **Homepage dominant-mood staleness cutoff implemented** (`docs/agent-logs/dominant-mood-staleness-cutoff-run44.md`):
  addresses run 43's flagged finding (mood carried forward ~24 weeks stale). Adds a
  12-week cutoff to `getThisWeeksIndex()` — within it, carry-forward behavior is
  unchanged; beyond it, the homepage now shows an honest "no distinct mood signal in
  recent weeks" state instead of an indefinitely stale carry-forward.
- **Dataset structured data added alongside NewsArticle** (`docs/agent-logs/journalism-standards-check-run44.md`):
  research found report pages are also dataset landing pages, a distinct schema.org
  type Google recommends marking up separately. Converted report-page JSON-LD to a
  `@graph` with linked `NewsArticle` + `Dataset` entities. Deliberately omitted
  `distribution`/`contentUrl` since no public raw-JSON download route exists yet —
  documented as a follow-up rather than a claimed-but-dead link.
- **Slug quality audit renames 4 over-length slugs, full prose sweep done upfront** (`docs/agent-logs/slug-quality-audit-run44.md`):
  found 4 slugs created since run 36 exceeding the 2-4 word convention, renamed all 4
  with a full cross-file prose grep done before considering the rename complete —
  applying run 38's lesson from the start instead of needing a follow-up pass.
- **Periodic audit clean** (`docs/agent-logs/periodic-audit-run44.md`): 44 confidence
  mismatches all editor-conservative, 0 field-coverage warnings, `gh` CLI unavailable
  (10th+ consecutive check), dormancy states all correctly held per plan.
- **Consolidation catch**: the new-report agent (run concurrently, started before the
  slug-rename agent's fix landed) used the pre-rename long slugs
  (`wales-bonner-hermes-menswear-debut-2027`, `paris-january-2027-weeks-post-show-coverage-gap`)
  in the new 2027-03-08 report — the same cross-run collision class as run 6's
  slug-mismatch bug. Caught via `grep` before committing and fixed directly via
  `save_report(revision_reason=..., corrected_at=...)`.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (37/37 valid), `npx tsc --noEmit`, `npx next build` — all clean, 102 pages generated.

### Known gaps carried forward
- The run-19 confidence-gate fix remains untested.
- `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
- Report-page Dataset JSON-LD omits `distribution`/`contentUrl` since there's no public
  raw-JSON download route — consider adding one if the underlying data is ever meant to
  be directly downloadable, not just human-readable.
