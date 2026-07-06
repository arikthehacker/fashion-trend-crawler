# TODO — ARI3LLA INDEX

Living list of work remaining on the site/pipeline. Updated each loop run. See
`docs/CHANGELOG.md` for what's already shipped and `docs/agent-logs/` for per-run detail.

## Pipeline
- [x] Wire `summarize.py` into `src/run.sh` (run 1).
- [ ] Run a real crawl + summarize pass to replace hand-authored/WebSearch-researched
      example reports in `data/reports/` with genuinely scraped/summarized data — still
      open, the 2026-07-13 report added in run 1 is WebSearch research, not a live crawl.
- [ ] `trends_raw.json`/`trends_summary.json` are live-load-bearing (run 2 correction),
      not dead legacy files — removal requires repointing `crawler.py`/`summarize.py`/
      `server.py` at the new report schema first. Real migration, still open.
- [x] Human-editor-note field added to signals (run 1, 2026-07-13 report).
- [x] `source_corroboration_count` + `content_hash` (fixity) fields added to
      `report_schema.py`, backward-compatible (run 2).
- [x] Backfilled `source_corroboration_count`/`content_hash` onto the two pre-existing
      example reports (run 3).
- [x] Added `signal_id` slug field to Signal, backfilled across all 3 reports, same slug
      reused for verbatim-recurring signals ("sheer-layering", "soft-tailoring") (run 3).
- [x] **Bug fix (run 3 consolidation):** `data/reports/2026-05-07.json` had several
      hand-authored vocab values that never matched `taxonomy.py`'s controlled lists and
      silently failed `validate_report()` (`volatility: "seasonal/recurring"`,
      `"stable/seasonal"`, `"medium"`; `origin_classification: "editorial"`,
      `"designer_origin"`, `"independent_criticism"`; `confidence: "low-medium"`). Fixed
      to valid enum values; all 3 reports now pass `validate_report()`. This had gone
      unnoticed since the file was first hand-authored — worth a lint/CI check going
      forward so bad example data doesn't silently sit unvalidated again.
- [x] Wire-service style cross-check against `summarize.py`'s prompt (run 3) — tightened
      wording on attribution verbs and ubiquity-language avoidance per Reuters Handbook.
- [x] Manual-sampling workflow designed: `docs/manual-sampling-template.md`,
      `docs/manual-sampling-workflow.md`, `src/manual_sample.py` helper enforcing a
      non-empty `human_editor_note` (run 3).
- [ ] Actually run the manual-sampling workflow once to produce a real social-sector
      signal via `src/manual_sample.py` — designed but not yet exercised.

## Frontend
- [x] Voice audit pass across all pages (run 1) — fixed first-person slip in case-study.
- [x] Taxonomy/sources/methodology drift audit (run 2) — fixed missing source sectors.
- [x] `/timeline` page built (run 3) — plain reverse-chronological index, matches archive
      page conventions, nav links added from homepage/archive/report pages.
- [ ] `/signals/[slug]` — `signal_id` now exists (run 3), but still only 3 reports and 2
      recurring slugs; hold until more reports accumulate before building the page itself.
- [x] `layout.tsx` metadata confirmed correct (run 1 audit).
- [x] `docs/PROJECT_STRUCTURE.md` synced to actual tree, `/timeline`/`/signals/[slug]`
      marked planned vs. built accordingly (run 3).

## Data / sourcing
- [x] TikTok/Pinterest compliant-ingestion research done (run 2). Recommendation: manual
      sampling first, Pinterest Trends API later, skip TikTok Research API and commercial
      datasets.
- [x] Manual-sampling workflow implemented (design + helper, run 3) — see Pipeline section.
- [x] Taxonomy source-sector coverage audit (run 2); outlet-list cross-check against doc
      §11 found no gaps in `DOMAIN_SECTOR_MAP` (run 3).

## Docs / process
- [x] `docs/CHANGELOG.md` kept current each run.
- [x] `docs/PROJECT_STRUCTURE.md` synced (run 3).
- [ ] Periodically re-read doc §2 (voice), §18/19 (human-in-loop), §31 (compliant social
      ingestion), §24 (signals/timeline) to keep the build aligned with the source concept
      doc as it grows.
- [ ] Consider adding a CI/pre-commit check that runs `validate_report()` against every
      file in `data/reports/` so a bad hand-authored value (like the run-3 bug) can't sit
      undetected again.

## Run 4 — done
- [x] CI validation check: `src/validate_all_reports.py` + `.github/workflows/validate-reports.yml`,
      tested against an injected failure case, not just the happy path.
- [x] Exercised `manual_sample.py`: added a real Pinterest-sourced social signal
      ("Off-Duty Varsity", flagged low-confidence/flash/event-driven in its own
      human_editor_note) to `data/reports/2026-07-13.json`.
- [x] Shipped `/signals/[slug]` — decided to ship now rather than wait; low cost, and more
      reports/slugs will only make it more useful over time.
- [x] Surfaced `source_corroboration_count` and `content_hash` in the report UI (small,
      unobtrusive — corroboration count only shown when >1, checksum truncated in footer).

## Run 5 — done
- [x] Fixed WCAG heading hierarchy: report/signal/timeline page section labels converted
      from styled `<p>` to real `<h2>`/`<h3>`.
- [x] Added `web/app/sitemap.ts`, `web/app/robots.ts`, and `NewsArticle` JSON-LD on report
      pages.
- [x] Added a "Cite as" citation block to report page footers (site name, date, canonical
      path, checksum reference) — kept site-relative since no absolute domain exists yet
      anywhere in the codebase (don't invent one; add real domain when one is chosen).
- [x] Legacy `trends_raw.json` migration plan written (`docs/agent-logs/legacy-migration-plan.md`) —
      detailed, sequenced, verifiable steps. **Not executed** — deliberately scoped as
      planning only since `server.py`'s MCP tools are a real external contract
      (registered in `.codex/config.toml`), and rewiring them unattended is too risky for
      one loop run. Execute deliberately, one step at a time, with verification between
      each.
- [x] Confidence-scoring research (`docs/agent-logs/confidence-scoring-research.md`):
      ICD 203/Words-of-Estimative-Probability and CTI-analyst practice both support
      deriving `confidence` deterministically from `source_corroboration_count` +
      source-sector diversity rather than an LLM judgment call. Concrete formula proposed,
      not yet implemented.

## Run 6 — done
- [x] Implemented `derive_confidence()` in `report_schema.py` as an opt-in helper (not
      auto-applied to `save_report()` yet) plus a `confidence_source` field to track
      derived vs. manual. See `docs/agent-logs/confidence-derivation-impl.md`.
- [x] Executed migration-plan step 1 only: parameterized `crawler.py`'s cache path behind
      a named constant, zero behavior change, verified nothing downstream breaks. 4 steps
      remain in `docs/agent-logs/legacy-migration-plan.md` — do one at a time.
- [x] Curated 6 overly long `signal_id` slugs down to 2-3 words in 2026-07-13.json.
- [x] Added `data/reports/2026-07-20.json`, a 4th report (WebSearch-researched), including
      2 recurrence checks against 2026-07-13's signals (one flagged `declining` now that
      the World Cup, which drove it, has ended).
- [x] **Cross-run consistency fix (run 6 consolidation):** the new-report agent and the
      slug-curation agent ran concurrently and produced a slug mismatch — 2026-07-20.json
      referenced the pre-curation long slugs for its two recurring signals. Fixed to match
      the curated short slugs so recurrence tracking on `/signals/[slug]` actually works
      across both files. All 4 reports now pass `validate_all_reports.py`.
- [x] Gap analysis against the original doc's §40 priority list after 6 runs — see
      `docs/agent-logs/gap-analysis-run6.md`.

## Run 7 — done
- [x] Added Corrections, Editorial Independence, and AI Involvement disclosure sections to
      `methodology/page.tsx` and `about/page.tsx` — closes the top gap-analysis finding.
- [x] Migration step 2/5: parameterized `summarize.py`'s `load_trends()`/`summarize()` to
      optionally accept an explicit path/in-memory data, default behavior unchanged.
