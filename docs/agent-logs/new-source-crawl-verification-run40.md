# Run 40: crawl verification of run 39's new sources

Follow-up to run 39, which added scmp.com and thenationalnews.com to
`FASHION_SOURCES` but only checked reachability via WebFetch, not the
project's real crawl path (`requests` + `get_robots_parser()` in
`src/crawler.py`). Tested both directly with `crawler.get_robots_parser()`,
`crawler.is_allowed()`, and `crawler.crawl()` using the project's real
`HEADERS` User-Agent (`fashion-trend-crawler/1.0 (educational project)`).

## scmp.com — WORKS

- `https://www.scmp.com/lifestyle/fashion-beauty`
- robots.txt: fetched fine, `is_allowed()` -> `True` (not disallow_all/allow_all
  fallback, real robots.txt parsed).
- `requests.get()`: HTTP 200, no Cloudflare challenge.
- `crawl(max_depth=0, max_pages=5)`: 1 page result, 48 headlines extracted
  from h1/h2/h3 tags. Confirmed working end-to-end with the real crawl path.

## thenationalnews.com — REACHABLE BUT YIELDS ZERO HEADLINES (not a robots/UA block)

- `https://www.thenationalnews.com/lifestyle/fashion`
- robots.txt: fetched fine, `is_allowed()` -> `True`.
- `requests.get()`: HTTP 200, 840KB of HTML, no block/403/Cloudflare
  challenge — this is NOT the run-18-style false-block bug.
- `crawl(max_depth=0, max_pages=5)`: 0 results. Root cause: the raw HTML
  response contains **zero `<h1>`/`<h2>`/`<h3>` tags at all**
  (`soup.find_all(["h1","h2","h3"])` returns an empty list). The page title
  and description are present in `<title>`/`<meta>`, so the request itself
  succeeded, but the headline markup this crawler relies on is evidently
  injected client-side (JS-rendered, likely Next.js/React) and isn't present
  in the static HTML `requests` fetches.

## Recommendation

scmp.com is confirmed good, no action needed. thenationalnews.com is not
blocked (so it's a different failure class from run 18's tokyofashion.com
UA issue — no header/UA fix will help here), but it currently contributes
zero data to `trends_raw.json` because the crawler's simple h1/h2/h3
static-HTML scraping approach can't see the content. Left in
`FASHION_SOURCES` per instructions (not removed here) — a future run should
decide whether to drop it, or extend the crawler to parse a different
selector/JSON-LD/embedded state if the headlines are recoverable without a
headless browser.
