# ARI3LLA INDEX
### weekly style signal report — live at [ari3lla.com](https://ari3lla.com)

---

ARI3LLA INDEX is an experimental weekly style signal report that tracks
recurring style language, silhouettes, materials, aesthetics, and cultural
signals across public web sources.

Most trend tools are built for brands, marketers, and retail forecasting.
This project is different: it is not trying to predict what will sell. It
is trying to preserve what style culture is talking about, how signals move
across source sectors, and how platform-driven trends become market
language.

---

## Overview

ARI3LLA INDEX is a source-linked, recurring style signal report. It is not
a fashion blog, an influencer trend page, a shopping guide, or a brand
forecasting tool. It treats trends less as shopping instructions and more
as cultural evidence — a dated record of what style culture is naming,
repeating, reviving, and absorbing.

The project combines a Python crawler, an MCP server, LLM-assisted
extraction and summarization, and a Next.js editorial frontend.

## Live Site

The current report is live at **[ari3lla.com](https://ari3lla.com)**.

## Why This Exists

Style discourse moves quickly across platforms, editorial media, retail
copy, and brand campaigns. Signals are usually flattened into "trends"
without source context, historical memory, or incentive analysis. Most
existing fashion analytics tools ask what is trending, what will sell, or
what should brands produce. ARI3LLA INDEX asks what is being observed,
where, how often, across which source types, and what that reveals about
style culture — before it disappears into the feed.

## Methodology

Signals are not ranked by popularity alone. Reports consider recurrence,
source diversity, source type, specificity of language, visual coherence,
historical continuity, and persistence across reporting periods.

Social/platform signals (TikTok, Instagram, etc.) are treated as
high-noise by default. They may indicate cultural velocity, but they are
not treated as stable style evidence unless supported by recurrence across
multiple sectors or reporting periods. Editorial coverage is treated as
one source sector among several, not as final authority, since editorial
media is itself shaped by commerce, PR, and platform attention.

## Source Sectors

Sources are classified rather than treated as equal:

1. designer-origin sources (brand sites, lookbooks, press releases)
2. runway sources
3. editorial/magazine sources
4. commerce/retail sources
5. social/platform sources
6. visual archive/search sources
7. independent criticism
8. institutional/historical sources
9. street/user-generated sources
10. resale/secondhand market sources

## Signal Taxonomy

Each observed signal is classified along several axes:

- **type** — garment, silhouette, material, color, styling behavior,
  aesthetic term, commerce language, cultural reference, etc.
- **confidence** — low / medium / high / archival
- **volatility** — stable, emerging, seasonal, volatile, flash,
  microtrend, recurring, revival, long-tail, saturated, declining
- **origin classification** — designer-originated, editorial-amplified,
  retail-adopted, social-amplified, platform-native, archive revival,
  unclear

## Architecture

```
public web sources
 ↓
crawler / source collector
 ↓
raw extracted items
 ↓
source-sector classifier
 ↓
LLM extraction and clustering
 ↓
structured JSON report
 ↓
human/editorial review
 ↓
report archive
 ↓
Next.js frontend
 ↓
public weekly report
```

## Data Pipeline

- crawls public fashion pages starting from seed urls
- follows links up to a set depth using BFS
- respects robots.txt and only goes where it's allowed
- extracts headlines/signals from every page it visits
- saves everything to JSON for analysis
- dated reports are archived so the project accumulates a historical
  record over time, rather than only showing the current week
- each report is validated against a controlled schema
  (`src/report_schema.py`) before it can be considered part of the
  archive, and CI (`.github/workflows/validate-reports.yml`) re-runs that
  validation on every push/PR against everything in `data/reports/`;
  the same workflow's `lint-web` job runs ESLint (including
  `eslint-plugin-jsx-a11y` accessibility rules) against `web/` on every
  push/PR
- confidence can be derived deterministically from source-corroboration
  count and source-sector diversity (`derive_confidence()`), tracked
  against a manual "confidence_source" so editorial judgment calls stay
  distinguishable from mechanically derived ones — this is opt-in and not
  yet auto-applied on save