- [x] Added `collection_status`/`thin_week_note` fields to `report_schema.py` and a prompt
      instruction in `summarize.py` for honest low-signal weeks instead of manufactured
      signals.
- [x] Refreshed `.claude/skills/ari3lla-index/SKILL.md` — removed the stale "run.sh KNOWN
      STALE" note (fixed in run 1), added missing file-map entries, replaced the outdated
      "Common next steps" list with a pointer to this file's top items.
- [x] Audited all 22 signals across 4 reports against `derive_confidence()`
      (`src/audit_confidence.py`, new reusable script) — 14 mismatches, mostly the formula
      scoring conservatively-assigned signals higher (not concerning). **One genuinely
      concerning case found:** `Resale/secondhand retail growth` (2026-07-13) was assigned
      "high" confidence with `source_corroboration_count=1` — a single-source signal
      promoted past what its corroboration actually supports. Not auto-corrected (per
      audit's own recommendation not to auto-adopt formula output) — flagged for human
      review below.

## Run 8 — done
- [x] Resolved the flagged "Resale/secondhand retail growth" signal — found genuine second
      independent corroboration (GlobalData's own published resale analysis, distinct from
      the BoF/ThredUp source already cited) rather than downgrading. "High" confidence now
      legitimately earned; confirmed by re-running `audit_confidence.py`.
- [x] Wired `derive_confidence()` into `validate_all_reports.py` as a non-blocking
      confidence warning (flags assigned="high" vs. derived in medium/low), also wired into
      the CI workflow. Reuses the existing formula, doesn't duplicate logic, never fails
      the build.
- [x] Migration step 3/5: `server.py`'s three MCP tool functions now reference the shared
      `DEFAULT_OUTPUT_FILE` constant instead of hardcoded string literals — zero behavior
      change, function signatures/names untouched (real external MCP contract, verified
      registered in `.codex/config.toml`).
- [x] **Major finding: ran the real pipeline end-to-end for the first time.**
      `crawler.py` successfully crawled real pages (Vogue, WhoWhatWear, Hypebeast — 119
      real headlines), and `summarize.py` made a real Anthropic API call using the
      pre-existing `.env` credentials. **Found and fixed a genuine bug**: `max_tokens=2000`
      in `summarize.py` was too small and truncated Claude's JSON response mid-string,
      crashing the pipeline — fixed to `max_tokens=4000`. The live output collided with the
      existing hand-authored `2026-07-06.json` (today's date) and was correctly NOT used to
      overwrite curated data; saved instead to
      `docs/agent-logs/live-crawl-2026-07-06-real-output.json` for reference. See
      `docs/agent-logs/live-crawl-attempt.md`.
- [x] Retention/versioning research (`docs/agent-logs/retention-versioning-design.md`):
      found that `save_report()` silently overwrites `content_hash` with no change history,
      which undercuts the site's own Corrections-section claim that originals are preserved
      alongside corrections. Concrete `revision_history` field proposed, not implemented.
- [x] **Coordination bug found and fixed during consolidation:** one agent's cleanup
      (`git checkout` while reverting its own exploration files) silently wiped out two
      other concurrently-running agents' uncommitted work (the migration-step-3 edit to
      `server.py` and the confidence-warning wiring in `validate_all_reports.py`). Caught
      by re-checking `git diff` against each agent's described changes before committing;
      both pieces of work were redone directly by the coordinator from the agents' logged
      specs. **Process note for future runs:** agents that explore/revert should scope
      `git checkout`/`git restore` to the exact files they touched, never a bare
      `git checkout .`, since concurrent agents' uncommitted changes share the same
      working tree.

## Run 9 — done
- [x] Implemented `revision_history` on `Report` — `save_report()` now requires
      `revision_reason`/`corrected_at` when overwriting a differing report for an existing
      date, appending the old `content_hash` to history first. Matches what the
      methodology page's Corrections section already claimed.
- [x] Design proposal for handling pipeline re-runs on an already-used date
      (`docs/agent-logs/pipeline-rerun-design.md`) — recommends wiring through
      `revision_history` (mandatory reason) rather than silent overwrite or `--force`.
      Not yet wired into `summarize.py`'s save call.
- [x] Migration step 4/5: `test_tools.py` now references the shared `DEFAULT_OUTPUT_FILE`
      constant too. All 4 files that touch the legacy cache filename now point at one
      source of truth in `crawler.py`. Step 5 (final deletion) is unblocked.
- [x] Manual-sampling workflow exercised a second time — added a Pinterest Predicts 2026
      "Poetcore" signal (WWD-corroborated) to `2026-07-20.json`, proving the workflow is
      repeatable, not a one-off.
- [x] Added an explicit git-safety guardrail to the project skill doc after run 8's
      coordination bug (agents must scope revert commands to exact files, never a bare
      `git checkout .`) — this run's 5 agents followed it and no work was lost.
- [x] Refreshed skill doc's "Common next steps" to reflect run 9 status (fixed a note that
      was already stale the moment it landed, since revision_history shipped concurrently
      with the note claiming it was still open).

## Run 10 — done
- [x] Wired `revision_history` into `summarize.py` — `summarize()` takes optional
      `revision_reason`/`corrected_at` (CLI flags via argparse), blocks with a clear
      re-run message on an unreasoned overwrite instead of crashing, first-time saves
      unaffected.
- [x] **Migration step 5 verification found a real blocker prior runs missed:**
      `web/lib/trends.ts` (the Next.js live-crawl data loader) still reads root-level
      `trends_raw.json`/`trends_summary.json` directly via `fs.readFileSync` — every prior
      migration-step run only checked `src/*.py`, never the frontend. Legacy files
      correctly NOT deleted. See `docs/agent-logs/migration-step5-final.md`.
- [x] Second full voice audit (first since run 1) — found and fixed a tonal outlier on the
      about page (manifesto-style aphorisms that read as "stylist voice" without using a
      literal banned word). Everything else already compliant.
- [x] Added `data/reports/2026-07-27.json`, a 5th report — **first real-world test of the
      thin-week honesty mechanism**: genuinely found too few distinct signals in-window and
      correctly set `collection_status: "thin"` with an honest note instead of padding.
      This validates the run-7 schema work actually holds up in practice.
