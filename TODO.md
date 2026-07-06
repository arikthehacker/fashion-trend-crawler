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

## Next up (run 24 candidates)
- [ ] Southeast Asian source coverage remains open (vogue.ph blocked by Cloudflare JS
      challenge — would need a headless-browser approach, likely out of scope).
- [ ] Two real "claimed but not shown" transparency gaps have now been found and fixed
      (`human_editor_note` run 21, `revision_history` run 23) — worth one more sweep to
      check if any OTHER schema field with a transparency/trust claim is similarly unused
      in the actual UI.
- [ ] README/PROJECT_STRUCTURE have now gone stale 2 times (runs 18, 23) — consider
      whether report-count/feature-list sections should be generated automatically at
      build time instead of manually maintained, to stop this recurring.
