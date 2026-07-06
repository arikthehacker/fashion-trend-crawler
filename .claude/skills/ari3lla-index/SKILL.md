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
  taxonomy.py         # source sector / confidence / volatility / origin-classification vocab + classify_source(url); domain coverage expanded run 12 for 4 previously-thin sectors (designer_origin, visual_archive, independent_criticism, institutional)
  report_schema.py    # Report/Signal/CollectionWindow dataclasses, validate_report(), save/load/list by date; get_signal_status_history(signal_id, all_reports) (run 12) surfaces a signal's volatility/confidence trend across reports instead of a static dormancy label
  summarize.py        # calls Claude to produce a report; prompt MUST follow doc section 21's objective tone; max_tokens=4000 (fixed run 8, was 2000 and truncated real API output)
  server.py           # MCP tools: crawl_fashion_trends, get_cached_trends, search_trends, list_reports, get_report — now uses shared DEFAULT_OUTPUT_FILE constant (run 8)
  run.sh               # runs the full pipeline: crawler.py -> summarize.py (classify+summarize+save dated report). Fixed in run 1 — no longer stale.
  test_tools.py       # tests the OLD raw-cache pipeline, unrelated to report_schema — leave alone unless migrating it
  manual_sample.py    # helper for the manual TikTok/Pinterest sampling workflow; enforces non-empty human_editor_note
  validate_all_reports.py  # CI check — runs validate_report() against every file in data/reports/, see .github/workflows/validate-reports.yml; also runs derive_confidence() as a non-blocking warning (run 8)
  audit_confidence.py # reusable script (run 7) comparing assigned confidence vs. derive_confidence() across all reports; used for periodic confidence/dormancy review, not wired into CI
  check_field_coverage.py # reusable script (run 25) enumerating every Report/Signal schema field and flagging any that's neither typed in reports.ts nor referenced in a .tsx file — the structural fix for the "claimed but not shown" bug pattern (human_editor_note/thin_week_note/revision_history all shipped in data before they were ever rendered); non-blocking, not wired into CI
  check_heading_patterns.py # reusable script (run 22, revisited run 29) — heuristic scan for the recurring styled-<p>-as-heading bug that ESLint/jsx-a11y cannot catch; not wired into CI, manual/heuristic
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
    search/page.tsx, search/SearchClient.tsx  # client-side facet filter (source sector,
      confidence, volatility) over getSearchIndex() in reports.ts (run 12); full-text
      search (Pagefind) deliberately deferred
    about/page.tsx        # doc sections 37/38
    glossary/page.tsx     # ~29 terms from aesthetic_terms/cultural_references/top_signals[].name across all reports, deduped, wire-service definitions (shipped run 20)
    case-study/page.tsx   # doc section 33, portfolio framing
    layout.tsx           # site-wide <title>/description metadata — keep in sync with rebrand, this has gone stale before
    sitemap.ts, robots.ts  # added run 5
    rss.xml/route.ts      # RSS feed over the report archive
  lib/
    reports.ts           # archive data layer, reads data/reports/*.json; homepage reads off this too (trends.ts retired run 13, confirmed gone — do not re-add); also exposes getSearchIndex() (run 12) for the /search facet filter and getConsecutiveThinWeekCount()/getLatestReport() helpers (run 13)
    site.ts               # shared SITE_URL/SITE_NAME constants for metadata/sitemap/robots/JSON-LD
