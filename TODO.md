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

## Next up (run 8 candidates)
- [ ] **Human review needed:** `data/reports/2026-07-13.json`'s "Resale/secondhand retail
      growth" signal is rated "high" confidence on a single source — either find a second
      corroborating source, or downgrade to "medium"/"low" to match its actual evidence.
      See `docs/agent-logs/confidence-audit.md`.
- [ ] Wire `derive_confidence()` in as a non-blocking validation warning (flag
      assigned="high" vs. derived<="medium" for editor re-review) rather than full auto-
      adoption, per the audit's recommendation.
- [ ] Continue legacy migration: step 3 of 5 (`server.py`'s cache reads).
- [ ] Still no report from an actual live crawl — all 4 dated reports are hand-authored or
      WebSearch-researched.
- [ ] Manual TikTok/Pinterest sampling has only been exercised once — not yet proven as a
      repeatable weekly habit.
