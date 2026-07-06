# TODO — ARI3LLA INDEX

Living list of work remaining on the site/pipeline. Updated each loop run. See
`docs/CHANGELOG.md` for what's already shipped and `docs/agent-logs/` for per-run detail.

## Pipeline
- [ ] Wire `summarize.py` into `src/run.sh` so crawl → classify → summarize → save-report
      runs as one command (currently two disconnected halves).
- [ ] Run a real crawl + summarize pass to replace hand-authored example reports in
      `data/reports/` with genuinely scraped/summarized data.
- [ ] Once new pipeline confirmed end-to-end, remove legacy `trends_raw.json` /
      `trends_summary.json` (root + `src/`, 4 files, diverged).
- [ ] Add a human-editor-note field/review step to the report schema so interpretive
      clustering stays human-reviewed (doc §18/19) rather than fully automated.

## Frontend
- [ ] Audit all page copy against doc §2 voice rules (no first person, no hype, no
      shopping language) — re-check after every content change, not just at launch.
- [ ] `/signals/[slug]` longitudinal page once enough dated reports exist to track
      recurrence (doc §24).
- [ ] `/timeline` page, same precondition.
- [ ] Confirm `layout.tsx` metadata stays in sync on every rebrand/copy pass (has gone
      stale before).

## Data / sourcing
- [ ] TikTok/Pinterest signal ingestion via official APIs or manual sampling only — never
      scraping (doc §31). Still unaddressed.
- [ ] Expand source list coverage per sector (editorial/retail/social/designer/independent
      /institutional) — audit `taxonomy.py` against doc §11 outlet lists for gaps.

## Docs / process
- [ ] Keep `docs/CHANGELOG.md` current with every change + PST/PDT timestamp.
- [ ] Keep `docs/PROJECT_STRUCTURE.md` in sync with actual tree as files are added/removed.
- [ ] Periodically re-read doc §2 (voice), §18/19 (human-in-loop), §31 (compliant social
      ingestion) to keep the build aligned with the source concept doc as it grows.

## Research inputs to fold in (journalism/archival best practice)
- [ ] Review standard newsroom sourcing/attribution norms (single-source vs corroborated
      claims) and reflect confidence levels accordingly in `report_schema.py`.
- [ ] Review digital-archive/preservation practices (fixity, stable URLs, permanence of
      dated records) for `data/reports/` as the archive grows past a handful of dates.
- [ ] Review wire-service style guidance for neutral tone, cross-check against
      `summarize.py`'s prompt.
