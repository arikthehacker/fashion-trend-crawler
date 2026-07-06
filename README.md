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

## MCP / LLM Layer

An MCP server exposes the crawl and cache as tools an AI agent can call
directly:

| tool | what it does |
|---|---|
| `crawl_fashion_trends` | crawls all sources and saves fresh headlines |
| `get_cached_trends` | returns the last crawl without hitting the web again |
| `search_trends` | searches cached headlines by keyword |

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
- [ ] structured JSON report schema saved by date
- [ ] archive page (`/archive`, `/reports/[date]`) — a historical record,
  not just a current snapshot
- [ ] methodology page (`/methodology`) and taxonomy page (`/taxonomy`)
- [ ] source-sector-aware crawling (more nuance beyond editorial/retail)
- [ ] compliant handling of social/platform signals (TikTok, Pinterest)
- [ ] scheduled crawls so the archive stays fresh automatically
- [ ] signal timelines and longitudinal tracking per signal

## Limitations

- source coverage is currently weighted toward editorial and retail; social
  and designer-origin sources are underrepresented
- signal classification depends on human/editorial review, which does not
  yet run on a fixed cadence
- historical continuity claims are limited until the archive accumulates
  more than a few reporting periods
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

Approximate layout — some paths (report schema, taxonomy module, archive
and methodology routes) are actively evolving as the archive/methodology
features are built out.

```
fashion-trend-crawler/
  src/
    crawler.py        # core crawler — bfs, robots.txt, headline extraction
    server.py          # mcp server with three tools
    summarize.py       # calls claude api to generate trend summary
    report_schema.py   # structured report schema (in progress)
    taxonomy.py         # signal/source taxonomy definitions (in progress)
  data/
    reports/           # dated JSON reports, e.g. 2026-05-07.json (in progress)
  web/                 # next.js editorial site
    app/
      page.tsx          # homepage — current report
      case-study/        # portfolio case study
      archive/           # historical reports (in progress)
      methodology/       # methodology page (in progress)
    lib/
      trends.ts          # data layer
  trends_raw.json     # cached crawl output
  trends_summary.json # ai-generated summary
  run.sh              # full pipeline runner
```

---

ARI3LLA INDEX is an independent style signal archive. Reports are
generated from public source material and structured for historical
reference. No purchasing recommendation is implied.