docs/
  ARI3LLA INDEX.txt      # source concept doc, read-only reference, don't edit
  CHANGELOG.md           # master INDEX — one paragraph + link per run, chronological, PDT/PST timestamps
  changelog-entries/*.md # full per-run changelog detail (run-00-branch-setup.md .. run-16.md), linked from CHANGELOG.md
  PROMPT_CHANGELOG.md    # dedicated review trail for summarize.py's prompt instructions (added run 15, reconstructed retroactively from git history)
  PROJECT_STRUCTURE.md   # intended end-state tree with per-entry notes
  agent-logs/*.md        # per-agent working logs from the overnight build — provenance detail, not the master log
  agent-logs/live-crawl-2026-07-06-real-output.json  # real crawler.py+summarize.py output (run 8), saved for reference, not merged into data/reports/ (collided with existing curated date)
  agent-logs/fashion-week-calendar-research.md  # NYFW/LFW/MFW/PFW run ~Sept 8 - Oct 6, 2026 (run 16 research) — see institutional-knowledge note below
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
   **When adding new page copy/sections, manually check for the styled-`<p>`-as-heading
   bug** (a `<p>` with heading-scale styling instead of a real `<h1>`-`<h6>`) — this has
   recurred 3+ times across runs and jsx-a11y/ESLint cannot detect it (confirmed run 22:
   it only checks tag semantics, not computed visual styling), so it needs an actual
   visual/structural read, not just a lint pass.
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
7. **When multiple subagents work concurrently on the same branch/working tree, scope any
   git revert to the exact files you personally touched.** If you need to undo your own
   exploratory changes, use `git checkout -- <exact-file-path>` or `git restore
   <exact-file-path>` per file — never a bare `git checkout .` / `git restore .` / `git
   clean`, which can silently wipe out other agents' concurrent uncommitted work in the
   same tree. This happened for real in run 8: an agent's broad cleanup of its own
   `summarize.py`/`trends_raw.json` exploration also erased two other agents'
   unrelated-file edits (`server.py`, `validate_all_reports.py`); both had to be redone from
   the original agents' logged specs. Caught only because the coordinator diffed actual
   working-tree state against each agent's described changes before committing.

8. **Avoid hardcoded counts/date-ranges in docs that will go stale.** README/
   PROJECT_STRUCTURE's report-count and dated-file-list claims went stale twice
   (doc-sync runs 18 and 23) because they're manually maintained numbers that drift
   every time a new report is added. Run 24 replaced them with pointers to the live
   `/archive` page or `data/reports/` instead of a specific number/list. When editing
   docs going forward, prefer phrasing that doesn't need updating (point at the live
   source of truth) over a hardcoded count/date-range; if a specific number is
   genuinely useful, tag it with "(count as of <date>, verify against
   data/reports/ for current total)" so it reads as a snapshot, not a guarantee.

9. **A schema field being populated with real data is not the same as it being visible
   to a reader, and a documented instruction is not the same as it actually working.**
   Three separate runs (21, 23, 24) found fields (`human_editor_note`,
   `revision_history`, `thin_week_note`) that were typed, populated, and referenced in
   the site's own transparency claims — but never actually rendered anywhere, making
   those claims false in practice. Run 25's `check_field_coverage.py` is the structural
   fix for this specific pattern. Separately, run 28 found README's own run instructions
   (`bash run.sh`) didn't work from the documented starting point. When a doc or schema
   field makes a claim about what the project does, verify it end-to-end (grep for the
   render site, or actually run the command) rather than trusting that "it's in the
   data/doc" means "it's true of the live site."

10. **A prolonged-silence factual question is not the same as a dormant style signal, and
    must not be closed out the same way.** Dormant STYLE signals (off-duty-varsity,
    layered-tops-styling) get an `EDITORIAL CLOSE-OUT` note declaring them
    resolved/faded — a legitimate call, since discourse volume genuinely dropping is an
    observable fact. A tracked FACTUAL question (e.g. CFDA Fashion Fund winner, CFDA
    Fashion Awards — both past `is_prolonged_silence()`'s threshold as of the
    2026-12-21 report) has no such resolution available from silence: the crawler not
    finding an answer is not evidence the question is settled. Do not declare these
    "closed" or "resolved." Once `is_prolonged_silence()` has been True for several
    consecutive windows running (roughly 3 windows past the initial crossing), mark the
    signal_id **"untracked going forward pending new information"** in prose
    (`human_editor_note`/`index_note`/`archive_tags`) instead of repeating the same
    "still open" note every week. This is a third, honest state — distinct from
    "resolved" and from routine "still tracked" — that lets future report-writing
    agents stop re-litigating the question weekly without fabricating an answer. Any
    agent that later finds real coverage should resume normal tracking/resolution.
    See `is_prolonged_silence()`'s docstring in `src/report_schema.py` and
    `docs/agent-logs/permanent-open-signal-design.md` for full reasoning. No new schema
    enum was added for this — it's expressed as prose in existing free-text fields.

## Institutional knowledge worth knowing before you start

**Fashion-week calendar context (run 16 research,
`docs/agent-logs/fashion-week-calendar-research.md`):** NYFW/LFW/MFW/PFW run roughly
Sept 8 - Oct 6, 2026. The site has logged 5 consecutive thin/low-volatility reports
(07-27 through 08-24) — this is a **verified, expected quiet stretch**, not a crawl or
sourcing failure. Don't treat it as a bug to fix or force `collection_status: "normal"`
before fashion month actually starts around Sept 8, 2026. This isn't obvious from the
schema or code alone — it only shows up if you've read the run-16 agent log, so it's
called out here explicitly.

## Common next steps

See `TODO.md` at repo root for the current authoritative, per-run list (updated every loop
run) — don't duplicate it here. As of run 28, the highest-priority open items ("run 29
candidates" in `TODO.md`) are:

- The run-19 confidence-gate fix (`independent_criticism` added to
  `HIGH_RELIABILITY_SECTORS`) remains untested in practice — revisit once
  `independent_criticism` sources reappear in a report.
- `gh` CLI is unavailable in this environment; CI's real GitHub Actions pass/fail status
  remains genuinely unconfirmed (manual YAML read-throughs only).
- CFDA Fashion Fund winner and CFDA Fashion Awards have both stayed unconfirmed across
  multiple windows — consider whether prolonged silence eventually warrants an explicit
  "awaiting resolution" status rather than repeated carry-forward.
- README's operational instructions are now fixed (run 28) — periodically re-verify them
  against actual pipeline behavior as `summarize.py`/`run.sh` evolve, since this is the
  second time a doc-accuracy sweep found a real, previously-unknown gap.
