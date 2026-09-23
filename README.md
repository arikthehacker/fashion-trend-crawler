# ARI3LLA INDEX

A public, dated archive of style language. It records which style terms appear, where they appear first, and how they move between runway, editorial, social, retail and resale sources. Every claim links to the specific article it rests on.

The site is at [www.ari3lla.com](https://www.ari3lla.com).

ARI3LLA INDEX is not a trend forecaster, a shopping guide or a brand analytics product. It does not predict what will sell or recommend what to buy.

## Status

The published archive is empty. It restarts with the first weekly report whose every claim links to a dated, fetched source.

The 94 reports published before 2026-09-22 were written by an autonomous agent loop that advanced a simulated weekly calendar. 92 of them were written before their own report date, and none linked a claim to a specific article. They are kept, unpublished, in [`data/archive/simulated/`](data/archive/simulated/), and the publish gate described below rejects all of them.

## How it works

1. **Collection.** `src/ingest_rss.py` reads the RSS and Atom feeds listed in [`data/feeds.json`](data/feeds.json). It respects robots.txt, identifies itself, waits between requests to the same host, and stores only the title, link and dates of each item. Items without a publish date are skipped, because an undated item can't be evidence.
2. **Item store.** Items go into a local SQLite database built from [`db/migrations/`](db/migrations/). Each outlet is mapped to a source sector by `src/taxonomy.py`, with the date each mapping took effect. The database is local data and is not committed.
3. **Reports.** A weekly report is a JSON file in `data/reports/`. Each signal lists its `evidence_items`, and each item records a URL, a publish date and a retrieval date.
4. **Publish gate.** `src/validate_all_reports.py` runs in CI on every push. It fails the build if a report is dated after the day it is published, if any signal or thin-week summary lacks evidence, if an evidence URL is an outlet homepage, or if evidence was published after the report date.
5. **Site.** A static Next.js site in `web/` builds the archive, report pages, per-signal histories, full-text search (Pagefind) and an RSS feed. Report pages list each signal's linked evidence.

Drafting a report from the item store is not built yet. `src/summarize.py` and `src/crawler.py` are from the earlier pipeline. The crawler collects headlines only, without publish dates, so its output can't pass the publish gate.

## Sources

Sources are grouped by sector because each sector has different incentives. The sectors are designer origin, runway, editorial, independent criticism, trade intelligence, institutional, visual archive, retail, resale, social, and street or user-generated.

`data/feeds.json` currently lists 66 feeds: 52 editorial, 7 independent criticism, 3 institutional, and 1 each for retail, resale, trade intelligence and visual archive. Coverage leans heavily toward editorial. Brand, retail and resale sites rarely publish dated feeds, and social platforms are never scraped. Social data will come from official APIs (Reddit, Google Trends, Pinterest), with signals from TikTok and similar platforms added by hand through `src/manual_sample.py`. Runway images are linked and never rehosted.

## Classification

Each signal has a type, such as a garment or an aesthetic term, and three labels from the controlled vocabularies in `src/taxonomy.py`:

- **Confidence:** low, medium, high, archival.
- **Volatility:** stable, emerging, seasonal, volatile, flash, microtrend, recurring, revival, long-tail, saturated, declining.
- **Origin:** designer originated, editorial amplified, retail adopted, social amplified, platform native, archive revival, unclear.

Social signals are treated as high-noise by default. Editorial coverage counts as one source sector among several, because editorial media is also shaped by commerce, PR and platform attention. The `human_editor_note` field on each signal is written by the editor and never by software.

## Running it

Python 3.10 or later, and Node 20.

```bash
pip install -r requirements.txt

# item store: create or migrate the local database, then show counts
python src/item_store.py init
python src/item_store.py stats

# collection
python src/ingest_rss.py ingest      # fetch every feed in data/feeds.json
python src/ingest_rss.py discover    # find feeds for outlets in src/taxonomy.py
python src/ingest_rss.py sections    # prefer an outlet's fashion or style section feed

# checks (CI runs all of these)
python src/test_publish_gate.py
python src/test_item_store.py
python src/test_ingest_rss.py
python src/validate_all_reports.py

# site
cd web
npm ci
npx eslint .
npm run build        # static export to web/out, then the Pagefind search index
```

`src/summarize.py` calls the Claude API and needs `ANTHROPIC_API_KEY`. Copy `.env.example` to `.env` and set the key there.

## MCP server

`src/server.py` is an MCP server with five tools: `crawl_fashion_trends`, `get_cached_trends`, `search_trends`, `list_reports` and `get_report`. The report tools read `data/reports/`, which is empty. The crawl and search tools use `trends_raw.json`, a cache from the old crawler, and return an error until the crawler has run. None of the tools read the item store yet.

## Repository layout

```
src/            Python: ingestion, item store, taxonomy, report schema, checks, MCP server
db/migrations/  SQLite schema for the item store
data/
  feeds.json        the feeds collection reads
  reports/          published reports (empty)
  archive/simulated/  the withdrawn simulated reports, unpublished
web/            Next.js site (app/ pages, lib/ data layer, vercel.json headers)
docs/           concept document, methodology notes, historical agent logs
.github/        CI: Python checks and tests, site lint
```

## Site standards

- Every page shares one header, navigation and footer, and the current page is marked for screen readers.
- The site targets WCAG 2.2 AA.
- It sends a Content-Security-Policy and related security headers, and publishes a `security.txt`.
- Analytics use Vercel Web Analytics, which sets no cookies and reports only aggregate counts. Details are on the [privacy page](https://www.ari3lla.com/privacy).

## Contact and corrections

Errors can be reported by email to ariella@duck.com or as a [GitHub issue](https://github.com/arikthehacker/fashion-trend-crawler/issues). A published report is corrected with a dated note and is never silently edited.

The index's own classifications and report text are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Linked articles belong to their publishers.
