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

## Next up (run 13 candidates, from the health check)
- [ ] **Still pending your sign-off:** retire `web/lib/trends.ts`, rebuild the homepage off
      `reports.ts` (proposal in `docs/agent-logs/trends-ts-fate-proposal.md`, run 11).
      2 runs old now — flagging again since it's genuinely blocked, not forgotten.
- [ ] Resolve `off-duty-varsity`'s dormancy — 3 reports have now flagged it quiet without
      a resolution. `get_signal_status_history()` now exists to check its actual trend;
      use it to make a final call (declining vs. genuinely ended) rather than flagging a
      4th time.
- [ ] Consider whether to explicitly surface "N consecutive thin/low-signal weeks" as its
      own noted pattern on the site (e.g. in the archive or methodology page) rather than
      leaving each thin report to read as an isolated event — per the health check's
      reader-experience observation.
- [ ] Consider prioritizing qualitative fixes (the above) over mechanically adding an 8th
      report every run, per the health check's explicit recommendation.
