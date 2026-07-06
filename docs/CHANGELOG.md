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

- **2026-07-08 ~01:30 PDT — [Loop run 38](changelog-entries/run-38.md)** — Dedicated
  slug-reference audit finds 17 more stale prose mentions run 37 missed; 31st report
  re-checks and correctly does not force a correction; build-time warning added for
  undefined glossary terms; editorial calendar gains a January menswear/couture window;
  `source_domains` extended to the per-signal history page.

- **2026-07-08 ~00:15 PDT — [Loop run 37](changelog-entries/run-37.md)** — `source_domains`
  fully wired end-to-end; 30th report catches a false lead; the report-page
  dateModified fix extended to RSS; a new glossary failure mode found (undefined terms
  silently dropped); periodic audit catches a real regression from last run's slug
  rename.

- **2026-07-07 ~23:00 PDT — [Loop run 36](changelog-entries/run-36.md)** — Resolves the
  source-citation tension with a real decision (`source_domains`, homepage-only,
  schema-enforced); completes the dedicated slug-curation pass (12 renames); IPTC check
  finds and fixes a real `dateModified` bug; fresh CI environment verification clean.

- **2026-07-07 ~21:30 PDT — [Loop run 35](changelog-entries/run-35.md)** — All 5 tasks
  tightly scoped, no stalls. 28th report exercises the "untracked going forward"
  convention for real; slug-quality check correctly stops at its scope boundary;
  archival research finds a real citation gap in tension with a prior run's removal;
  quality spot-check and Pagefind regression check both clean.

- **2026-07-07 ~20:15 PDT — [Loop run 34](changelog-entries/run-34.md)** — 27th report;
  editorial calendar addition retried successfully after last run's stall; `source_links`
  removed with real reasoning; a genuinely new honest "untracked going forward" state
  designed for factual questions that never resolve; homepage index-module concern
  verified as a non-issue.

- **2026-07-07 ~18:45 PDT — [Loop run 33](changelog-entries/run-33.md)** — CFDA Fashion
  Awards crosses the prolonged-silence threshold for real, validating the run-29 tool;
  doc-sync finds and fixes real drift (missing tool scripts, stale sample-count claims);
  source-protection research finds no real risk but flags dead TS typing; a 4th instance
  of the populated-but-unrendered bug found and fixed on the signal history page.

- **2026-07-07 ~17:00 PDT — [Loop run 32](changelog-entries/run-32.md)** — 25th report
  avoids conflating two similarly-named award shows; periodic audit closes out 2 more
  overdue dormant signals; year-end review research correctly declines an unsupported
  feature; search facets confirmed fully dynamic; manual-sampling cadence check declines
  to manufacture a signal just to hit a quota.

- **2026-07-07 ~15:30 PDT — [Loop run 31](changelog-entries/run-31.md)** — Confirms
  `human_editor_note` was the one real "populated by convention, not schema-enforced"
  gap; 24th report; resort/cruise calendar research added; full-year coherence review
  clean across 23 reports; performance check fixes a real redundant-call issue.

- **2026-07-07 ~13:50 PDT — [Loop run 30](changelog-entries/run-30.md)** — Built a
  heading-bug heuristic (honest negative result); 23rd report finds a real signal that
  was only ever tracked in prose, never as a real `signal_id`; conservative prompt audit
  correctly declines a rewrite; citation format improved; manual-sampling check finds
  `human_editor_note` was never actually a schema field — fixed properly.

- **2026-07-07 ~12:30 PDT — [Loop run 29](changelog-entries/run-29.md)** — Resolved
  prolonged-silence handling with a minimal helper, not a new field; 22nd report adds a
  genuine Black Friday signal; skill doc codifies the "documented ≠ working" lesson;
  forecast-calibration check honestly finds one concerning miscalibration; accessibility
  audit fixes a 4th instance of the recurring heading bug.

- **2026-07-07 ~11:10 PDT — [Loop run 28](changelog-entries/run-28.md)** — 21st report
  handles a 4th-window open question with a named explanation instead of repetition;
  manual sampling diversified beyond Pinterest for the first time (TikTok, compliant);
  a documented-but-never-fixed garment drift finally corrected; continuity research
  found README's run instructions were actually broken and fixed them; RSS/sitemap
  verification found and fixed a real missing-routes bug.

- **2026-07-07 ~09:50 PDT — [Loop run 27](changelog-entries/run-27.md)** — Closed out
  layered-tops-styling's 13-window dormancy; 20th report correctly avoids conflating a
  similarly-named UK award with the still-open CFDA question; added non-English source
  translation-transparency to the prompt; archive-milestone research correctly declined
  an unnecessary feature; signal-link integrity fully verified clean.

- **2026-07-07 ~08:30 PDT — [Loop run 26](changelog-entries/run-26.md)** — Resolved
  review_status/reviewed_by (rendered, real data); 19th report; periodic audit flags
  layered-tops-styling as 13-windows dormant; genuine Southeast Asian source progress
  (first local-language outlet added); fixed a real UX gap — corrections/AI-disclosure
  content had no pointer from report pages, the actual reader entry point.

- **2026-07-07 ~07:10 PDT — [Loop run 25](changelog-entries/run-25.md)** — Built a
  structural fix (`check_field_coverage.py`) for the 3-times-recurring unrendered-field
  bug; 18th report honestly logs an unresolved signal instead of fabricating; first full
  voice audit since run 10 finds nothing wrong across 14 runs of additions; fashion
  archive research validates current schema design; confidence-gate fix verification is
  an honest "still untested" result.

- **2026-07-07 ~05:50 PDT — [Loop run 24](changelog-entries/run-24.md)** — Systematic
  transparency sweep finds a third instance of the "claimed but not shown" bug pattern
  (`thin_week_note`) — fixed; de-staled README/PROJECT_STRUCTURE's report-count claims
  for good; 17th report closes out a stale signal; retrospective-format research
  correctly deferred a premature feature; CI verification honestly notes it's never
  been confirmed against real GitHub Actions.

- **2026-07-07 ~04:30 PDT — [Loop run 23](changelog-entries/run-23.md)** — 16th report
  genuinely confirms the post-fashion-month volume drop (not assumed); fixed real nav
  gaps (`/search`/`Glossary` missing from primary nav); found and fixed the corrections-
  transparency claim was actually false on the live site; confidence/dormancy review
  clean; doc-sync fixed README/PROJECT_STRUCTURE staleness again.

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