- overwriting an existing dated report requires a `revision_history`
  entry (reason + timestamp) rather than a silent overwrite, so the
  archive can't quietly rewrite its own past

## Archive & Reporting Surfaces

- `/archive` — chronological list of all dated reports
- `/reports/[date]` — full report render, one page per collection window
- `/timeline` — reverse-chronological index of every signal across all
  reports
- `/signals/[slug]` — longitudinal view of a single signal's recurrence,
  volatility, and confidence across reporting periods
- `/methodology`, `/taxonomy`, `/sources`, `/about` — how signals are
  evaluated, the full source-sector and confidence/volatility taxonomy,
  and the outlet lists behind it
- `/glossary` — plain-language definitions of aesthetic terms and cultural
  references, but only for terms that actually appear in an archived
  report (sourced from `data/reports/*.json` at build time, not an
  abstract style dictionary)
- `/case-study` — project write-up
- `/search` — full-text search over report prose (Pagefind, indexed at
  build time via a `postbuild` step against the static export) alongside
  client-side facet filters (source sector, confidence, volatility)
- `/rss.xml` — RSS feed over the report archive
- the homepage includes a "This Week's Index" module — a condensed
  metrics summary of the latest report (doc section 27/28), distinct from
  the full per-date report render at `/reports/[date]`
- report pages carry `NewsArticle` + `Dataset` JSON-LD (the latter with a
  CC BY 4.0 license URL and a `DataDownload` pointing at the report's raw
  JSON), a stable "Cite as" line, and a sitemap/robots setup for
  discoverability; heading structure follows WCAG hierarchy rather than
  styled paragraphs standing in for headings
- each report page also has a human-visible "download raw data" link to
  `/data/reports/<date>.json` — a static copy of that date's report JSON,
  placed in `web/public/data/reports/` at build time by
  `web/scripts/copy-reports.mjs` (invoked from `next.config.ts` on every
  build, plus redundantly via the `prebuild` npm script)

## Transparency & Editorial Disclosures

Methodology and About pages carry explicit Corrections, Editorial
Independence, and AI-Involvement sections — what gets corrected and how,
that editorial judgment (not an advertiser or platform) decides what
signals matter, and where AI is and isn't used in the pipeline. A
"thin week" fallback state exists in the schema so a genuinely low-signal
reporting period is disclosed as such rather than padded with
manufactured signals.

## Manual / Compliant Social Sampling

TikTok and Pinterest signals are never scraped. A manual-sampling
workflow (`src/manual_sample.py`, `docs/manual-sampling-template.md`)
lets a human add a social-origin signal sourced from an official
platform trend report or API, with a required `human_editor_note`
explaining why it is or isn't likely to be durable. This workflow has
been exercised against real reports (Pinterest and TikTok sources so
far) opportunistically, not on a fixed schedule, not just designed.

## MCP / LLM Layer

An MCP server exposes the crawl and cache as tools an AI agent can call
directly:

| tool | what it does |
|---|---|
| `crawl_fashion_trends` | crawls all sources and saves fresh headlines |
| `get_cached_trends` | returns the last crawl without hitting the web again |
| `search_trends` | searches cached headlines by keyword |
| `list_reports` | lists all archived dated reports |
| `get_report` | returns one archived report by date |

An LLM layer (Claude) then extracts, clusters, and summarizes the raw
material into a structured, source-aware report rather than a hyped list
of "must-haves."

### API key setup