- [x] Refreshed `README.md` and `case-study/page.tsx` to match 9 runs of actual shipped
      work (they'd drifted well behind reality).

## Run 11 — done
- [x] **`web/lib/trends.ts` decision proposal ready for human sign-off**
      (`docs/agent-logs/trends-ts-fate-proposal.md`): `getTrends()` is used by the
      homepage specifically, currently rendering a stale, un-versioned crawl snapshot from
      run 8's live-crawl test rather than anything from the dated-report archive — a real,
      user-visible inconsistency. Recommendation: retire `trends.ts`, rebuild the homepage
      as a masthead + latest-report teaser sourced from `reports.ts`, then delete the 4
      legacy JSON files. **Not yet executed — needs sign-off since it changes the
      homepage's data source**, see below.
- [x] Periodic confidence review — no new concerning cases across the 2 reports added in
      runs 9-10; all mismatches remain in the harmless conservative-editor direction.
- [x] Site-wide nav/link audit — found and fixed real drift: `/case-study` was completely
      orphaned (no inbound links from anywhere), and methodology/taxonomy/sources/about had
      fallen behind the homepage's nav set as newer pages (timeline, archive) shipped in
      later runs without updating the older pages' nav. Unified nav across 5 pages.
- [x] Search/discoverability design (`docs/agent-logs/search-discoverability-design.md`):
      recommends Pagefind (static post-build indexing, zero backend) for free-text search
      plus a small client-side facet filter over `source_sectors`/`confidence`/
      `volatility`/`origin_classification`, given the site is a fully static export.
      Not implemented — scoped as its own future build.
- [x] Added `data/reports/2026-08-03.json`, a 6th report — again honestly thin, plus two
      "dormancy check" signals correctly downgraded from earlier medium/high ratings due to
      lack of fresh corroboration (sheer-layering, soft-tailoring), consistent with
      `derive_confidence()`.

## Run 12 — done
- [x] Built `/search` with client-side facet filtering (source sector, confidence,
      volatility) over a flattened `getSearchIndex()` in `reports.ts`. Full-text search
      (Pagefind) deliberately deferred as a heavier follow-up, not needed for the current
      corpus size.
- [x] Signal dormancy: after checking `taxonomy.py`'s existing `declining` volatility
      label, decided a parallel `signal_status` field would be redundant. Built
      `get_signal_status_history(signal_id, all_reports)` instead — a helper that surfaces
      a signal's actual volatility/confidence trend across reports, which is what an editor
      actually needs to judge dormancy, rather than a static label that would itself go
      stale.
- [x] Expanded `taxonomy.py`'s domain coverage for 4 previously-thin sectors
      (designer_origin, visual_archive, independent_criticism, institutional).
- [x] Added `data/reports/2026-08-10.json`, a 7th report — Copenhagen Fashion Week SS27
      fell in-window but no dated post-show coverage was retrievable; logged one signal at
      deliberately low confidence rather than treating a pre-show forecast as confirmed.
      Did NOT repeat the sheer-layering/soft-tailoring dormancy check a third consecutive
      time (would have been padding) — noted in limitations instead.
- [x] **12-run health check** (`docs/agent-logs/health-check-run12.md`) — a genuinely
      useful outside-the-loop look: found `off-duty-varsity`'s dormancy flag has now gone
      3 reports without a resolution mechanism (real, if minor, neglect); confirmed
      `web/lib/trends.ts` is correctly "blocked on you" rather than neglected; found three
      consecutive thin/near-thin reports read differently to a reader than three isolated
      ones and recommended surfacing that pattern explicitly rather than each report
      restating "quiet period" fresh. **This run's report agent independently addressed
      the cadence concern** by giving 2026-08-10 a distinct, honestly-argued thin-status
      reason instead of repeating prior boilerplate.

## Run 13 — done
- [x] Resolved `off-duty-varsity` dormancy via `get_signal_status_history()` — confirmed
      3+ weeks silent since the World Cup ended, closed it out with a `revision_history`
      entry on `2026-07-20.json`.
- [x] Surfaced consecutive-thin-week pattern on the archive page via
      `getConsecutiveThinWeekCount()`, shown when streak >= 2.
- [x] Reorganized `docs/CHANGELOG.md` into a concise index + `docs/changelog-entries/*.md`
      per-run detail files (13 files), all content preserved.
- [x] Added Pagefind full-text search wiring — **found and fixed a real build break
      during consolidation**: the agent's `output: "export"` config change broke the build
      because `sitemap.ts`/`robots.ts` aren't yet export-compatible (need explicit
      `dynamic = "force-static"`). Reverted that one line; Pagefind's devDependency/postbuild
      script are left in place but inert until static export is properly restored.
- [x] Refreshed skill doc file map and next-steps for run 12-13 state.
- [x] **User approved the `trends.ts` retirement mid-run** — executing now, see below.

- [x] **`trends.ts` retirement executed — user approved mid-run-13.** Rewrote the
      homepage as a masthead + latest-report teaser sourced from `reports.ts`'s new
      `getLatestReport()`. Deleted `web/lib/trends.ts` and all 4 legacy
      `trends_raw.json`/`trends_summary.json` files (root + `src/`). **Migration step 5/5
      complete** — the 6-run-old legacy-migration plan is finally closed out.

## Run 14 — done
- [x] Fixed static export properly: `force-static` on `sitemap.ts`/`robots.ts`,
      `output: "export"` restored, confirmed real `out/` directory produced. Pagefind's
      postbuild step still needs a local `npm install` to actually verify indexing.
- [x] Added `/rss.xml` — standard RSS 2.0 feed of all reports, plus a `<link rel="alternate">`
      tag in `layout.tsx` metadata.
- [x] Added `data/reports/2026-08-17.json`, an 8th report — **now the 4th consecutive
      thin report** (07-27, 08-03, 08-10, 08-17). Explicitly named as a streak in the
      report's own limitations/tags, per the run-12 health check's recommendation.
- [x] Doc consistency pass — README/PROJECT_STRUCTURE/skill doc had several stale
      references (legacy trend files, wrong report count, `run.sh` still marked broken)
      fixed to match actual current state.
- [x] AI-journalism-standards research (`docs/agent-logs/ai-journalism-standards-research.md`):
      compared against AP/Poynter/Reuters guidelines. Found real gaps: `human_editor_note`
      isn't an auditable per-report sign-off record, no prompt-versioning/review cadence,
      no stated bias-audit practice, no explicit draft-vs-published gate.

## Run 15 — done
- [x] **Investigated the 4-thin-week question directly:** ran a real `crawler.py` crawl
      (119 headlines, 106 unique). Only ~8-12 were genuine style-discourse candidates, none
      providing new corroboration for tracked signals. **Conclusion: the streak is a real
      quiet period, not a WebSearch under-finding artifact** — higher raw crawl volume
      doesn't translate into higher usable signal volume. See
      `docs/agent-logs/live-crawl-vs-websearch-run15.md`.
- [x] Added `review_status`/`reviewed_by` fields to `Report` (soft metadata, not a hard
      gate — `human_editor_note` remains the substantive review record).
- [x] Created `docs/PROMPT_CHANGELOG.md`, a dedicated review trail for `summarize.py`'s
      prompt instructions, reconstructed retroactively from git history.
- [x] **Verified Pagefind end-to-end for real** (`npm install && npm run build`) — full
      search index built (39 pages/1750 words), all expected static assets confirmed
      served correctly. Search feature is now fully functional, not just wired.
- [x] Confidence/dormancy review — no new concerning cases; `sheer-layering`/
      `soft-tailoring` are one quiet window short of the close-out threshold, flagged for
      next review rather than closed prematurely.

## Run 16 — done
- [x] Added `data/reports/2026-08-24.json`, a 9th report — 5th consecutive thin week.
- [x] Closed out `sheer-layering`/`soft-tailoring` (3 quiet windows confirmed) and
      `peplum-waist-revival` (also hit its own stated 3-window threshold), same
      `revision_history` close-out pattern as `off-duty-varsity`.
- [x] Added low-volatility framing to the methodology page — thin weeks are now
      explicitly described as a verified data point, not a gap.
- [x] **First real bias-audit pass** (logged in `docs/PROMPT_CHANGELOG.md` and
      `docs/agent-logs/bias-audit-run16.md`): found `crawler.py`'s source list is
      English-language/Western-editorial only (real, documented scope limitation, not
      fixed this run); found `derive_confidence()`'s `HIGH_RELIABILITY_SECTORS`
      inconsistently excluded `independent_criticism` despite comparable noise profile to
      editorial — **fixed** by adding it to the gate.
- [x] Backfilled meaningful `reviewed_by` provenance on 7 reports (e.g.
      "websearch-run-thin-week", "hand-authored-example-run1") instead of leaving it blank.
- [x] Fashion week calendar research confirms NYFW/LFW/MFW/PFW run ~Sept 8 – Oct 6, 2026 —
      the low-volatility stretch should end structurally around then, not before.

## Run 17 — done
- [x] Expanded `FASHION_SOURCES`/`taxonomy.py` with 4 non-Western-oriented outlets
      (nataal.com, okayafrica.com, fashionunited.in, tokyofashion.com) — partial fix,
      honestly caveated: BFS from these seeds still can't guarantee balanced coverage, and
      most remain English-language/diaspora-facing rather than local-for-local.
- [x] Added homepage thin-week framing — a conditional note under the latest-report
      teaser when `collection_status === "thin"`, linking to methodology.
- [x] **Added `data/reports/2026-08-31.json`, a 10th report — ends the 5-week thin
      streak with a genuinely earned "normal" status.** Caught a real editorial red flag:
      a Pantone/movie-tie-in signal where the causal claim ("movie inspired the report")
      is likely reversed since the report predates the film's public imagery — flagged
      low confidence with the concern noted explicitly.
- [x] Refreshed skill doc for runs 13-16, added an "institutional knowledge" section on
      the fashion-week calendar so the thin-week streak isn't mistaken for a bug.
- [x] Created `docs/EDITORIAL_CALENDAR.md` — a reusable reference for recurring
      high-volatility windows, so future report-writing agents don't re-research fashion
      week dates from scratch each time.

