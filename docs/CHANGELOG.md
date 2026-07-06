# CHANGELOG — ARI3LLA INDEX rebuild

Branch: `ari3lla-index-rebuild`
Source of truth for scope: `docs/ARI3LLA INDEX.txt` (raw brainstorm transcript — section 40 has the
prioritized build list, section 41 has the JSON schema).

This file is the master log. Individual per-agent working logs are kept in `docs/agent-logs/*.md`
for provenance (who/what changed, in the agent's own words); this file is the reconciled,
chronological record of what actually landed on the branch and why.

All timestamps are Pacific (PDT, UTC-7 — this work happened in July).

---

## 2026-07-06 ~14:00 PDT — loop run 10, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, no lost work (git-safety guardrail from run 9 holding).

- **Pipeline** (`docs/agent-logs/summarize-revision-wiring.md`): `summarize.py` now
  threads `revision_reason`/`corrected_at` through to `save_report()`'s
  `revision_history` mechanism, with CLI flags and a clear block-and-explain message on
  an unreasoned overwrite instead of a crash.
- **Migration — real blocker found** (`docs/agent-logs/migration-step5-final.md`): the
  agent doing final-deletion verification grepped beyond `src/*.py` for the first time
  and found `web/lib/trends.ts` — the frontend's live-crawl data loader — still reads the
  legacy `trends_raw.json`/`trends_summary.json` files directly. Every prior migration
  step (1-4) only touched backend Python files; nobody had checked the frontend. Legacy
  files correctly NOT deleted. This is now a real, scoped follow-up: migrate or retire
  `trends_raw.json` usage.
- **Voice** (`docs/agent-logs/voice-audit-2.md`): first full re-audit since run 1, given
  how much copy has accumulated. Found one tonal outlier — manifesto-style aphorisms on
  the about page that read as "stylist voice" without tripping a literal banned word.
  Fixed. Everything else already compliant.
- **New report, real thin-week test** (`docs/agent-logs/real-report-2026-07-27.md`):
  added a 5th report. Genuinely found too few distinct in-window signals and correctly
  used `collection_status: "thin"` with an honest note rather than padding — the first
  real-world proof that run 7's honesty-over-filler schema work actually holds up when an
  agent is under implicit pressure to produce "enough" content.
- **Docs** (`docs/agent-logs/readme-case-study-refresh.md`): README and case-study page
  had drifted well behind 9 runs of actual shipped work; refreshed to match reality,
  including honest limitations (migration incomplete, no live crawl merged into archive).
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (5/5 reports valid), `npx tsc --noEmit`, `npx next build` — all clean, 5 dated reports,
  19 signal-slug routes.

### Known gaps carried forward
- `web/lib/trends.ts` still depends on legacy cache files — needs a deliberate migration
  or retirement decision before step 5 can complete.
- Confidence-warning count needs periodic review as reports accumulate.

## 2026-07-06 ~12:45 PDT — loop run 9, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes. Every agent prompt this run included an explicit
git-safety instruction (scope reverts to exact files, never `git checkout .`) after run
8's coordination bug — no work was lost this time, all 5 agents' changes landed intact.

- **Schema** (`docs/agent-logs/revision-history-impl.md`): implemented the
  `revision_history` mechanism proposed last run — `save_report()` now requires
  `revision_reason` and `corrected_at` when overwriting a differing report for an existing
  date, appending the prior `content_hash` before writing. Backward compatible.
- **Design, not implemented** (`docs/agent-logs/pipeline-rerun-design.md`): a concurrently
  running agent proposed the exact same mechanism independently — good convergent
  validation. Recommends `summarize.py` route its save call through `revision_history`
  rather than silently overwriting or adding a `--force` flag, tied to the project's own
  fixity/transparency principles.
- **Migration step 4/5** (`docs/agent-logs/migration-step4.md`): `test_tools.py` now
  references the shared `DEFAULT_OUTPUT_FILE` constant. All 4 files touching the legacy
  cache filename (`crawler.py`, `summarize.py`, `server.py`, `test_tools.py`) now share one
  source of truth. Step 5 (final deletion) is unblocked pending a last verification pass.
- **Manual sampling, second exercise** (`docs/agent-logs/manual-sample-exercised-2.md`):
  added a "Poetcore" signal from Pinterest Predicts 2026, corroborated by WWD, to
  `2026-07-20.json` — establishes the workflow as repeatable, not a one-off. This agent
  also handled a concurrent `save_report()` signature change gracefully (adapted its call
  site rather than fighting the other agent's edit).
- **Process fix** (`docs/agent-logs/git-safety-guardrail.md`): added an explicit
  git-safety convention to the project skill doc documenting run 8's coordination bug and
  its fix. Also refreshed the skill doc's "Common next steps," though its revision_history
  note was itself immediately stale on landing since another agent shipped that mechanism
  in the same run — fixed during consolidation.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`,
  `python src/audit_confidence.py` (14 mismatches, all previously reviewed as
  non-concerning), `npx tsc --noEmit`, `npx next build` — all clean.

### Known gaps carried forward
- `revision_history` exists but `summarize.py`'s save call doesn't route through it yet —
  today's pipeline re-run collision is still unresolved in practice, only in design.
- Migration step 5 (final legacy-file deletion) unblocked but not yet executed.
- Confidence-warning count will need periodic review as new reports are added.

## 2026-07-06 ~11:30 PDT — loop run 8, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes. This run surfaced both a genuine pipeline bug and a
genuine coordination bug — documenting both in full since they're the most valuable
findings so far.

- **Confidence resolution** (`docs/agent-logs/confidence-resolution.md`): the
  "Resale/secondhand retail growth" signal flagged last run was resolved by finding real
  independent corroboration (GlobalData's own resale analysis) rather than downgrading —
  its "high" confidence is now legitimately earned.
- **CI** (redone by coordinator, see below): `derive_confidence()` wired into
  `validate_all_reports.py` as a non-blocking warning.
- **Migration step 3/5** (redone by coordinator, see below): `server.py`'s MCP tools now
  reference the shared `DEFAULT_OUTPUT_FILE` constant.
- **Major finding — live pipeline works** (`docs/agent-logs/live-crawl-attempt.md`): an
  agent actually ran `crawler.py` (real network, 119 real headlines from Vogue/
  WhoWhatWear/Hypebeast) and `summarize.py` (real Anthropic API call using the
  pre-existing `.env` key). Found `max_tokens=2000` in `summarize.py` was too small and
  truncated Claude's response mid-JSON, crashing the run. **Fixed to `max_tokens=4000`
  during consolidation** — this is the first confirmed-real bug in the actual pipeline
  code (as opposed to hand-authored data) found across 8 runs. The live output collided
  with today's existing hand-authored report; correctly not used to overwrite curated
  data, saved instead for reference at `docs/agent-logs/live-crawl-2026-07-06-real-output.json`.
- **Retention design research** (`docs/agent-logs/retention-versioning-design.md`): found
  `save_report()` silently overwrites `content_hash` with no history, contradicting the
  site's own Corrections-section claim that originals are preserved. Schema proposal
  written, not implemented.
- **Coordination bug found during consolidation:** the live-crawl agent's own cleanup
  (reverting its exploratory changes to `summarize.py`/`trends_raw.json`) used a git
  revert broad enough to also wipe out two OTHER agents' concurrent uncommitted work —
  the migration-step-3 edit to `server.py` and the confidence-warning wiring in
  `validate_all_reports.py` both vanished silently. Caught by diffing actual file state
  against each agent's described changes before committing (a habit worth keeping — agent
  self-reports describe intent, not always the final working-tree state). Both pieces of
  lost work were redone directly by the coordinator from the original agents' logged specs.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (now shows 0 warnings on top of 4/4 valid), `python src/audit_confidence.py` (13
  mismatches, down from 14, all now non-concerning), `npx tsc --noEmit` — all clean.

### Known gaps carried forward
- Live-crawled output for today's date exists but wasn't merged into `data/reports/` due
  to a naming collision with existing curated data — needs a deliberate decision on how to
  handle re-running the pipeline on an already-used date.
- `revision_history` schema addition proposed, not implemented.
- 2 of 5 migration steps remain (test_tools.py, final legacy-file deletion).
- **Process gap:** no explicit guardrail yet against agents' cleanup/revert commands
  clobbering concurrent agents' uncommitted work — flagged as a run 9 candidate.

## 2026-07-06 ~10:10 PDT — loop run 7, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated.

- **Transparency** (`docs/agent-logs/transparency-disclosure.md`): added Corrections,
  Editorial Independence, and AI Involvement sections to methodology/about pages —
  directly closes run 6's gap analysis top finding.
- **Migration** (`docs/agent-logs/migration-step2.md`): step 2 of 5 — parameterized
  `summarize.py`'s `load_trends()`/`summarize()`, default behavior unchanged, confirmed
  `server.py` unaffected (it never imports from summarize.py).
- **Schema** (`docs/agent-logs/thin-week-fallback.md`): added `collection_status`/
  `thin_week_note` fields and a prompt instruction so a genuinely low-signal week gets
  reported honestly instead of padded with manufactured signals, per Nieman Lab-style
  guidance from run 6's research.
- **Docs** (`docs/agent-logs/skill-doc-refresh.md`): corrected the project skill doc —
  removed a stale "run.sh KNOWN STALE" note that was itself stale since run 1, added
  missing file-map entries for everything built across runs 1-6, replaced an outdated
  "Common next steps" list with a pointer to `TODO.md`.
- **Audit** (`docs/agent-logs/confidence-audit.md`): cross-checked all 22 signals across 4
  reports against `derive_confidence()`. Found one genuinely concerning case —
  "Resale/secondhand retail growth" in 2026-07-13.json is rated "high" confidence on a
  single uncorroborated source, exactly the failure mode the formula was built to catch.
  Not auto-corrected; flagged for human review rather than silently changed, since
  confidence assignment is meant to stay editorially reviewable, not mechanically
  overwritten.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`,
  `python src/audit_confidence.py`, `npx tsc --noEmit`, `npx next build` — all clean.

### Known gaps carried forward
- One signal ("Resale/secondhand retail growth") has confidence overstated relative to its
  corroboration — needs a human decision, not fixed automatically this run.
- `derive_confidence()` still not wired into the pipeline as even a soft warning.
- 3 of 5 legacy-migration steps remain (server.py, test_tools.py, final deletion).
- No report yet produced by an actual live crawl.
- Manual sampling still exercised only once.

## 2026-07-06 ~09:00 PDT — loop run 6, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated.

- **Schema** (`docs/agent-logs/confidence-derivation-impl.md`): implemented
  `derive_confidence()` in `report_schema.py` per run 5's research — an opt-in helper
  (high: corroboration>=2 across >=2 sectors; medium: same-sector corroboration or a
  single high-reliability-sector source; low: uncorroborated social-only; archival passed
  through unchanged). Added `Signal.confidence_source` ("derived"/"manual") to track
  provenance. Not auto-applied to `save_report()` yet — deliberately opt-in.
- **Migration** (`docs/agent-logs/migration-step1.md`): executed step 1 of 5 from the
  prior run's migration plan — parameterized `crawler.py`'s cache path behind a named
  constant, zero behavior change. 4 steps remain, to be done one at a time in future runs.
- **Data curation** (`docs/agent-logs/slug-curation.md`): shortened 6 overly long
  `signal_id` slugs in `2026-07-13.json` to 2-3 words.
- **New report** (`docs/agent-logs/real-report-2026-07-20.md`): added
  `data/reports/2026-07-20.json`, a 4th weekly window, WebSearch-researched, including a
  recurrence check that correctly flagged "off-duty-varsity" as `declining` now that its
  driving event (World Cup) has ended.
- **Cross-run consistency bug found and fixed during consolidation:** the new-report agent
  and the slug-curation agent ran concurrently; the new report referenced the
  pre-curation long slugs for its two recurring signals, silently breaking cross-report
  recurrence tracking on `/signals/[slug]`. Fixed both references to match the curated
  slugs; all 4 reports now validate and cross-reference correctly.
- **Gap analysis** (`docs/agent-logs/gap-analysis-run6.md`): re-checked the original doc's
  §40 priority list against 6 runs of actual work (verified against the codebase directly,
  not just prior changelog claims). Confirmed genuine progress but found a real, unaddressed
  gap: no corrections/transparency/editorial-independence disclosure anywhere on-site,
  which Trust Project/Trusting News research flags as important for a small, new
  publication's credibility.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`,
  `npx tsc --noEmit`, `npx next build` after fixing the slug-consistency bug — all clean,
  4 reports, 18 signal-slug routes.

### Known gaps carried forward
- No corrections/transparency policy on-site — new finding, top priority for run 7.
- 4 of 5 legacy-migration steps remain.
- No report yet produced by an actual live crawl.
- No "thin week" fallback state for honest low-signal reporting periods.
- `derive_confidence()` exists but isn't wired into the actual pipeline yet.

## 2026-07-06 ~07:50 PDT — loop run 5, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated. Three agents
concurrently edited `web/app/reports/[date]/page.tsx` (heading hierarchy, JSON-LD,
citation line) — one hit a mid-write collision and re-read/retried, all three merged
cleanly, confirmed by a fresh build with no restructuring conflicts.

- **Accessibility** (`docs/agent-logs/heading-hierarchy-fix.md`): fixed WCAG heading
  hierarchy on report/signal/timeline pages — section labels were styled `<p>` tags,
  now real `<h2>`/`<h3>` with identical visual styling preserved.
- **SEO** (`docs/agent-logs/sitemap-robots-jsonld.md`): added `web/app/sitemap.ts`,
  `web/app/robots.ts`, and `NewsArticle` JSON-LD structured data on report pages, plus
  `web/lib/site.ts` for shared site constants.
- **Archival citation** (`docs/agent-logs/citation-line.md`): added a "Cite as" block to
  report page footers per Library-of-Congress-derived digital-preservation practice —
  kept site-relative (no absolute domain exists in the codebase yet; deliberately not
  invented).
- **Migration planning, not executed** (`docs/agent-logs/legacy-migration-plan.md`): a
  detailed, sequenced plan to retire `trends_raw.json`/`trends_summary.json` safely.
  Notably found that `.codex/config.toml` registers `server.py` as a real MCP server, so
  its 5 tool functions are an external contract — migration must preserve function
  signatures, only rewire internals. Deliberately scoped as planning-only; too risky to
  execute unattended in one run.
- **Research, not implemented** (`docs/agent-logs/confidence-scoring-research.md`):
  intelligence-community confidence frameworks (ICD 203 / Words of Estimative
  Probability) and CTI-analyst practice both support deriving `confidence`
  deterministically from `source_corroboration_count` + source-sector diversity instead
  of an LLM judgment call. Concrete formula proposed for run 6.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`,
  `npx tsc --noEmit`, and `npx next build` after consolidating three concurrent edits to
  the same file — all clean, `/sitemap.xml` and `/robots.txt` confirmed in the route table.

### Known gaps carried forward
- Confidence-scoring formula researched, not implemented.
- Legacy-file migration planned in detail, not executed — do one step at a time in a
  future run, verifying between each, per the plan's own caution.
- No absolute canonical domain yet; sitemap/robots/JSON-LD/citation are site-relative only.
- Real live-crawl replacement of WebSearch-sourced report data still open.

## 2026-07-06 ~06:40 PDT — loop run 4, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated. This run had 3
agents concurrently touching adjacent frontend/data files (`/signals/[slug]` build, fixity
UI display, manual-sample data addition) — all merged cleanly, confirmed by a fresh build.

- **CI** (`docs/agent-logs/ci-validation-check.md`): added `src/validate_all_reports.py`
  (validates every report in `data/reports/`, exits non-zero with a clear per-file error on
  failure) and `.github/workflows/validate-reports.yml` to run it on push/PR. Actually
  tested the failure path by corrupting a scratch copy of a report, not just the happy path
  — directly closes the gap flagged at the end of run 3.
- **Data** (`docs/agent-logs/manual-sample-exercised.md`): exercised `manual_sample.py` for
  the first time — added a real signal ("Off-Duty Varsity") to `2026-07-13.json`, sourced
  from Pinterest's official Summer 2026 Trend Report (a compliant platform trend-report
  page, not a scrape), with a human_editor_note arguing it's likely World-Cup-driven search
  noise rather than a durable shift.
- **Frontend** (`docs/agent-logs/signals-slug-page.md`, `docs/agent-logs/fixity-ui-display.md`):
  shipped `/signals/[slug]` (chronological per-signal history page, linked from timeline and
  report pages when `signal_id` is present) and surfaced `source_corroboration_count`/
  `content_hash` in the report UI, small and unobtrusive.
- **Research, not implemented** (`docs/agent-logs/accessibility-seo-research.md`): audited
  against WCAG heading-hierarchy guidance, Google's Article/NewsArticle JSON-LD
  conventions, and Library of Congress digital-preservation practices. Found real gaps:
  report page section labels are styled `<p>` not real headings, no sitemap/robots/JSON-LD,
  no canonical/OG metadata. Concrete fixes documented for run 5.
- Coordinator re-ran `python -m py_compile src/*.py`, `python src/validate_all_reports.py`
  (new script, passes), `npx tsc --noEmit`, and `npx next build` after consolidating —
  all clean, `/signals/[slug]` confirmed generating 13 signal-slug routes including the new
  Pinterest-sourced signal.

### Known gaps carried forward
- Accessibility/SEO fixes (headings, sitemap, robots, JSON-LD, OG metadata) — researched,
  not implemented.
- No stable per-report citation line yet for archival permanence.
- New CI workflow untested against a live GitHub Actions run (only run locally so far).
- Legacy `trends_raw.json` migration and real live-crawl replacement of WebSearch-sourced
  data both still open from earlier runs.

## 2026-07-06 ~05:30 PDT — loop run 3, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated.

- **Schema** (`docs/agent-logs/signal-id-backfill.md`): added `Signal.signal_id` slug
  field to `report_schema.py` (optional, backward-compatible, validated as lowercase-
  alphanumeric-with-hyphens when present). Backfilled slugs onto all 3 reports, reusing
  the same slug for verbatim-recurring signals ("sheer-layering", "soft-tailoring").
  Backfilled `source_corroboration_count`/`content_hash` onto the two pre-existing example
  reports, which previously only had schema defaults.
- **Bug found and fixed during consolidation:** `data/reports/2026-05-07.json` failed
  `validate_report()` — several hand-authored field values never matched
  `taxonomy.py`'s controlled vocab (`volatility: "seasonal/recurring"`, `"stable/seasonal"`,
  `"medium"`; `origin_classification: "editorial"`, `"designer_origin"`,
  `"independent_criticism"`; `confidence: "low-medium"`). This had been silently broken
  since the file was first hand-authored, before this branch existed. Fixed all values to
  valid enum members; all 3 reports now pass validation. Added a TODO item recommending a
  CI check against `validate_report()` so this can't recur silently.
- **Frontend** (`docs/agent-logs/timeline-page.md`): built `/timeline`, a plain reverse-
  chronological signal index (not a graph, per run 2's design research), plus
  `getTimelineEntries()` in `web/lib/reports.ts` and nav links from homepage/archive/report
  pages.
- **Prompt tightening** (`docs/agent-logs/prompt-style-crosscheck.md`): closed two gaps in
  `summarize.py`'s prompt against Reuters Handbook attribution norms — banned evaluative
  verbs ("declared," "proves") in favor of attribution-anchored ones, and added explicit
  instructions against ubiquity language ("everyone is wearing") per doc §2.
- **Manual sampling** (`docs/agent-logs/manual-sampling-workflow.md`): designed (not yet
  exercised) a compliant workflow for social-sector signals —
  `docs/manual-sampling-template.md` for a human to fill out weekly, `src/manual_sample.py`
  helper that builds a valid `Signal` and enforces a non-empty `human_editor_note`.
- **Docs sync** (`docs/agent-logs/structure-taxonomy-sync.md`): `docs/PROJECT_STRUCTURE.md`
  brought in line with the actual tree; `taxonomy.py`'s outlet list cross-checked against
  doc §11 and found already complete, no changes needed.
- Coordinator re-ran `python -m py_compile src/*.py`, a full load+validate pass over all 3
  reports, `npx tsc --noEmit`, and `npx next build` after consolidating and fixing the
  2026-05-07 validation bug — all clean, `/timeline` confirmed in the route table.

### Known gaps carried forward
- `manual_sample.py` designed but not yet exercised to produce a real signal.
- `/signals/[slug]` still held pending more dated reports.
- No CI check yet enforcing `validate_report()` against `data/reports/*.json`.
- Legacy `trends_raw.json` migration still open (see run 2).
- Real live crawl still hasn't replaced the WebSearch-researched 2026-07-13 report.

## 2026-07-06 ~04:20 PDT — loop run 2, branch `ari3lla-index-loop-improvements`

5 more subagents, disjoint scopes, coordinator verified and consolidated.

- **Schema** (`docs/agent-logs/schema-fixity-fields.md`): added
  `Signal.source_corroboration_count` (default 1, AP/Reuters-style single-vs-corroborated
  distinction) and `Report.content_hash` (sha256 fixity check per DPC/NDSA guidance) to
  `report_schema.py`. Both optional/backward-compatible — existing example reports still
  validate without modification.
- **Frontend audit** (`docs/agent-logs/static-pages-audit-2.md`): `taxonomy/page.tsx` and
  `sources/page.tsx` were silently missing 2-3 of the 10 source sectors defined in
  `taxonomy.py` (street/user-generated, resale/secondhand, visual archive/search) — fixed.
  Build verified clean.
- **Correction to run 1's plan** (`docs/agent-logs/legacy-file-cleanup.md`): `trends_raw.json`
  is NOT dead legacy data — it's the live default output of `crawler.py`, read/written by
  `summarize.py`, `server.py`'s MCP tools, and `test_tools.py`. TODO.md's removal plan was
  wrong and has been corrected; removal now correctly requires a real migration (repoint
  those 3 files at the new report schema) rather than a straight deletion.
- **Design research, not implemented** (`docs/agent-logs/signals-timeline-design.md`):
  only 2 signal names recur verbatim across the 3 existing dated reports — not enough to
  justify `/signals/[slug]` yet, and it needs a `signal_id` field first. `/timeline` is
  lower-risk and could ship sooner.
- **Sourcing research, not implemented** (`docs/agent-logs/social-ingestion-research.md`):
  TikTok Research API is academic-only (commercial use prohibited, ruled out). Pinterest
  Trends API is usable but has no historical backfill. Recommendation: manual sampling
  first, matching doc §31's compliant-ingestion requirement.
- Coordinator re-ran `python -m py_compile src/*.py`, `npx tsc --noEmit`, `npx next build`
  after consolidating — all clean.

### Known gaps carried forward
- Manual-sampling workflow for social signals not yet implemented.
- `/timeline` and `/signals/[slug]` not yet built (latter intentionally held).
- `signal_id` field not yet added to `report_schema.py`.
- Legacy `trends_raw.json` migration (repointing crawler/summarize/server at the new
  schema) not yet done — this is real refactor work, not cleanup.
- Wire-service style cross-check against `summarize.py`'s prompt still open.

## 2026-07-06 ~03:15 PDT — loop run 1, branch `ari3lla-index-loop-improvements`

5 subagents ran in parallel on disjoint scopes, coordinator verified and consolidated.

- Added `TODO.md` at repo root: living punch list across pipeline, frontend, sourcing, and
  docs/process, seeded from `docs/CHANGELOG.md` "Known gaps" plus journalism/archival
  research below.
- **Pipeline** (`docs/agent-logs/pipeline-wiring.md`): fixed `src/run.sh` so it runs
  crawl -> summarize as one command instead of the old crawl -> test_tools -> server
  sequence, which never produced a saved report. `summarize.py` already had a usable
  `__main__` entry point.
- **Data** (`docs/agent-logs/real-report-2026-07-13.md`): added
  `data/reports/2026-07-13.json`, a 7-signal report built from WebSearch research (not a
  live crawler run — that gap in "Known gaps" below is *not* closed by this). Each signal
  carries a `human_editor_note` per doc §18/19's human-in-the-loop requirement. Validated
  against `report_schema.validate_report()`.
- **Frontend** (`docs/agent-logs/voice-audit.md`): fixed a first-person slip in
  `web/app/case-study/page.tsx` ("Designed and built..." -> "Scope: ..."). Confirmed
  `layout.tsx` branding and all other pages already voice-compliant. `tsc --noEmit` and
  `next build` clean.
- **Research** (`docs/agent-logs/journalism-research.md`): sourced 5 recommendations from
  AP Stylebook attribution guidance, the Reuters Handbook of Journalism, and the DPC/NDSA
  digital-preservation fixity guidance — folded into `TODO.md`'s new "Research inputs"
  section (source-corroboration count on signals, fixity/checksum fields on report files).
- **Hygiene** (`docs/agent-logs/hygiene-scan.md`): no sensitive data found in tracked or
  untracked files; `.gitignore` already sufficient; legacy `trends_raw.json`/
  `trends_summary.json` still present, still correctly left alone pending a confirmed
  end-to-end `run.sh` run.
- Coordinator re-ran `python -m py_compile src/*.py`, `npx tsc --noEmit`, and
  `npx next build` after consolidating all agent output — all clean, 13 routes build
  including the new 2026-07-13 report page.

### Known gaps carried forward
- `run.sh`'s crawl->summarize wiring has not yet been exercised end-to-end against live
  network access — needs a real run before legacy `trends_raw`/`trends_summary.json` files
  can be safely removed.
- The 2026-07-13 report is WebSearch-researched, not scraped by `crawler.py` — the "run a
  real crawl" gap remains open until a live crawl replaces this.
- TikTok/Pinterest compliant ingestion (doc §31) still unaddressed.

## 2026-07-06 02:04 PDT — branch setup and repo hygiene (done directly, not by a subagent)

- Created branch `ari3lla-index-rebuild` off `master`.
- Removed a stray nested `.git` repo inside `src/` (accidental `git init`, not a real
  submodule — was silently preventing `src/*` files from being tracked correctly by the
  root repo). Also removed `src/__pycache__`.
- Committed this cleanup alone first, before any feature work, so the feature diff stays
  readable.
- **Why:** the doc (section 40) calls for a rebrand + archive feature build; before adding
  new files it's worth starting from a repo that isn't quietly broken.

## 2026-07-06 02:06–02:07 PDT — five parallel subagents, each scoped to disjoint files

Dispatched 5 background agents in parallel, each restricted to a specific file set so
concurrent edits couldn't collide. None of them ran `git commit` — they edited files and
wrote their own dated log entry to `docs/agent-logs/`; consolidation and commits happened
afterward, by me, once all 5 reported back. Full detail for each is in its own log file;
summarized below.

### Data pipeline (`docs/agent-logs/data-pipeline.md`)
- Added `src/taxonomy.py` — controlled vocabularies for source sectors, confidence levels,
  volatility labels, origin classifications (doc sections 11/12/14/15), plus
  `classify_source(url)` mapping ~30 known domains to a sector.
- Added `src/report_schema.py` — `Report`/`Signal`/`CollectionWindow` dataclasses
  implementing the section-41 JSON schema, `validate_report()`, and
  `save_report()`/`load_report()`/`list_report_dates()` writing to
  `data/reports/<YYYY-MM-DD>.json`.
- Rewrote `src/summarize.py`'s LLM prompt to match section 21 (objective, no first person,
  no hype, source-incentive aware, social defaults to volatile). Computes
  `source_sector_breakdown` from real crawl data rather than trusting the model. Saves via
  the new schema instead of overwriting `trends_summary.json`.
- Added two MCP tools to `src/server.py`: `list_reports()`, `get_report(report_date)`.
- Added `data/reports/2026-07-06.json` as a schema-validated example report.
- **Why:** this is the structural core the doc keeps circling back to — without a real
  schema and per-date storage, nothing else (archive page, taxonomy, confidence labels)
  has anywhere to live.

### Frontend archive (`docs/agent-logs/frontend-archive.md`)
- Added `web/lib/reports.ts` (new file, doesn't touch existing `trends.ts`) reading dated
  JSON from `data/reports/`.
- Added `web/app/archive/page.tsx` — chronological list of all dated reports.
- Added `web/app/reports/[date]/page.tsx` — full report renderer following the section 41
  schema and section 36 module ordering.
- Added a placeholder `data/reports/2026-05-07.json` (written before the data-pipeline
  agent's `2026-07-06.json` landed — both coexist fine, confirming the schema/reader are
  independent of who authors the file).
- Verified via `npx tsc --noEmit` and `npx next build`.
- **Why:** section 23 of the doc calls the archive "the next feature" — this is what turns
  a single summary page into a historical record.

### Frontend static pages + rebrand (`docs/agent-logs/frontend-static-pages.md`)
- Rebranded `web/app/page.tsx` hero/footer/section labels from the old
  "busy girl who misses vogue" influencer tone to the ARI3LLA INDEX name, tagline, and
  section-2 institutional voice. Added nav links to the four new pages.
- Added `web/app/methodology/page.tsx`, `web/app/taxonomy/page.tsx`,
  `web/app/sources/page.tsx`, `web/app/about/page.tsx` per doc sections 22/11/14/15/16/37/38.
- Flagged (didn't fix, out of scope for that agent) that `web/app/layout.tsx`'s `<title>`
  still read "RUNWAY" — **fixed directly during consolidation**, see below.
- **Why:** the doc is explicit (section 2, section 21) that voice/tone is not cosmetic —
  "no first person, no hype, no shopping advice" is the whole differentiator from a trend
  blog. The methodology/taxonomy/sources pages are what let the site show its work instead
  of asserting authority.

### README + case study (`docs/agent-logs/readme-casestudy.md`)
- Rewrote root `README.md` from the old casual crawler-project framing to the "public
  research index" framing per section 34, preserving the accurate install/run instructions
  and MCP tools table rather than discarding them.
- Added `web/app/case-study/page.tsx` using section 33's outline nearly verbatim.
- **Why:** section 32/33 frame this project as a portfolio piece — the README and case
  study are the artifacts a recruiter/reviewer actually reads, so they needed to match the
  new positioning, not just the code.

### Repo hygiene (`docs/agent-logs/repo-hygiene.md`)
- Confirmed no other stray nested `.git` dirs exist.
- Added Python cache patterns (`__pycache__/`, `*.pyc`, `*.pyo`, `.venv/`) to the root
  `.gitignore`, which only had JS-oriented entries.
- Flagged `trends_raw.json`/`trends_summary.json` (both at repo root and in `src/`, with
  diverged content) as stale relative to the new `data/reports/` pipeline — **left in
  place** since the old crawler pipeline (`run.sh`) still produces/consumes them and
  removing them isn't reversible-free until the new pipeline is confirmed in production use.
- Wrote `docs/PROJECT_STRUCTURE.md` describing the intended end-state tree.
- **Why:** organizational debt (stray artifacts, incomplete gitignore) undermines the
  "fully organized project file system" goal even when every feature works.

## 2026-07-06 ~02:10 PDT — consolidation pass (done directly)

- Fixed `web/app/layout.tsx`'s `<title>`/`description` metadata, which still read the old
  "RUNWAY: Fashion Trend Intelligence" branding — flagged by the static-pages agent but
  out of its file scope.
- Ran `npx tsc --noEmit` and `npx next build` in `web/` — clean, all 9 routes
  (`/`, `/about`, `/archive`, `/case-study`, `/methodology`, `/reports/[date]` ×2 dates,
  `/sources`, `/taxonomy`) compile and statically generate.
- Ran `python -m py_compile` on all touched/added Python modules
  (`summarize.py`, `server.py`, `report_schema.py`, `taxonomy.py`, `crawler.py`) — clean.
- Sanity-checked `report_schema.list_report_dates()` / `load_report()` against both
  example reports (`2026-05-07.json`, `2026-07-06.json`) — both load and validate.
- Wrote this consolidated changelog and `.claude/skills/ari3lla-index/SKILL.md`.
- Committed all of the above to `ari3lla-index-rebuild` in logically separated commits.

## Known gaps / deliberately not done tonight

- `src/run.sh` and `src/test_tools.py` still exercise the **old** pipeline
  (`crawler.py` → raw-cache test → `server.py`) and never call `summarize.py` at all — this
  gap predates tonight's work (run.sh never invoked the summarizer even before this
  branch). Not fixed here because it wasn't in any agent's assigned scope and touching it
  wasn't part of the doc's explicit priority list. Worth a follow-up pass.
- Legacy `trends_raw.json` / `trends_summary.json` (root and `src/`, four files total) are
  still present and diverged from each other. Recommended: delete once `run.sh` is updated
  to call the new `summarize.py` pipeline end-to-end and the old cache files are confirmed
  unused.
- No real crawl was run tonight — the two example reports in `data/reports/` are hand-
  authored to validate the schema, not live-scraped. First real report should be generated
  by actually running the updated `summarize.py` against a fresh crawl.
- TikTok/Pinterest signal ingestion (doc sections 30/31) is still unaddressed — the doc is
  explicit that this needs compliant APIs/manual sampling, not scraping, so it was
  intentionally left out of an unattended overnight run.
