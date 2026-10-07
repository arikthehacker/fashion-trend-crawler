# ARI3LLA INDEX

[![Validate reports](https://github.com/arikthehacker/fashion-trend-crawler/actions/workflows/validate-reports.yml/badge.svg)](https://github.com/arikthehacker/fashion-trend-crawler/actions/workflows/validate-reports.yml) ![python](https://img.shields.io/badge/python-3.10%2B-3776ab) ![node](https://img.shields.io/badge/node-20-339933) ![site](https://img.shields.io/badge/site-ari3lla.com-black)

ARI3LLA INDEX is a public, dated archive of style language. It records which style terms appear, where they show up first, and how they move between runway, editorial, social, retail and resale sources, and every claim links to the specific article it rests on. This repository began as fashion-trend-crawler and is now the pipeline behind the site at [www.ari3lla.com](https://www.ari3lla.com). It is not a trend forecaster, a shopping guide or a brand analytics product.

## quickstart

```
git clone https://github.com/arikthehacker/fashion-trend-crawler.git
cd fashion-trend-crawler
python src/validate_all_reports.py
```

The publish gate reads every report in `data/reports/` and checks it against the rules below. It is what CI runs on each push, and it needs no setup.

expected output:

```
OK: all 2 report(s) in data/reports/ passed schema validation and the publish gate.
```

## how it works

1. **Collection.** `src/ingest_rss.py` reads the 97 RSS and Atom feeds in [`data/feeds.json`](data/feeds.json). It respects robots.txt, identifies itself, waits between requests to the same host, and stores only each item's title, link and dates. Undated items are skipped, because an undated item can't be evidence.
2. **Item store.** Items go into a local SQLite database built from [`db/migrations/`](db/migrations/). `src/taxonomy.py` maps each outlet to a source sector, with the date each mapping took effect. The database is local and is not committed.
3. **Reports.** A weekly report is a JSON file in `data/reports/`. Each signal lists its `evidence_items`, and each item records a URL, a publish date and a retrieval date.
4. **Publish gate.** `src/validate_all_reports.py` fails the build if a report is dated after the day it is published, if any signal lacks evidence, if an evidence URL is an outlet homepage, or if evidence was published after the report date.
5. **Site.** A static Next.js site in `web/` builds the archive, report pages, per-signal histories, full-text search (Pagefind) and an RSS feed.

Each signal carries a type and three labels from the controlled vocabularies in `src/taxonomy.py`: confidence, volatility and origin. The `human_editor_note` on a signal is written by the editor, never by software.

## ari3

ARI3 is the model system behind the index, kept in [`models/`](models/) as frozen, versioned components, each with a model card and preregistered hypotheses. Two parts are frozen today:

- **Retrieval** (`src/rag_retrieve.py`): BM25 over SQLite FTS5, dense cosine search over embeddings from a frozen multilingual sentence encoder (`paraphrase-multilingual-MiniLM-L12-v2`), and a hybrid that fuses the two rankings with reciprocal rank fusion. Filters run first in SQL, so similarity can never admit an item that fails a filter, and ties break by id, so the same inputs always give the same ranking.
- **Perception** (`models/ari3-v0.0.1/`): decides whether an item is about style. The same sentence encoder feeds an L2 logistic regression, with temperature scaling for calibration and split conformal prediction for the items it is unsure about. On 34 held-out items fixed by a SHA-256 split, it scores 0.882 accuracy against a 0.529 majority baseline, and expected calibration error drops from 0.234 to 0.088 after scaling. The numbers, limits and hashes are in [`models/ari3-v0.0.1/MODEL_CARD.md`](models/ari3-v0.0.1/MODEL_CARD.md).

The write-up and the live notebook are at [www.ari3lla.com/ari3](https://www.ari3lla.com/ari3).

## running it

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

# checks (CI runs these)
python src/test_publish_gate.py
python src/test_item_store.py
python src/test_ingest_rss.py
python src/validate_all_reports.py

# site
cd web
npm ci
npm run build        # static export to web/out, then the Pagefind search index
```

`src/summarize.py` calls the Claude API and needs `ANTHROPIC_API_KEY`. Copy `.env.example` to `.env` and set it there.

`src/server.py` is an MCP server with five tools: `crawl_fashion_trends`, `get_cached_trends`, `search_trends`, `list_reports` and `get_report`. The report tools read `data/reports/`.

## history

The project began as fashion-trend-crawler, a weekly crawler that collected fashion headlines and summarized them with the Claude API (`src/crawler.py`, `src/summarize.py`). The 94 reports published before 2026-09-22 came from an autonomous agent loop running a simulated weekly calendar. 92 of them were written before their own report date, and none linked a claim to a specific article. They are kept, unpublished, in [`data/archive/simulated/`](data/archive/simulated/), and the publish gate rejects all of them.

The published archive now holds only reports whose every claim links to a dated, fetched source. The crawler still collects headlines without publish dates, so its output can't pass the gate, and drafting a report from the item store is the next piece.

## corrections

Errors can be reported by email to ariella@duck.com or as a [GitHub issue](https://github.com/arikthehacker/fashion-trend-crawler/issues). A published report is corrected with a dated note, never silently edited. The index's own classifications and report text are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Linked articles belong to their publishers.