## Run 18 — done
- [x] Verified all 4 run-17 source additions are actually crawlable. Found and fixed a
      real crawler bug: `tokyofashion.com` (Cloudflare-fronted) was falsely blocked
      because `get_robots_parser()` used Python's default urllib user-agent, which
      Cloudflare 403s on `/robots.txt` — the parser then treated that 403 as "disallow
      all." Fixed to fetch robots.txt with the crawler's own real user-agent. General
      robustness fix, not source-specific.
- [x] Busy-week readiness check: the largest report was already close to the 4000-token
      ceiling; raised `max_tokens` to 8000 in `summarize.py` proactively, before fashion
      month causes a real truncation (same failure mode as run 8's bug, just avoided this
      time instead of hit).
- [x] Added `data/reports/2026-09-07.json`, an 11th report (pre-NYFW week) — correctly
      did NOT force-continue the prior week's Pantone/movie-tie-in signal once its news
      hook was exhausted.
- [x] Second bias-audit pass, appended to `docs/PROMPT_CHANGELOG.md`. Confirmed with real
      production data (not just code analysis) that `independent_criticism` signals get
      "low" confidence far more often than `editorial` at equal corroboration counts.
      **Clarification during consolidation:** this pattern is now driven by the LLM's own
      conservative confidence assignment, not the formula gate — run 16 already added
      `independent_criticism` to `HIGH_RELIABILITY_SECTORS`, so the residual gap is a
      prompt-tuning question, not an unfixed code bug. Also flagged: Pinterest's own
      self-promotional "trend report" pages get tagged identically to organic social
      content, with no schema-level way to distinguish platform marketing from UGC.
- [x] Doc-sync check found a real staleness bug: README/PROJECT_STRUCTURE claimed only
      7 reports (and listed even fewer) when 10 actually existed. Fixed to 11.

## Run 19 — done
- [x] Tuned `summarize.py`'s prompt to remove the default confidence penalty on
      `independent_criticism` at equal corroboration counts vs. `editorial`.
- [x] Added platform-marketing-vs-organic guidance to the manual-sampling template/workflow
      docs (documentation-level, no schema change).
- [x] Added `data/reports/2026-09-14.json`, a 12th report — the first genuinely
      high-volatility window (NYFW SS27 week 1). **Busy-week fixes held up**: 5 signals,
      no truncation, no validation issues. Correctly recognized the harness's real current
      date (2026-07-06) predates the actual show and stuck to verifiable pre-show facts
      rather than fabricating runway reviews.
