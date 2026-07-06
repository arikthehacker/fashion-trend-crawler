# dieworkwear.com crawl verification (run 55)

Follow-up to run 54, which added `dieworkwear.com` to `FASHION_SOURCES` but only
verified it via WebFetch. This run actually exercised the project's own
`src/crawler.py` functions (`get_robots_parser()`, `is_allowed()`, `crawl()`)
with the project's real `HEADERS` User-Agent (`fashion-trend-crawler/1.0
(educational project)`) and the `requests` library, no WebFetch involved.

## Results

- `get_robots_parser()` / `is_allowed("https://dieworkwear.com")` -> **True**.
  robots.txt is fetched fine and is permissive, as run 54 found.
- `crawl("https://dieworkwear.com", max_depth=1, max_pages=10)` -> **0 pages,
  0 headlines.** Not client-side rendering this time -- something else.

## Root cause

`requests.get()` against dieworkwear.com returns `Content-Encoding: br`
(Brotli, served via Cloudflare/Sucuri in front of the WordPress site).
`requests` only auto-decompresses Brotli if the optional `brotli` or
`brotlicffi` package is installed -- neither is installed in this project's
environment (checked: `ModuleNotFoundError` for both, and there is no
`requirements.txt` pinning either). Confirmed directly:

```
Content-Encoding: br
r.content[:20] = b'\x8b\xb1)\x8cH\xcc\x07@#t\xf8\x9c\xf7\xff{3\xfd\xef\xf1\xcf'  # raw brotli bytes
```

Because `requests` can't decompress it, `response.text` is garbled binary,
`BeautifulSoup` finds 0 `h1`/`h2`/`h3` tags, `crawl()`'s "only save pages that
had titles" check silently drops the page, and `crawl_all_sources()` just logs
0 pages crawled for this source with **no error or warning** -- identical
failure-mode shape to thenationalnews.com in run 40, but a different root
cause: not JS rendering, a missing optional dependency for a compression
scheme this specific host happens to use.

## Verdict

`dieworkwear.com` is currently a **non-functional entry** in `FASHION_SOURCES`
under this project's actual crawl path -- it contributes 0 pages/headlines
every run, silently. It is not disallowed by robots.txt and is not JS-heavy;
this is fixable (installing `brotli` or `brotlicffi`, or explicitly setting
`Accept-Encoding: gzip, deflate` in `HEADERS` to stop the server from serving
Brotli at all), but as committed it does not work. Flagging for a decision:
either (a) add `brotli`/`brotlicffi` as a project dependency, (b) restrict
`Accept-Encoding` in `HEADERS`, or (c) pull `dieworkwear.com` back out of
`FASHION_SOURCES` like `thenationalnews.com` was in run 41, leaving
`independent_criticism` unreachable again. Left `FASHION_SOURCES` untouched
pending that decision.
