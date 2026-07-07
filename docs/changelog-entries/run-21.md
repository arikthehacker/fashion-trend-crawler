[← back to index](../CHANGELOG.md)

## 2026-07-07 ~01:50 PDT — loop run 21, branch `ari3lla-index-loop-improvements`

5 subagents, disjoint scopes, no lost work.

- **Prompt** (`docs/PROMPT_CHANGELOG.md`, `docs/agent-logs/garment-terminology-practice.md`):
  formalized the interim garment-terminology practice from run 20's Costume Core research
  — continued signals should keep consistent terminology unless a change is genuine and
  explicitly noted.
- **Third full doc re-read finds a real granular gap** (`docs/agent-logs/doc-reread-run21.md`):
  no whole missing pages this time — a sign the doc is largely covered — but found
  `human_editor_note` was typed and substantively populated in the archive's own data yet
  never rendered anywhere on the site, despite being the concrete evidence of the
  human-in-the-loop review process the project's transparency pages describe. **Fixed by
  the coordinator**: added to the `TopSignal` type and rendered per-signal on report pages.
- **New report** (`docs/agent-logs/real-report-2026-09-28.md`): added a 14th report (MFW
  week). Caught a genuine sourcing-integrity issue — conflicting MFW dates across
  sources — and logged it as its own signal rather than silently resolving the
  discrepancy.
- **Stress test** (`docs/agent-logs/index-module-stress-test.md`): verified "THIS WEEK'S
  INDEX" against thin-week data — every field degrades gracefully, no bug found.
- **Accessibility audit** (`docs/agent-logs/accessibility-audit-run21.md`): found the
  exact run-5 heading-hierarchy bug pattern (styled `<p>` acting as a heading) recurring
  in both brand-new run-20 surfaces — fixed on the homepage's index module/signal cards
  and added proper `<dl>`/`<dt>`/`<dd>` semantics to the glossary.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (14/14 valid), `npx tsc --noEmit`, `npx next build` — all clean.

### Known gaps carried forward
- Southeast Asian source coverage remains open.
- The heading-hierarchy bug has now recurred 3 times across different pages/runs —
  worth automating the check (lint rule/pre-commit) instead of relying on periodic
  manual audits.
- No cross-link exists between `/glossary` and `/taxonomy` despite them deliberately
  splitting related content.