`summarize.py` calls the Claude API and needs `ANTHROPIC_API_KEY` set. Copy the
example env file, then fill in a real key:

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=<your real key>
```

`.env` is git-ignored and never committed. `summarize.py` loads it automatically
via `python-dotenv` (`load_dotenv()`), so no manual `export` is required.

### How to run it

`run.sh` and the pipeline scripts assume you're running from inside `src/`, not the
repo root (they call `python crawler.py`/`python summarize.py` with no `src/` prefix).

**`crawler.py` (and therefore `run.sh`, which calls it) is currently off-limits for
unattended/autonomous runs pending a human-supervised live test.** Two hang-fixes have
been implemented and locally verified (a hard-deadline `ThreadPoolExecutor` wrapper and
an incremental-flush mitigation), but neither has been proven against real, live sources
yet — prior unattended attempts left hung `python crawler.py` processes running for over
an hour. If you're running this yourself interactively and can watch/kill the process,
that's a different risk profile than an unattended agent run; either way, expect this
note to be removed once a supervised live run confirms the fix.

```bash
# install dependencies (requirements.txt covers crawler/summarize/server/manual_sample;
# includes brotli, required for hosts that serve Brotli-compressed responses — see
# docs/agent-logs/dieworkwear-crawl-verification-run55.md)
pip install -r requirements.txt mcp

cd src

# run the full pipeline: crawl -> classify -> summarize -> save a dated report
bash run.sh

