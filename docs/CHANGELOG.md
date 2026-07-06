# CHANGELOG — ARI3LLA INDEX rebuild

Branch: `ari3lla-index-rebuild`
Source of truth for scope: `docs/ARI3LLA INDEX.txt` (raw brainstorm transcript — section 40 has the
prioritized build list, section 41 has the JSON schema).

This file is the master **index**. Each entry below is a one-paragraph summary of a loop
run or branch-setup milestone; full detail (per-agent breakdowns, bugs found, exact file
lists) lives in its own file under `docs/changelog-entries/`. Individual per-agent working
logs are kept separately in `docs/agent-logs/*.md` for provenance (who/what changed, in the
agent's own words); the files in `docs/changelog-entries/` are the reconciled, chronological
record of what actually landed on the branch and why, just split one-file-per-run instead of
one giant file.

All timestamps are Pacific (PDT, UTC-7 — this work happened in July).

---

## Index

- **2026-07-07 ~03:10 PDT — [Loop run 22](changelog-entries/run-22.md)** — Investigated
  automating the heading-hierarchy check (honestly concluded ESLint can't catch it,
  documented a manual checklist instead); added glossary/taxonomy cross-link; 15th report
  closes out fashion month; made a real placement decision keeping the index module
  homepage-only; cross-report audit of all 5 fashion-month reports found and fixed one
  real gap.

- **2026-07-07 ~01:50 PDT — [Loop run 21](changelog-entries/run-21.md)** — Formalized the
  garment-terminology practice; a third doc re-read found `human_editor_note` was never
  rendered anywhere despite substantive data — fixed; 14th report caught a real
  sourcing-integrity issue; index module stress-tested clean; accessibility audit found
  the run-5 heading bug recurring in brand-new pages — fixed again.

- **2026-07-07 ~00:30 PDT — [Loop run 20](changelog-entries/run-20.md)** — Shipped the
  two doc-central gaps run 19 found: "THIS WEEK'S INDEX" (real derived metrics on the
  homepage) and `/glossary` (terms extracted from the actual archive). Also fixed real
  nav drift, researched Costume Core vocabulary standards (concluded not worth adopting
  yet), and added a 13th report.

- **2026-07-06 ~23:50 PDT — [Loop run 19](changelog-entries/run-19.md)** — Tuned the
  confidence-conservatism prompt; added manual-sampling marketing-vs-organic guidance; a
  12th report proved the busy-week fixes hold under real fashion-week volume; source
  diversity narrowed further; a full re-read of the original doc found two genuine
  18-run-old gaps: an unbuilt glossary page and the "THIS WEEK'S INDEX" metrics module.

- **2026-07-06 ~22:45 PDT — [Loop run 18](changelog-entries/run-18.md)** — Found and fixed
  a real crawler bug (Cloudflare 403 on robots.txt false-blocking a source); proactively
  raised `max_tokens` ahead of fashion month; added an 11th report; second bias-audit pass
  confirmed a real confidence-conservatism pattern with production data; doc-sync found
  README/PROJECT_STRUCTURE undercounting reports by more than half.

- **2026-07-06 ~21:30 PDT — [Loop run 17](changelog-entries/run-17.md)** — Expanded
  source diversity (partial fix, honestly caveated); added homepage thin-week framing;
  10th report ends the 5-week thin streak with an earned "normal" status and catches a
  likely reversed-causality claim; refreshed docs, added a reusable editorial-calendar
  reference.

- **2026-07-06 ~20:15 PDT — [Loop run 16](changelog-entries/run-16.md)** — Added a 9th
  report (5th consecutive thin week); closed out 3 dormant signals; added low-volatility
  methodology framing; first real bias audit found and fixed an inconsistent confidence
  gate; backfilled meaningful `reviewed_by` provenance; confirmed fashion month
  (~Sept 8 – Oct 6, 2026) should end the quiet stretch structurally.

- **2026-07-06 ~19:00 PDT — [Loop run 15](changelog-entries/run-15.md)** — Ran a real
  crawl to test whether the 4-thin-week streak was a WebSearch artifact — confirmed it's a
  genuine quiet period. Added soft review-status metadata; created `PROMPT_CHANGELOG.md`;
  verified Pagefind search fully works end-to-end via a real `npm install`/build;
  confidence/dormancy review found nothing new.

- **2026-07-06 ~17:45 PDT — [Loop run 14](changelog-entries/run-14.md)** — Fixed static
  export properly (real `out/` output confirmed); added `/rss.xml`; added an 8th report,
  now the 4th consecutive thin week, explicitly flagged as a streak; fixed stale
  README/PROJECT_STRUCTURE/skill-doc references; AI-journalism-standards research found
  real gaps (auditable review records, prompt versioning, bias audits).

- **2026-07-06 ~16:45 PDT — Loop run 13 homepage rewrite (approved)** — User approved
  retiring `web/lib/trends.ts`; homepage rebuilt as a masthead + latest-report teaser via
  `getLatestReport()`; deleted the 4 legacy `trends_raw.json`/`trends_summary.json` files —
  **migration step 5/5 complete**, closing the 6-run-old legacy-migration plan.

- **2026-07-06 ~16:30 PDT — [Loop run 12](changelog-entries/run-12.md)** — Shipped `/search`
  with client-side facet filtering; built a signal-dormancy history helper instead of a
  static status field; expanded taxonomy outlet coverage; added a 7th report (Copenhagen
  Fashion Week, correctly logged as pre-show forecast); a 12-run health-check audit flagged
  `off-duty-varsity`'s unresolved dormancy and a "3 thin reports in a row" pattern worth
  watching. All checks clean.

- **2026-07-06 ~15:15 PDT — [Loop run 11](changelog-entries/run-11.md)** — Proposed (not yet
  executed, needs sign-off) retiring `web/lib/trends.ts` since the homepage renders a stale
  crawl snapshot; fixed real nav-coherence drift across 5 pages; designed (not built)
  Pagefind + facet search; added a 6th report with two signals correctly downgraded on
  dormancy.

- **2026-07-06 ~14:00 PDT — [Loop run 10](changelog-entries/run-10.md)** — Wired
  `revision_reason`/`corrected_at` through `summarize.py`; found a real migration blocker —
  `web/lib/trends.ts` still reads legacy cache files, missed by every prior migration step;
  fixed a tonal voice slip on the about page; added a 5th report that honestly used
  `collection_status: "thin"` instead of padding; refreshed README/case-study to match
  actual shipped state.

- **2026-07-06 ~12:45 PDT — [Loop run 9](changelog-entries/run-09.md)** — Implemented the
  `revision_history` mechanism on `save_report()`; completed migration step 4/5
  (`test_tools.py`); exercised manual sampling a second time (Poetcore signal); added an
  explicit git-safety guardrail to the skill doc after run 8's coordination bug — no work
  lost this run.

- **2026-07-06 ~11:30 PDT — [Loop run 8](changelog-entries/run-08.md)** — Biggest-finding
  run: a live `crawler.py` + `summarize.py` run against real network/API succeeded and
  surfaced a real bug (`max_tokens=2000` truncating responses, fixed to 4000); a
  coordination bug was also found and fixed, where one agent's broad git revert silently
  wiped two other agents' concurrent work (redone from their logs). Retention/versioning
  design proposed, not implemented.

- **2026-07-06 ~10:10 PDT — [Loop run 7](changelog-entries/run-07.md)** — Added
  Corrections/Editorial-Independence/AI-Involvement disclosure sections; migration step
  2/5; added `collection_status`/`thin_week_note` schema fields for honest thin-week
  reporting; refreshed the stale skill doc; audited all signals and flagged one
  (Resale/secondhand) with confidence overstated relative to corroboration, for human
  review.

- **2026-07-06 ~09:00 PDT — [Loop run 6](changelog-entries/run-06.md)** — Implemented
  `derive_confidence()` (opt-in); migration step 1/5; curated overly long signal slugs;
  added a 4th report; fixed a cross-run consistency bug where a concurrent slug-curation
  and new-report agent produced mismatched slugs; gap analysis found no
  corrections/transparency disclosure existed anywhere on-site.

- **2026-07-06 ~07:50 PDT — [Loop run 5](changelog-entries/run-05.md)** — Fixed WCAG heading
  hierarchy; added sitemap/robots/JSON-LD SEO; added an archival "Cite as" citation line;
  wrote a detailed (unexecuted) legacy-migration plan, noting `server.py` is a real MCP
  server contract; researched confidence-scoring frameworks for run 6. Three agents
  concurrently edited the same report page file and merged cleanly.

- **2026-07-06 ~06:40 PDT — [Loop run 4](changelog-entries/run-04.md)** — Added CI
  (`validate_all_reports.py` + GitHub Actions workflow, failure path actually tested);
  exercised `manual_sample.py` for the first time (Off-Duty Varsity signal); shipped
  `/signals/[slug]` and fixity-field UI display; researched (not yet implemented)
  accessibility/SEO fixes for run 5.

- **2026-07-06 ~05:30 PDT — [Loop run 3](changelog-entries/run-03.md)** — Added
  `Signal.signal_id` slugs and backfilled them across reports; found and fixed a
  pre-existing hand-authored report that silently failed schema validation; built
  `/timeline`; tightened the summarizer prompt against Reuters attribution norms; designed
  (not yet exercised) the manual-sampling workflow.

- **2026-07-06 ~04:20 PDT — [Loop run 2](changelog-entries/run-02.md)** — Added
  fixity/corroboration schema fields; fixed missing source sectors on taxonomy/sources
  pages; corrected run 1's plan — `trends_raw.json` is live-used, not dead, so removal
  needs a real migration; researched (not implemented) signal timeline design and
  compliant social-sourcing options.

- **2026-07-06 ~03:15 PDT — [Loop run 1](changelog-entries/run-01.md)** — First loop run:
  added `TODO.md`; fixed `run.sh`'s broken crawl→summarize wiring; added the first
  WebSearch-researched dated report; fixed a first-person voice slip; folded in
  journalism/archival research; hygiene scan found no sensitive data.

- **2026-07-06 02:04–02:10 PDT — [Branch setup and overnight build](changelog-entries/run-00-branch-setup.md)** —
  Created the `ari3lla-index-rebuild` branch, removed a stray nested `.git`; dispatched 5
  parallel subagents (data pipeline/schema, frontend archive, frontend static pages +
  rebrand, README + case study, repo hygiene) that built the structural core of the
  project from scratch; consolidation pass fixed stale branding and verified full build.
  Known gaps and deliberate overnight scope cuts are listed at the end of that file.

---

For the currently open items, see `TODO.md` at the repo root (updated every loop run) —
it is the authoritative, current punch list; this file is a historical record only.
