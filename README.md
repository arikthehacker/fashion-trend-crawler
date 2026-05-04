# fashion-trend-crawler 

### a tool for the busy human who still wants to know what's going on in fashion

---
General purpose web crawler and MCP server that extracts headlines 
from fashion publications and exposes them as tools for AI agents.

Mainly built to stay current with fashion trends without manual 
browsing. Longer term goal is a landing page that surfaces trend
summaries for people who don't have time to keep up themselves.

---

## what it does

- crawls public fashion pages starting from seed urls
- follows links up to a set depth using bfs
- respects robots.txt & only goes where it's allowed
- extracts headlines from every page it visits
- saves everything to json for analysis
- exposes three mcp tools so an ai agent can use it directly

## mcp tools

| tool | what it does |
|---|---|
| `crawl_fashion_trends` | crawls all sources and saves fresh headlines |
| `get_cached_trends` | returns the last crawl without hitting the web again |
| `search_trends` | searches cached headlines by keyword |

## how to run it

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

## default sources i'm currently using

- vogue.com/fashion
- whowhatwear.com
- hypebeast.com/fashion

### you can point it anywhere though:
```bash
python src/crawler.py https://www.elle.com https://www.harpersbazaar.com
```

## what's next

- [ ] landing page for trend summaries
- [ ] claude integration for ai-generated trend analysis
- [ ] more fashion sources & nuance (tiktok is one of the top hubs of fashion trends: need to find how to utilize this)
- [ ] scheduled crawls so it stays fresh automatically

---

*TLDR: I miss having time to read vogue.*
