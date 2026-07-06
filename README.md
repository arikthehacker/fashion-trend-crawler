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
  validation on every push/PR against everything in `data/reports/`
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
- `/case-study` — project write-up
- `/search` — full-text search over report prose (Pagefind, indexed at
  build time via a `postbuild` step against the static export) alongside
  client-side facet filters (source sector, confidence, volatility)
- `/rss.xml` — RSS feed over the report archive
- report pages carry `NewsArticle` JSON-LD, a stable "Cite as" line, and a
  sitemap/robots setup for discoverability; heading structure follows
  WCAG hierarchy rather than styled paragraphs standing in for headings

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
been exercised twice against real reports, not just designed.

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

### How to run it

```bash
# install dependencies
pip install requests beautifulsoup4 mcp anthropic

# run the full pipeline
bash run.sh

# or run pieces individually
python src/crawler.py          # just the crawler
python test_tools.py           # just the tests
python src/server.py           # just the mcp server
```

### default sources currently in use

- vogue.com/fashion
- whowhatwear.com
- hypebeast.com/fashion

You can point it anywhere though:
```bash
python src/crawler.py https://www.elle.com https://www.harpersbazaar.com
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
  exercised twice, not automated ingestion
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
  more than a few reporting periods (10 dated reports as of this writing)
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
  src/
    crawler.py                # core crawler — bfs, robots.txt, headline extraction
    server.py                  # mcp server, five tools (crawl/cache/search/list/get)
    summarize.py               # calls claude api to generate trend summary
    report_schema.py           # Report/Signal/CollectionWindow schema, validate/save/load,
                                #   derive_confidence(), revision_history
    taxonomy.py                 # signal/source taxonomy definitions + classify_source(url)
    manual_sample.py           # compliant manual social-signal sampling helper
    validate_all_reports.py    # CI check against every file in data/reports/
  data/
    reports/                   # dated JSON reports (10 as of this writing:
                                #   2026-05-07, -07-06, -07-13, -07-20, -07-27,
                                #   -08-03, -08-10, -08-17, -08-24, -08-31)
  web/                          # next.js editorial site
    app/
      page.tsx                  # homepage — reads off reports.ts (trends.ts retired)
      archive/                  # historical report list
      reports/[date]/           # per-date report render
      timeline/                 # reverse-chronological signal index
      signals/[slug]/           # per-signal longitudinal view
      search/                   # Pagefind full-text search + client-side facet filters
      methodology/, taxonomy/, sources/, about/  # static reference pages
      case-study/                # portfolio case study
      sitemap.ts, robots.ts, rss.xml/  # SEO / syndication
    lib/
      reports.ts                 # archive data layer, reads data/reports/*.json
      site.ts                     # shared SITE_URL/SITE_NAME constants
  .github/workflows/validate-reports.yml  # CI: validates the archive on push/PR
  run.sh                        # full pipeline runner
```

---

ARI3LLA INDEX is an independent style signal archive. Reports are
generated from public source material and structured for historical
reference. No purchasing recommendation is implied.