- [x] Deeper source-diversity pass: added 3 more verified local-for-local outlets
      (vogue.mx, tribune.com.pk, savoirflair.com). Honestly narrowed, not closed — still
      English/Spanish-only, Southeast Asia remains open (vogue.ph blocked by a Cloudflare
      JS-challenge, a different failure mode than run 18's UA fix).
- [x] **Full re-read of the original concept doc found two real, 18-run-old gaps**: an
      unbuilt `/glossary` page (doc §24) and the "THIS WEEK'S INDEX" condensed metrics
      module (doc §27/28 — an AQI/stock-index-style glanceable summary, central to the
      original "index people check daily" thesis, never built). Also brought a fresh
      external citation: Getty AAT/ICOM Costume Core controlled-vocabulary standards,
      relevant to `taxonomy.py`'s garment/material vocab as the archive scales.

## Run 20 — done
- [x] **Built "THIS WEEK'S INDEX"** — `getThisWeeksIndex()` in `reports.ts` derives 8
      real metrics (sources scanned, items collected, top signal, rising term, recurring
      material, dominant mood, highest-volatility sector, overall confidence) from actual
      report data, no hardcoding. Compact, plain-text module on the homepage per doc §27/28.
- [x] **Built `/glossary`** — ~29 terms extracted from `aesthetic_terms`/
      `cultural_references`/`top_signals[].name` across all 13 reports, deduplicated,
      wire-service definitions, linked from nav on 4 pages.
- [x] Costume Core/Getty AAT research: found one genuine terminology drift case
      (`peplum-waist-revival`'s garment description silently changed across 3 reports) but
      concluded a formal controlled vocabulary isn't worth adopting yet at this archive
      size — recommended a lightweight interim practice instead.
- [x] Nav-consistency audit found and fixed real drift in the "minimal footer nav" family
      (missing Search/Home links on 3 pages) — independent of and complementary to the
      glossary page's own nav wiring.
- [x] Added `data/reports/2026-09-21.json`, a 13th report (LFW week) — continued the
      established discipline of not re-asserting unverified prior signals without fresh
      evidence.

## Run 21 — done
- [x] Formalized the garment-terminology practice in `summarize.py`'s prompt: continued
      signals should keep consistent garment/material terminology unless a change is
      genuine and explicitly noted.
- [x] Third full doc re-read: no whole missing pages found this time (a good sign the
      doc is largely covered), but found a real granular gap — **`human_editor_note` was
      typed and substantively populated in the data but never rendered anywhere on the
      site**, despite being the most concrete evidence of the human-in-the-loop review
      process the project's transparency claims describe. **Fixed** — added to the
      `TopSignal` type and rendered per-signal on report pages.
- [x] Added `data/reports/2026-09-28.json`, a 14th report (MFW week) — caught a genuine
      sourcing-integrity issue (conflicting MFW dates across sources) and logged it as its
      own signal rather than silently picking one.
- [x] Stress-tested "THIS WEEK'S INDEX" against thin-week data — held up with graceful
      fallbacks on every field, no bug found.
- [x] Accessibility audit of the two new-in-run-20 surfaces found the exact run-5 heading-
      hierarchy bug pattern recurring (styled `<p>` acting as headings) — fixed on the
      homepage's new index module and signal cards, plus added proper `<dl>`/`<dt>`/`<dd>`
      semantics to the glossary.

## Run 22 — done
- [x] Investigated automating the heading-hierarchy check — **honest conclusion: ESLint/
      jsx-a11y cannot catch it** (it only checks tag semantics, not computed visual
      styling). Added `eslint-plugin-jsx-a11y` and a `lint-web` CI job anyway (real value
      for other a11y issues), but the actual mitigation is a documented manual-review
      step, now added to the skill doc's verification checklist.
- [x] Added a reciprocal cross-link between `/glossary` and `/taxonomy`.
- [x] Added `data/reports/2026-10-05.json`, a 15th report — closes out fashion month
      (PFW week). Resolved 2 continuing signals with fresh evidence, correctly noted that
      volume should return to the lower runs-19–22 baseline afterward, not read as a
      regression.
- [x] Made a real design decision on "THIS WEEK'S INDEX" placement (not just another
      proposal): it stays homepage-only, since doc §27 frames it as a live "check it now"
      snapshot, which would misrepresent `/archive`'s "preserved as issued" historical
      framing if duplicated there. Added a one-line navigational pointer from `/archive`
      to the homepage instead.
- [x] Cross-report consistency audit of all 5 fashion-month reports found the sequence
      held together well overall (signal_id renaming was intentional/documented, no
      contradictions, consistent voice) but found and fixed one real gap: a signal
      disappeared from `2026-09-14.json` without the close-out acknowledgment every other
      retired signal in the sequence got.

## Run 23 — done
- [x] Added `data/reports/2026-10-12.json`, a 16th report — **confirmed the expected
      post-fashion-month volume drop for real** (a genuine search turned up almost
      nothing verifiable, items_collected=3, not an assumed thin status).
- [x] Broad frontend health sweep found and fixed real nav gaps: `/search` was orphaned
      from primary header nav on 7 pages (only linked from footers), and `Glossary` was
      missing from the homepage nav.
- [x] **Tested the corrections/transparency claim end-to-end and found it was false**:
      3 reports have real `revision_history` entries, but nothing on the site ever
      displayed them — the methodology page's claim about correction transparency wasn't
      actually true of the live site. Fixed: added a "Correction History" section to
      report pages. Same category of gap as run 21's `human_editor_note` finding.
- [x] Periodic confidence/dormancy review — clean. No new concerning cases; all
      previously-flagged dormant signals confirmed closed and not reappearing.
- [x] Doc-sync check fixed README/PROJECT_STRUCTURE staleness again (4 runs behind,
      undercounting reports) and verified 3 spot-checked claims against actual code —
      all held up.

## Run 24 — done
- [x] **Systematic transparency-field sweep found a third instance of the same bug
      pattern**: `thin_week_note` was populated with real per-window explanations and the
      methodology page explicitly claims thin windows are checked against source volume,
      but the field was never typed or rendered — homepage and report pages showed
      generic boilerplate regardless of the actual note. Fixed. Every other schema field
      checked and confirmed either rendered or legitimately backend-only.
      `review_status`/`reviewed_by` flagged as borderline, correctly not forced.
- [x] De-staled README/PROJECT_STRUCTURE's report-count claims — replaced hardcoded
      counts/date-lists with pointers to the live archive, and added a workflow
      convention against hardcoding counts that will go stale, so this doesn't recur a
      third time.
- [x] Added `data/reports/2026-10-19.json`, a 17th report — independently re-tested (not
      copied) the thin-week call, and formally closed out
      `lfw-eligibility-wholesale-requirement-dropped` after 4 silent windows.
- [x] Retrospective-format research: counted real `signal_id` recurrence across all 16
      prior reports (only 10 of 36 unique signals recur at all, none beyond 3
      consecutive reports) and concluded a quarterly retrospective page would be
      premature — correctly deferred rather than built prematurely. Set a concrete
      revisit threshold (4-5 signals recurring 4+ times) for a future run.
- [x] CI verification: no `gh` CLI access in this environment, so real GitHub Actions
      pass/fail status remains genuinely unverified — documented honestly rather than
      assumed. Manual YAML read-through found no obvious defects.

## Run 25 — done
- [x] **Built the structural fix for the recurring "claimed but not shown" bug**:
      `src/check_field_coverage.py`, a non-blocking script enumerating every schema field
      and checking if it's typed in `reports.ts` and referenced in any `.tsx` file.
      Verified it correctly doesn't re-flag `revision_history`/`thin_week_note` (already
      fixed) or `confidence_source`/`content_hash` (legitimately backend-only). Currently
      0 warnings. Flagged `review_status`/`reviewed_by` as worth a manual look (neither
      typed nor referenced) — not auto-fixed, left for human/future-run judgment.
- [x] Added `data/reports/2026-10-26.json`, an 18th report — CFDA/Vogue Fashion Fund
      winner is now in-window by date but no dated coverage exists yet; logged as an
      honest open/unresolved signal rather than fabricated or backfilled.
- [x] **First full voice audit since run 10 (14 runs of additions) found zero
      violations** — glossary, THIS WEEK'S INDEX, search, RSS, and correction-history
      copy all checked clean, and no styled-`<p>`-as-heading bug anywhere. Confirms the
      voice discipline and the new checklist item are both actually holding.
- [x] Fashion archive standards research (Met Costume Institute, FIT Special
      Collections) confirms the schema's confidence/origin_classification/revision_history
      design already aligns with real institutional provenance practice — no new fields
      needed, a validating result rather than a new gap.
- [x] Verified the run-19 confidence-gate fix — honest negative result: no
      `independent_criticism` signals have appeared since the fix shipped, so it remains
      genuinely untested in practice, neither confirmed working nor failing.

## Run 26 — done
- [x] Resolved `review_status`/`reviewed_by`: data check confirmed they're populated with
      genuinely varying, meaningful values (not schema defaults) across 15/18 reports —
      rendered them (real editorial provenance, same category as prior fixes), not
      suppressed as backend-only.
- [x] Added `data/reports/2026-11-02.json`, a 19th report — re-checked the open CFDA/
      Vogue Fashion Fund signal (still unresolved after 2 windows, honestly carried
      forward, not fabricated).
- [x] Periodic field-coverage/confidence audit run — clean, but flagged a real gap:
      `layered-tops-styling` has gone silent for 13 consecutive windows with no
      dormancy-check or close-out, unlike its sibling signals from the same period.
- [x] **Southeast Asian source coverage: genuine progress.** Found `dewimagazine.com`
      (Indonesia) — the first truly local-for-local, non-English-language source in the
      list — verified crawlable. Honestly rejected 2 other candidates that failed
      (Cloudflare block) or didn't fit (expat lifestyle content, not local fashion press).
- [x] Reader-trust-signal research found a real UX gap: Corrections/AI-disclosure content
      is buried at the bottom of methodology/about pages with zero inline pointer from
      report pages (the actual reader entry point). **Fixed**: added a "Corrections & AI
      use" link to report page footers.

## Run 27 — done
- [x] Closed out `layered-tops-styling` after 13 silent windows — same EDITORIAL
      CLOSE-OUT pattern as prior dormant signals, via `revision_history`.
- [x] Added `data/reports/2026-11-09.json`, a 20th report. CFDA/Vogue Fashion Fund
      winner remains open (3 windows now); correctly distinguished a similarly-named UK
      award result (Bianca Saunders, BFC/Vogue Designer Fashion Fund) from the CFDA
      question rather than conflating them.
- [x] Assessed non-English source handling — `crawler.py`'s extraction is already
      script-agnostic, but `summarize.py`'s prompt said nothing about non-English content
      now that `dewimagazine.com` (Bahasa Indonesia) is live. **Fixed**: added an
      instruction requiring Claude to flag non-English source material and note that any
      description is a translation, not a direct quote.
- [x] Archive-milestone research correctly declined to build a 20-report/6-month
      milestone feature — the real newsletter-industry threshold is ~100 issues or a
      year, and self-congratulatory framing would clash with the site's no-hype voice
      rules anyway. Confirmed `/about`/`/methodology` have no stale report-count claims
      (a distinct area from the run-24 README/PROJECT_STRUCTURE fix).
- [x] Signal-link integrity verification — all 37 signal_ids across 19 reports (pre-run)
      have matching static routes, and recurring signals show full history, not just the
      latest occurrence. Clean, nothing to fix.

## Run 28 — done
- [x] Added `data/reports/2026-11-16.json`, a 21st report. CFDA Fashion Fund winner open
      a 4th window — instead of repeating the same caveat, explicitly named the unusual
      duration and offered two live, non-asserted explanations.
- [x] Third manual-sampling exercise, first real diversification beyond Pinterest: used
      TikTok's public hashtag page directly (compliant, not scraped) with independent
      editorial coverage as corroboration.
- [x] **Found and fixed a real, previously-undone drift**: `peplum-waist-revival`'s
      garment terminology drift (documented in run 19 but never actually corrected) was
      finally fixed via `revision_history` — the run-20 prompt fix has no NEW drift to
      report but also hasn't been genuinely exercised since (post-fashion-month reports
      have all been scheduling/governance signals, not garment-description ones).
- [x] **Continuity/succession research found README's operational instructions were
      actually broken** — `bash run.sh` would fail from repo root since the pipeline
      scripts assume running from inside `src/`, and the doc never mentioned the
      `--revision-reason`/`--corrected-at` flags required to re-run against an existing
      date. Fixed: corrected the run instructions and documented the correction flags.
- [x] RSS/sitemap verification found and fixed a real bug: `/glossary` and `/search` were
      completely missing from `sitemap.xml` (never added to the route list). RSS feed
      itself was already correct — 20 reports, well-formed XML, proper escaping.

## Run 29 — done
- [x] Resolved the prolonged-silence question with a minimal, correctly-scoped decision:
      no new schema field — added `is_prolonged_silence(signal_id, all_reports,
      threshold=4)` as a thin wrapper over `get_signal_status_history()`. Verified live
      against the real CFDA signal (returns `True`).
- [x] Added `data/reports/2026-11-23.json`, a 22nd report — both CFDA questions remain
      open (5th and 4th windows respectively), plus a genuine new Black Friday/holiday
      retail-calendar signal.
- [x] Full skill doc refresh — codified the "populated ≠ rendered, documented ≠ working"
      lesson (runs 21/23/24/28) as a formal workflow convention, not just something
      caught reactively each time.