# or run pieces individually
python crawler.py          # just the crawler, writes trends_raw.json
python summarize.py        # classify + summarize + save (requires ANTHROPIC_API_KEY)
python test_tools.py       # just the tests
python server.py           # just the mcp server
```

**Re-running `summarize.py` against a date that already has an archived report**
(e.g. correcting today's report after already running it once) requires an explicit
correction reason — it will not silently overwrite:

```bash
python summarize.py --revision-reason "why this changed" --corrected-at "2026-07-07"
```

### default sources currently in use

See `src/crawler.py`'s `FASHION_SOURCES` list for the current, up-to-date set (it has
grown well past the original 3 — check the file directly rather than a list here, since
it changes as source-diversity work continues).

You can point the crawler at different sources for a one-off run:
```bash
python crawler.py https://www.elle.com https://www.harpersbazaar.com
```

## Ethical AI Statement

This project uses AI for summarization and organization, not for replacing
designers, journalists, stylists, archivists, or cultural analysis. The
goal is to make public style discourse easier to scan while keeping human
interpretation central. Language models are used as archival assistants,
not as taste authorities — the model does not decide what matters, the
methodology does.

Sourcing follows a few principles: respect robots.txt, avoid bypassing
platform protections, favor official APIs where possible, cite/link
sources rather than reproducing copyrighted content, and be transparent
about limitations.

## Roadmap

- [x] landing page for weekly reports — live at [ari3lla.com](https://ari3lla.com)
- [x] Claude integration for AI-assisted trend extraction
- [x] structured JSON report schema saved by date
- [x] archive page (`/archive`, `/reports/[date]`) — a historical record,
  not just a current snapshot
- [x] methodology page (`/methodology`) and taxonomy page (`/taxonomy`)
- [x] CI validation of the report archive on every push/PR
- [x] compliant handling of social/platform signals — manual sampling,
  exercised against real reports, not automated ingestion
- [x] signal timelines and longitudinal tracking per signal (`/timeline`,
  `/signals/[slug]`)
- [x] homepage rebuilt off `reports.ts`; legacy `web/lib/trends.ts` retired
- [ ] source-sector-aware crawling (more nuance beyond editorial/retail)
- [ ] scheduled crawls so the archive stays fresh automatically
- [ ] a live `crawler.py` + `summarize.py` run merged into the archive
  (one has succeeded against real sources — see Limitations)

## Limitations

- every report currently in `data/reports/` is hand-authored or
  WebSearch-researched, not produced by a live `crawler.py` run merged
  into the archive. A real crawl + summarize pass against live sources
  has succeeded once (119 headlines from Vogue/WhoWhatWear/Hypebeast,
  summarized via the Claude API), but its output collided with an
  existing dated report and was deliberately not merged — it's saved for
  reference at `docs/agent-logs/live-crawl-2026-07-06-real-output.json`.
  A `revision_history` mechanism now exists in the schema to resolve this
  kind of collision, but the pipeline doesn't route through it yet.
- source coverage is currently weighted toward editorial and retail; social
  and designer-origin sources are underrepresented
- signal classification depends on human/editorial review, which does not
  yet run on a fixed cadence
- historical continuity claims are limited until the archive accumulates
  more than a few reporting periods — see the live archive at
  [ari3lla.com/archive](https://ari3lla.com/archive) or `data/reports/` for
  the current count rather than a number stated here (this has gone stale
  twice already; see `docs/agent-logs/doc-sync-run18.md` and `-run23.md`)
- confidence can be derived deterministically (`derive_confidence()`) but
  is not yet auto-applied — it currently runs as a non-blocking warning
  in CI, flagging mismatches for human review rather than overwriting them
- this project does not use paid trend-data feeds; everything is derived
  from public, crawlable, or API-accessible sources

## Screenshots

*(placeholder — screenshots of the current report and archive views go here)*

## What I Learned

Building the crawler, MCP server, and LLM summarization layer was the
tractable part. The harder and more valuable part has been designing a
taxonomy that keeps a language model useful without letting it decide what
counts as a "trend" — separating what a designer made, what editors said
it meant, what retailers sold it as, and what social platforms renamed it.
That distinction, more than any single piece of tech, is what turns a
scraper into something closer to a research index.

## Project Structure

```
fashion-trend-crawler/
  requirements.txt             # Python deps for the crawler/summarize/server pipeline
                                #   (requests, beautifulsoup4, anthropic, brotli)
  src/
    crawler.py                # core crawler — bfs, robots.txt, headline extraction
    server.py                  # mcp server, five tools (crawl/cache/search/list/get)
    summarize.py               # calls claude api to generate trend summary
    report_schema.py           # Report/Signal/CollectionWindow schema, validate/save/load,
                                #   derive_confidence(), revision_history
    taxonomy.py                 # signal/source taxonomy definitions + classify_source(url)
    manual_sample.py           # compliant manual social-signal sampling helper
    validate_all_reports.py    # CI check against every file in data/reports/
    audit_confidence.py        # periodic confidence/dormancy review script, not wired into CI
    check_field_coverage.py    # flags schema fields not typed/rendered in web/ (not wired into CI)
    check_heading_patterns.py  # heuristic scan for styled-<p>-as-heading bug (not wired into CI)
    generate_archive_manifest.py  # produces a manifest of report-page URLs/hashes for a
                                #   human operator to feed into archive.org Save Page Now,
                                #   once a real SITE_URL exists; not wired into CI
    check_signal_reuse_claims.py  # flags a report's own reuse/continuation prose naming a
                                #   signal_id not present in that report's own top_signals
                                #   (run 61); not wired into CI, standing periodic-audit step (run 62)
  data/
    reports/                   # dated JSON reports — see /archive on the
                                #   live site or `ls data/reports/` for the
                                #   current count/date range (deliberately
                                #   not enumerated here, see run 24 log)
  web/                          # next.js editorial site
    app/
      page.tsx                  # homepage — reads off reports.ts (trends.ts retired);
                                #   includes "This Week's Index" condensed metrics module
      archive/                  # historical report list
      reports/[date]/           # per-date report render
      timeline/                 # reverse-chronological signal index
      signals/[slug]/           # per-signal longitudinal view
      search/                   # Pagefind full-text search + client-side facet filters
      glossary/                  # archive-sourced definitions of observed aesthetic terms
      methodology/, taxonomy/, sources/, about/  # static reference pages
      case-study/                # portfolio case study
      sitemap.ts, robots.ts, rss.xml/  # SEO / syndication
      icon.tsx                  # route-segment metadata file — Next auto-generates the
                                #   favicon (ImageResponse, no binary asset); force-static
                                #   like sitemap.ts/robots.ts
    scripts/
      copy-reports.mjs           # copies data/reports/*.json into public/data/reports/
                                #   for the static export's raw-data download links
    lib/
      reports.ts                 # archive data layer, reads data/reports/*.json
      site.ts                     # shared SITE_URL/SITE_NAME constants
  .github/workflows/validate-reports.yml  # CI: validates the archive (`validate` job)
                                #   and lints web/ with ESLint + jsx-a11y (`lint-web` job)
                                #   on push/PR
  run.sh                        # full pipeline runner
```

---

ARI3LLA INDEX is an independent style signal archive. Reports are
generated from public source material and structured for historical
reference. No purchasing recommendation is implied.
