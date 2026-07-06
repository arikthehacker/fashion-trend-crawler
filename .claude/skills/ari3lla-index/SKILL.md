---
name: ari3lla-index
description: How to work on the ARI3LLA INDEX project (formerly fashion-trend-crawler) — concept, architecture, voice rules, file map, and workflow conventions. Load this before making any change to this repo.
---

# ARI3LLA INDEX — working skill

## What this project is

A weekly "style signal report" — not a fashion blog, not a trend forecaster, not shopping
advice. It crawls public style discourse (editorial, retail, social, designer-origin,
independent criticism, institutional archive), classifies what it finds by source sector,
confidence, volatility, and origin, and preserves it as a dated, source-linked archive.

Full concept doc: `docs/ARI3LLA INDEX.txt` (long — it's a raw brainstorm transcript, not a
spec. Section 40 has the prioritized build list, section 41 has the JSON schema, section 2
has the non-negotiable voice rules). Read the specific section you need rather than the
whole file every time.

**Core distinction to hold onto:** designer intent ≠ editorial interpretation ≠ retail
adoption ≠ social amplification. The whole taxonomy exists to keep those separate instead
of flattening everything into "trending."

## Voice rules (apply to ALL copy — site pages, report text, README, everywhere)

No first person. No "must-have," "obsessed," "this season is all about." No shopping
recommendations. No hype. Uncertainty is allowed and should be stated plainly. TikTok/social
signals are high-noise by default and should not be upgraded just because an editorial
outlet also covered them — editorial is a source sector with its own incentives, not a
neutral authority. If you write copy that sounds like an influencer or a stylist, it's
wrong for this project, full stop — rewrite it in report/wire-service voice.

## Architecture / file map

```
src/
  crawler.py         # BFS crawler, robots.txt-respecting, extracts headlines — UNCHANGED core logic
  taxonomy.py         # source sector / confidence / volatility / origin-classification vocab + classify_source(url)
  report_schema.py    # Report/Signal/CollectionWindow dataclasses, validate_report(), save/load/list by date
  summarize.py        # calls Claude to produce a report; prompt MUST follow doc section 21's objective tone
  server.py           # MCP tools: crawl_fashion_trends, get_cached_trends, search_trends, list_reports, get_report
  run.sh               # runs the full pipeline: crawler.py -> summarize.py (classify+summarize+save dated report). Fixed in run 1 — no longer stale.
  test_tools.py       # tests the OLD raw-cache pipeline, unrelated to report_schema — leave alone unless migrating it
  manual_sample.py    # helper for the manual TikTok/Pinterest sampling workflow; enforces non-empty human_editor_note
  validate_all_reports.py  # CI check — runs validate_report() against every file in data/reports/, see .github/workflows/validate-reports.yml
data/
  reports/<YYYY-MM-DD>.json   # one archived report per collection window, schema in report_schema.py
web/                   # Next.js app
  app/
    page.tsx            # homepage — hero/tagline/footer must match section 2 voice + section 25 copy
    archive/page.tsx     # lists all dated reports
    reports/[date]/page.tsx  # renders one report, module order per doc section 20/36
    timeline/page.tsx     # reverse-chronological index across all reports (built run 3)
    signals/[slug]/page.tsx  # longitudinal view per signal_id, tracks recurrence across reports (shipped run 4)
    methodology/page.tsx  # doc section 22
    taxonomy/page.tsx     # doc sections 11/14/15/16
    sources/page.tsx      # doc section 11's outlet lists
    about/page.tsx        # doc sections 37/38
    case-study/page.tsx   # doc section 33, portfolio framing
    layout.tsx           # site-wide <title>/description metadata — keep in sync with rebrand, this has gone stale before
    sitemap.ts, robots.ts  # added run 5
  lib/
    trends.ts           # ORIGINAL data layer for the live/current-crawl view — don't repurpose for archive reads
    reports.ts           # archive data layer, reads data/reports/*.json — separate from trends.ts on purpose
docs/
  ARI3LLA INDEX.txt      # source concept doc, read-only reference, don't edit
  CHANGELOG.md           # master reconciled log of what changed and why, chronological, PDT/PST timestamps
  PROJECT_STRUCTURE.md   # intended end-state tree with per-entry notes
  agent-logs/*.md        # per-agent working logs from the overnight build — provenance detail, not the master log
.github/
  workflows/validate-reports.yml  # CI: runs validate_all_reports.py on push/PR (added run 4)
```

## Workflow conventions for this project

1. **Every change gets logged to `docs/CHANGELOG.md`** — what changed, why (tie back to a
   doc section when applicable), and a PST/PDT timestamp (`date -u` then subtract 7h for
   PDT / 8h for PST — check `TZ`/`zoneinfo` availability first, it's been missing tzdata on
   this machine before). Don't rely on memory of what you did — write it down as you go.
2. **When splitting work across multiple subagents**, scope each one to a disjoint file
   set and tell them explicitly not to touch anything else. Have them write to their own
   `docs/agent-logs/<name>.md` instead of committing directly — commits happen once, in
   consolidation, by whoever is coordinating, after verifying the build.
3. **Always verify before committing**: `cd web && npx tsc --noEmit && npx next build` for
   the frontend, `python -m py_compile src/*.py` for the backend. Don't trust an agent's
   self-report of "verified" without re-running it if you're the one consolidating.
4. **Never let voice slip** — if new copy sounds like a blog post or an ad, it's a bug, not
   a style choice. Check against doc section 2 before shipping any new page copy.
5. **The designer-eye / interpretive classification work (which signals cluster together,
   what a cluster of raw terms actually means culturally) is explicitly NOT something to
   automate away** — per doc section 18/19, AI extracts/clusters/summarizes, a human
   decides what the clusters mean. Don't build a fully automatic "signal detector" that
   skips human review; keep a human-editor-note field / review step in the pipeline.
6. **TikTok/Pinterest ingestion** should use official APIs, approved datasets, or manual
   sampling — never aggressive/ToS-violating scraping (doc section 31). If asked to add
   social scraping, push back and ask about the compliant path first.

## Common next steps

See `TODO.md` at repo root for the current authoritative, per-run list (updated every loop
run) — don't duplicate it here. As of run 6, the highest-priority open items are:

- Still no report from an actual live crawl — all dated reports so far are hand-authored or
  WebSearch-researched, not produced by `run.sh` end-to-end.
- No corrections/transparency policy on-site (methodology/about pages have no mention of
  corrections, editorial independence, or AI-involvement disclosure).
- Legacy `trends_raw.json`/`trends_summary.json` migration is a real, sequenced plan
  (`docs/agent-logs/legacy-migration-plan.md`) — execute one step at a time, not in one pass;
  these files are still load-bearing until the migration completes.