- [x] Forecast-calibration research: a real, methodologically honest retrospective check
      against this project's own data. Found labels mostly held (volatile/low-confidence
      signals faded as predicted) but caught one concerning miss — `soft-tailoring` was
      called "stable/high" then collapsed to "declining" the very next window. Correctly
      caveated the small sample size rather than overreaching; recommended a periodic
      re-check as the archive grows.
- [x] Full accessibility audit found a 4th instance of the recurring heading-hierarchy
      bug (case-study page's numbered section titles were styled `<p>` tags) — fixed.
      Confirmed no image/alt-text issues (text-only site), color contrast passes WCAG AA,
      and all interactive elements are properly labeled.

## Run 30 — done
- [x] Built a custom heuristic scanner for the heading bug — honest result: it can't
      structurally distinguish the real bug from legitimate kickers/labels (same score),
      so it's a candidate-list generator for review, not a reliable pass/fail signal.
      Doesn't replace the manual visual check, but is a new tool in the toolkit.
- [x] Added `data/reports/2026-11-30.json`, a 23rd report. **Found that CFDA Fashion
      Awards had only ever been tracked in prose across 5 reports, never as a real
      `signal_id`** — so `is_prolonged_silence()` couldn't see its history. Fixed by
      giving it a real tracked signal entry. Also refused to present stale 2025 Black
      Friday data mislabeled as 2026 results.
- [x] Prompt consistency audit — conservative, correct conclusion: no redundancy/
      contradiction found across 20+ accumulated instructions; didn't force a rewrite of
      a working, tested prompt for cosmetic reasons.
- [x] Citation format research added a copy-pasteable formatted citation line to report
      pages, closing a gap noted (but blocked on missing SITE_URL) back in run 5.
- [x] **Manual-sampling quality check found the real root cause of a `human_editor_note`
      inconsistency**: it was never an actual `Signal` schema field, just an ad hoc key
      some signals happened to have. Fixed properly at the schema level, backfilled
      missing data on 2 of 3 manually-sampled signals, and closed out one now-dormant
      signal (`poetcore-aesthetic`, silent 18 windows).

## Run 31 — done
- [x] Systematic audit for other by-convention-only fields — **confirmed `human_editor_note`
      was the one genuine instance** of this bug pattern; no others found across all 23
      reports checked against the real dataclass field lists.
- [x] Added `data/reports/2026-12-07.json`, a 24th report — CFDA Fashion Fund winner now
      7 windows open; CFDA Fashion Awards correctly still shows `False` on the silence
      check since its tracked history is short even though the question is informally
      older (the tool works as designed, distinguishing tracked-history length from
      informal question age). Genuine new signal: BoF VOICES 2026 industry gathering.
- [x] Added resort/cruise collection calendar research to `docs/EDITORIAL_CALENDAR.md` —
      genuinely useful since the archive is now in a December window where cruise retail
      arrivals traditionally appear.
- [x] Full-year archive coherence review (all 23 reports at the time) — clean throughout:
      no signal_id naming collisions, no cross-report contradictions, all tooling
      (`validate_all_reports.py`, `check_field_coverage.py`, `audit_confidence.py`) still
      passes cleanly at this scale.
- [x] Performance check found a genuine (if currently minor) redundancy — `getAllReports()`
      was being called 2-3x per page render — and fixed it with a simple module-level
      cache, no behavior change. Build time measured at ~9s for 80 pages/23 reports,
      confirmed not currently a bottleneck.

## Run 32 — done
- [x] Added `data/reports/2026-12-14.json`, a 25th report — Fashion Fund winner now 8
      windows open, Fashion Awards now 3 tracked windows. Correctly distinguished the
      unrelated BFC "The Fashion Awards" (Royal Albert Hall, Nov 30) from the still-open
      CFDA question rather than conflating them.
- [x] Periodic audit found and closed out 2 more dormant signals
      (`versace-mulier-debut-timing-unconfirmed`, `armani-post-founder-transition-continues`,
      both silent 8 windows) that had never gotten the standard close-out treatment.
- [x] Year-end review research: recounted real signal recurrence across all 24 reports —
      still doesn't clear run 24's threshold, and the one signal that does recur 4+ times
      is a non-style award-status item, not a genuine style thread. Correctly declined to
      build either a quarterly retrospective or year-in-review page.
- [x] Search-facet verification confirmed everything is already genuinely dynamic (no
      hardcoded value lists) and Pagefind's index is current, not stale — no bugs found.
- [x] Manual-sampling cadence check correctly declined to manufacture a 4th sample just
      to hit a quota — doc §31 has no cadence requirement, and forcing an entry would
      violate the workflow's own human-judgment principle. Softened the workflow doc's
      "weekly" wording to "opportunistically" to match actual/correct practice.

## Run 33 — done
- [x] Added `data/reports/2026-12-21.json`, a 26th report — **the CFDA Fashion Awards
      question crossed the prolonged-silence threshold for the first time**
      (`is_prolonged_silence()` now returns `True`), confirming the tool works exactly as
      designed on real, organically-arrived-at data.
- [x] Doc-sync verification found and fixed real drift: 3 recently-added tool scripts
      (`check_field_coverage.py`, `check_heading_patterns.py`, `audit_confidence.py`)
      were missing from README/PROJECT_STRUCTURE.md's listings, and `docs/agent-logs/`
      had grown to 166+ files while the doc still named only ~15 — replaced with a
      count+pointer. Also fixed stale "exercised twice" manual-sampling claims (now 3
      times, opportunistic not scheduled).
- [x] Source-protection research: no real current risk (no per-article URLs published,
      no small-outlet pile-on vector) but found `source_links` is TS-only dead typing
      with no backend dataclass field at all — a different, minor drift class than the
      "populated but unrendered" bug, flagged for cleanup.
- [x] **Found and fixed a 4th instance of the "populated but unrendered" bug**:
      `human_editor_note` (the editorial close-out reasoning) was never shown on the
      per-signal history page (`/signals/[slug]`), even though it's the whole point of a
      close-out note. Fixed with real heading semantics.
- [ ] Editorial calendar research/maintenance pass was still running when this run was
      consolidated (unusually long WebSearch) — its output will land as its own commit
      whenever it completes, separate from this run's batch.

## Run 34 — done
- [x] Added `data/reports/2026-12-28.json`, a 27th report — CFDA Fashion Fund winner now
      10 windows open, Fashion Awards now 5. Checked for genuine year-end "best of 2026"
      content and correctly found none in-window (only evergreen or wrong-year material).
- [x] Editorial calendar updated with Met Gala (first Monday in May, confirmed 2026
      edition date) — this time tightly scoped after last run's version stalled for 600s
      and timed out; the retry succeeded quickly.
- [x] **Resolved `source_links`**: removed entirely rather than implementing. Genuinely
      traced to the original concept doc (not pure drift), but the site's shipped design
      already deliberately diverged from that brainstorm (no per-article URLs anywhere),
      and reviving it would reopen the exact small-outlet pile-on risk run 33 flagged as
      dormant, without ever designing the recommended mitigation. Cleaned the one stray
      data key via `revision_history`, not hand-editing.
- [x] **Designed a third honest state for permanently-unresolved factual questions** —
      distinct from both "actively tracked" and "resolved/closed": after several windows
      past the prolonged-silence threshold, a report may mark a signal_id "untracked
      going forward pending new information" in prose, without fabricating an answer or
      misusing the dormant-signal close-out pattern (which implies resolution, not
      absence of an answer). Documented as workflow convention #10, no schema change.
- [x] Verified the homepage index module's thin-streak concern was not actually a bug —
      the report content itself already self-discloses carry-forward status (incrementing
      window counts, threshold-crossing notes), so the module reads as an evolving status
      line, not stale data.

## Run 35 — done (all 5 tasks tightly scoped, no stalls)
- [x] Added `data/reports/2027-01-04.json`, a 28th report, crossing into the new year —
      **both CFDA questions transitioned to "untracked going forward pending new
      information" for the first time**, exercising the run-34 convention in practice
      immediately.
- [x] Slug-quality check found 11+ candidates over the length threshold — correctly
      stopped without editing since that's well past the run's 5-candidate scope cap;
      flagged for a dedicated future pass that checks cross-file signal_id references
      before any renaming.
- [x] Archival-practice research found a genuine, actionable gap: no `source_url` field
      exists anywhere in the schema, so link-rot mitigation (Wayback/Perma.cc-style
      snapshotting) is premature — nothing is actually cited/linked yet. Recommends
      adding `source_url(s)` wired from the crawler's fetched URLs, but **note the
      tension with run 34's removal of `source_links`** for source-protection reasons —
      needs reconciling, not blind implementation.
- [x] 3-report quality spot-check across the archive's full timeline (early/mid/recent)
      — all clean, no fixes needed. Correctly deferred a judgment call on convention
      timing to the coordinator rather than acting unilaterally.
- [x] Pagefind regression check confirmed the search index still builds correctly after
      run 34's `source_links` removal — 81 pages/3456 words indexed, consistent growth.

## Run 36 — done
- [x] **Reconciled the `source_url`/`source_links` tension with a final decision**: added
      `Signal.source_domains` (bare homepage domains only, e.g. `"vogue.com"`) — satisfies
      the citation need from run 35 while structurally avoiding run 33's per-article
      pile-on risk, enforced by schema validation (rejects `/` or `http`-prefixed values),
      not just convention. Deliberately schema-only this run — not populated by
      `summarize.py`, not rendered anywhere yet (that's separately scoped future work).
      `check_field_coverage.py` correctly flags it as unreferenced — expected, not a bug.
- [x] Added `data/reports/2027-01-11.json`, a 29th report — correctly stopped
      re-litigating the untracked CFDA questions weekly per the new convention, and
      honestly logged a real Golden Globes calendar-date signal without fabricating
      post-ceremony coverage that doesn't exist yet.
- [x] **Dedicated slug-curation pass completed**: all 12 over-length signal_ids from run
      35's flag renamed across 19 report files, including the high-impact recurring CFDA
      Fashion Fund signal (spans 7+ reports) — safety-checked first (slugs are looked up
      dynamically, no hardcoded references anywhere).
- [x] IPTC metadata check found and fixed a real bug: `dateModified` in report pages'
      JSON-LD was hardcoded equal to `datePublished` even for reports with real
      corrections — now correctly uses the latest `revision_history` entry when present.
- [x] Fresh CI environment verification (new venv, `node_modules` wiped and reinstalled)
      found no environment-assumption bugs — everything that passes locally also passes
      fresh. `gh` CLI still unavailable, so real GitHub Actions status remains
      unconfirmed. Also cleaned up a stale `eslint-disable` comment flagged in 2
      consecutive runs.

## Run 37 — done
- [x] **`source_domains` fully wired end-to-end**: `summarize.py`'s prompt now populates
      it (reusing the existing domain-extraction convention), and report pages render it
      per-signal. `check_field_coverage.py` confirms typed+referenced, 0 warnings.
- [x] Added `data/reports/2027-01-18.json`, a 30th report — caught and excluded a false
      lead (previously-occurred designer debuts mislabeled as upcoming Jan 2027 news).
- [x] Found and fixed the same `dateModified`-staleness bug pattern a second place: the
      RSS feed's `<pubDate>` had the identical gap just fixed on report pages (run 36) —
      now also sourced from `revision_history` when present.
- [x] Glossary freshness check found a genuinely new failure mode: undefined terms were
      silently dropped rather than shown at all (distinct from the "populated but
      unrendered" bug — this was "present but invisible due to missing curation"). Fixed
      with a real definition for the missing term.
- [x] Periodic audit caught a real regression from run 36's slug renaming: 2 stale
      long-form signal_id references survived in report prose after the actual `signal_id`
      fields were shortened, which would have silently broken
      `get_signal_status_history()` lookups. Fixed via `revision_history`.

## Run 38 — done
- [x] Dedicated slug-reference audit across all prose fields (not just `signal_id`) found
      17 additional stale long-form slug mentions run 37 missed, across 6 slugs/17 files —
      fixed via `revision_history`. The grep-for-old-references pass TODO.md flagged is
      now complete for run 36's rename batch.
- [x] Added `data/reports/2027-01-25.json`, a 31st report — re-checked the Wales Bonner/
      Hermès debut for post-show coverage, found none, correctly made no false correction.
- [x] Added a build-time `console.warn()` in `web/app/glossary/page.tsx` for terms with no
      curated `DEFINITIONS` entry — verified genuinely reachable (~130 real hits currently,
      mostly long narrative strings rather than true glossary vocabulary).
- [x] `docs/EDITORIAL_CALENDAR.md` gains a January menswear + haute couture section,
      confirmed via WebSearch.
- [x] `source_domains` extended to `/signals/[slug]` (natural fit, same per-occurrence
      detail level as the report page); homepage/timeline/search correctly left untouched.

## Run 39 — done
- [x] Added `data/reports/2027-02-01.json`, a 32nd report — honestly reported that both
      the Wales Bonner/Hermès debut and Haute Couture SS27 still have no reachable
      post-show coverage, rather than fabricating runway content.
- [x] Added `isPlausibleGlossaryTerm()` filter to `web/app/glossary/page.tsx` — cut run
      38's build-time undefined-term warnings from ~130 to 19 genuinely curatable short
      phrases, with no real curated term filtered out.
- [x] Added South China Morning Post (Hong Kong) and The National (UAE) to
      `FASHION_SOURCES`/`DOMAIN_SECTOR_MAP` — genuine geographic diversification,
      WebFetch-verified reachable. One candidate (fashionnetwork.com/africa) honestly
      rejected (403).
- [x] Closed the run-35 archival/link-rot question for good: domain-level citation is a
      permanent design choice (no permalink exists to rot), documented in a new "How
      Citations Work" methodology section. Flagged a smaller, distinct future item:
      periodic self-archival snapshotting of the site's own report pages.
- [x] Periodic audit — clean. 44 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (7th consecutive check), 3-report spot-check
      consistent.

## Run 40 — done
- [x] Added `data/reports/2027-02-08.json`, a 33rd report — Wales Bonner/Hermès debut
      crosses the prolonged-silence threshold (4 windows) for the first time, flagged
      explicitly rather than fabricated or prematurely marked "untracked."
- [x] Curated real definitions for all 19 glossary terms run 39's filter identified —
      build now shows zero "no DEFINITIONS entry" warnings.
- [x] Tested the two run-39 sources against the real crawler path (not just WebFetch):
      scmp.com fully works (48 headlines); thenationalnews.com fetches fine but yields 0
      headlines because its content is client-side rendered — a different failure mode
      than prior UA-blocking bugs, flagged for a future decision (drop vs. extend parsing).
- [x] Brought correction-notice placement in line with AP/NYT/ONA standards — added a
      pinned top-of-page notice on report pages when `revision_history` has entries,
      instead of only a buried bottom-of-page section.
- [x] Full-archive coherence review — clean. No orphaned signal_ids, docs still accurate,
      voice spot-check clean.

## Run 41 — done
- [x] Added `data/reports/2027-02-15.json`, a 34th report — Wales Bonner/Hermès debut now
      5 consecutive windows unresolved; correctly kept under active tracking rather than
      forcing an early transition to "untracked going forward," with a flagged revisit
      date (2027-03-08) for the next agent.
- [x] Resolved the `thenationalnews.com` question directly: removed from
      `FASHION_SOURCES`/`DOMAIN_SECTOR_MAP` since its content is client-side rendered and
      the project deliberately keeps `crawler.py` static-HTML-only. Historical report
      data referencing the domain left untouched.
- [x] Added byline-level AI disclosure to report pages, per Trusting News/AP/BBC
      disclosure research — surfaces AI-assisted/human-reviewed status right in the
      header, not just on the general `/methodology` policy page.
- [x] Manual-sampling check — honest negative result, no current social signal cleared
      the independent-corroboration bar. Correctly declined to force a low-quality entry.
- [x] Periodic audit — clean. 44 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (8th consecutive check), no neglected
      dormant signals found.

## Run 42 — done
- [x] Added `data/reports/2027-02-22.json`, a 35th report — Wales Bonner/Hermès debut now
      6 consecutive windows unresolved; held the revisit plan rather than transitioning
      early (checkpoint remains 2027-03-08).
- [x] Fixed a real WCAG 2.2 Target Size Minimum (2.5.8) violation — site-section nav
      links across 5 pages had ~13-16px clickable targets, under the 24px minimum; added
      padding to bring them into compliance.
- [x] Found and fixed a genuine `summarize.py` prompt-drift bug 11 runs after the last
      clean audit: a stale hand-written sector list (with a non-existent `"commerce"`
      sector, missing 4 real ones) duplicated the prompt's own authoritative list. Fixed
      by pointing at the live list instead of a second hardcoded copy.
- [x] RSS/sitemap/Pagefind freshness check — clean, all reports present, correct pubDate
      sourcing, monotonic search-index growth.
- [x] Doc-sync/nav audit fixed two real gaps: `check_heading_patterns.py` missing from
      the skill doc's file map, and `/case-study` had no site nav at all — both fixed.

## Run 43 — done
- [x] Added `data/reports/2027-03-01.json`, a 36th report — Wales Bonner/Hermès debut now
      7 consecutive windows unresolved; correctly excluded an unrelated interim Hermès
      collection and a concurrent real-world Haute Couture week from the tracked signals.
- [x] **Self-archival decided:** built `src/generate_archive_manifest.py`, a local,
      non-networked script producing a manifest (url/report_date/content_hash) of every
      `/reports/[date]` page. Deliberately does NOT call the Wayback API —
      `SITE_URL` is still `web/lib/site.ts`'s placeholder domain, so an automated
      Save-Page-Now integration would snapshot a non-resolving URL. See
      `docs/agent-logs/self-archival-decision-run43.md` for the real trigger condition
      (set a real `SITE_URL`, then wire this manifest into a scheduled Save-Page-Now
      job) — not a perpetual carry-forward item anymore.
- [x] Improved RSS item quality per RSS 2.0 best practices — item titles now lead with
      the date plus up to 3 top signal names, and per-item `<category>` tags added from
      unique source sectors.
- [x] Verified the homepage "This Week's Index" module against 15+ new reports since its
      run-21 stress test — all 8 metrics render correctly. Flagged one non-bug finding:
      dominant mood is honestly carried forward from a report ~24 weeks stale.
- [x] Periodic audit — clean. 44 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (9th+ consecutive check), all silent
      signals already carry correct close-out/deferred-transition notes.

## Run 44 — done
- [x] Added `data/reports/2027-03-08.json`, a 37th report — Wales Bonner/Hermès debut
      finally transitioned to "untracked going forward pending new information" at its
      planned checkpoint (8 consecutive unresolved windows), rather than deferring again.
- [x] Added a 12-week staleness cutoff to the homepage index module's "dominant mood"
      metric — shows an honest "no distinct mood signal in recent weeks" state instead
      of indefinite carry-forward once the source is too old.
- [x] Added Dataset structured data alongside NewsArticle on report pages (schema.org
      `@graph`), reflecting that report pages are dataset landing pages, not just
      articles. Omitted `distribution`/`contentUrl` since no public raw-JSON download
      route exists yet.
- [x] Renamed 4 over-length signal_ids created since run 36, with the full cross-file
      prose sweep done upfront in the same pass (applying run 38's lesson from the
      start, not as a follow-up).
- [x] Periodic audit — clean. 44 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (10th+ consecutive check).
- [x] **Consolidation catch:** the new-report agent used pre-rename long slugs (ran
      concurrently with the slug-rename agent) — same cross-run collision class as run
      6. Caught via grep and fixed via `save_report(revision_reason=..., corrected_at=...)`
      before committing.

## Next up (run 45 candidates)
- [ ] The run-19 confidence-gate fix remains untested — revisit once
      `independent_criticism` sources reappear.
- [ ] `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.

## Run 45 — done
- [x] Added `data/reports/2027-03-15.json`, a 38th report — found a genuinely
      undocumented Feb-March Fall/Winter 2027-28 RTW fashion month underway, distinct
      from the archive's already-documented Sept-Oct RTW and January menswear/couture
      windows. Correctly did not re-litigate the now-untracked Wales Bonner question.
- [x] Implemented the public raw-JSON download route flagged in run 44: each report's
      raw JSON is now served at `/data/reports/<date>.json` via a `prebuild` npm script,
      wired into the Dataset JSON-LD's `distribution`/`contentUrl` fields, plus a
      visible download link on the report page. Note: requires `npm run build`, not a
      bare `next build`, to actually copy the files.
- [x] Added a "How This Report Was Compiled" transparency box per Pew/FiveThirtyEight
      convention — same existing content, now visually distinct instead of reading as
      ambient header text.
- [x] Nav/link audit — clean. Run 42's `/case-study` nav and WCAG target-size fixes both
      still intact; a new site-wide broken-link check found zero broken internal links.
- [x] Periodic audit — clean. 44 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (11th+ consecutive check), confirmed the
      Wales Bonner "untracked going forward" transition is being correctly respected.

## Next up (run 46 candidates)
- [ ] The run-19 confidence-gate fix remains untested — revisit once
      `independent_criticism` sources reappear.
- [ ] `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.

## Run 46 — done
- [x] Added `data/reports/2027-03-22.json`, a 39th report — correctly distinguished
      editorial post-season trend-confirmation roundups (retrospective commentary) from
      new in-window reporting, rather than conflating the two.
- [x] Added the Feb-March RTW fashion month to `docs/EDITORIAL_CALENDAR.md` as its own
      recurring entry, confirmed via real 2026-27 cycle dates.
- [x] Added a CC BY 4.0 license to the Dataset JSON-LD and a visible license line next
      to the raw-JSON download link — scoped only to the site's own classification/
      summary metadata, not underlying source articles.
- [x] Hardened the raw-JSON download route: moved the copy logic inline into
      `next.config.ts` (evaluated on every build invocation) so it no longer silently
      breaks under a bare `next build`. `copy-reports.mjs` and the inline copy now
      duplicate the same logic — keep both in sync if it ever changes.
- [x] Periodic audit — clean. 46 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (12th+ consecutive check).

## Next up (run 47 candidates)
- [ ] The run-19 confidence-gate fix remains untested — revisit once
      `independent_criticism` sources reappear.
- [ ] `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
      Note: CI's `lint-web` job doesn't actually run a Next.js build today, so the
      `next build` vs `npm run build` distinction is currently moot there.

## Run 47 — done
- [x] Added `data/reports/2027-03-29.json`, a 40th report — logged a new forward-looking
      SS27 trend-forecast signal, kept distinct from the prior report's backward-looking
      retrospective signal.
- [x] Re-ran the run-24/32 recurrence analysis: 4 signals now recur 4+ times, meeting
      the threshold for the first time — but all 4 are unresolved factual/institutional
      questions, not style trends. Built a minimal honest "Recurring across the archive"
      section on `/archive` rather than the previously-declined narrative retrospective
      feature, which would have misrepresented open questions as trending.
- [x] Trust Project 8-indicators audit found a real gap: no reader-facing
      correction-request channel exists. Honestly disclosed on the methodology page
      rather than fabricating a fake contact mechanism.
- [x] Full-archive coherence review at the 40-report milestone fixed real doc gaps:
      `generate_archive_manifest.py`, `copy-reports.mjs`, and the Dataset/download route
      were shipped but undocumented in README/PROJECT_STRUCTURE/SKILL.md. Also corrected
      a stale SKILL.md claim that Pagefind was still "deferred" (implemented since run 14/15).
- [x] Periodic audit — clean. 47 confidence mismatches all editor-conservative, 0 field
      coverage warnings, `gh` CLI unavailable (13th+ consecutive check).

## Next up (run 48 candidates)
- [ ] The run-19 confidence-gate fix remains untested — revisit once
      `independent_criticism` sources reappear.
- [ ] `gh` CLI still unavailable; CI's real GitHub pass/fail status remains unconfirmed.
- [ ] Consider revising the run-24 recurrence threshold to exclude factual/
      administrative carry-forward signals from counting toward a retrospective-feature
      trigger, since genuine style-trend recurrence has never exceeded 3 consecutive
      reports while unresolved-question signals now recur far more.
- [ ] No external correction-request channel exists — honestly disclosed for now;
      consider adding a real one (e.g. a monitored contact address) in the future.
