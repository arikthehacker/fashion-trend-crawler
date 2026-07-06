# TODO — ARI3LLA INDEX

Living list of work remaining on the site/pipeline. Updated each loop run. See
`docs/CHANGELOG.md` for what's already shipped and `docs/agent-logs/` for per-run detail.

## Pipeline
- [x] Wire `summarize.py` into `src/run.sh` (run 1).
- [ ] Run a real crawl + summarize pass to replace hand-authored/WebSearch-researched
      example reports in `data/reports/` with genuinely scraped/summarized data — still
      open, the 2026-07-13 report added in run 1 is WebSearch research, not a live crawl.
- [ ] **Correction (run 2):** `trends_raw.json`/`trends_summary.json` are NOT dead legacy
      files — `crawler.py` writes to `trends_raw.json` by default, `summarize.py` and
      `server.py`'s MCP tools (`crawl_fashion_trends`, `get_cached_trends`, `search_trends`)
      all read/write it, and `test_tools.py` hardcodes the path. Removing them requires
      first repointing `crawler.py`/`summarize.py`/`server.py` at the new
      `data/reports/<date>.json` schema — this is a real migration, not a cleanup task. See
      `docs/agent-logs/legacy-file-cleanup.md`.
- [x] Human-editor-note field added to signals (run 1, 2026-07-13 report).
- [x] `source_corroboration_count` + `content_hash` (fixity) fields added to
      `report_schema.py`, backward-compatible (run 2). See `docs/agent-logs/schema-fixity-fields.md`.
- [ ] Backfill `source_corroboration_count`/`content_hash` onto the two pre-existing
      example reports (2026-05-07, 2026-07-06) — not done yet, they still validate fine
      with defaults but don't carry real values.
- [ ] Add a `signal_id`/slug field to Signal — needed before `/signals/[slug]` is buildable
      (see Frontend section). See `docs/agent-logs/signals-timeline-design.md`.

## Frontend
- [x] Voice audit pass across all pages (run 1) — fixed first-person slip in case-study.
- [x] Taxonomy/sources/methodology drift audit (run 2) — `taxonomy/page.tsx` and
      `sources/page.tsx` were silently missing 2 of 10 source sectors ("street/user-generated",
      "resale/secondhand") and `sources/page.tsx` was missing "visual archive/search"
      entirely; fixed. See `docs/agent-logs/static-pages-audit-2.md`.
- [ ] `/timeline` page — per run 2's design research, lower-risk to build than
      `/signals/[slug]` (no cross-report identity matching needed). Needs
      `getTimelineEntries()` added to `web/lib/reports.ts`. Not yet built.
- [ ] `/signals/[slug]` — hold per run 2 research: only 3 reports exist and only 2 signal
      names ("Sheer layering", "Soft tailoring") recur verbatim; need a `signal_id` field
      plus 4-5 reports before this is meaningful. Not yet built.
- [x] `layout.tsx` metadata confirmed correct (run 1 audit).

## Data / sourcing
- [x] TikTok/Pinterest compliant-ingestion research done (run 2) — see
      `docs/agent-logs/social-ingestion-research.md`. Recommendation: manual sampling first
      (matches doc §31), Pinterest Trends API later (official, free, but no historical
      backfill — must build our own archive), skip TikTok Research API (academic-only,
      commercial use prohibited) and commercial datasets (out of budget for this scale).
- [ ] Implement manual-sampling workflow for social signals per above recommendation —
      not yet built, this is the next concrete step.
- [x] Taxonomy source-sector coverage audit done (run 2, see Frontend section above).

## Docs / process
- [ ] Keep `docs/CHANGELOG.md` current with every change + PST/PDT timestamp.
- [ ] Keep `docs/PROJECT_STRUCTURE.md` in sync with actual tree as files are added/removed.
- [ ] Periodically re-read doc §2 (voice), §18/19 (human-in-loop), §31 (compliant social
      ingestion), §24 (signals/timeline) to keep the build aligned with the source concept
      doc as it grows.

## Research inputs already folded in (journalism/archival best practice, run 1)
- [x] AP/Reuters attribution norms -> `source_corroboration_count` field (run 2).
- [x] DPC/NDSA fixity guidance -> `content_hash` field (run 2).
- [ ] Wire-service style guidance cross-check against `summarize.py`'s prompt — not yet
      done, still open.
