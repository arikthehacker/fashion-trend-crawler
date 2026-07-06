# Crawler hang investigation (run 67) — static code review only

Scope: read `src/crawler.py` line by line looking for an indefinite-hang mechanism, per the
run 62/65/66 reports of hung processes despite run 63/63b completing successfully. No code
was executed or modified.

## What checked out fine

1. **Every `requests.get()` call has an explicit `timeout`.** Robots.txt fetch (`get_robots_parser`,
   line 125) and page fetch (`crawl`, line 173) both pass `timeout=8`. No missing/default-timeout
   network call anywhere in the file.
2. **BFS termination logic is correct.** `while queue and len(results) < max_pages` bounds page
   count; `depth > max_depth` is checked before any work is done on a dequeued item; `visited` is
   checked for skip and then `.add(url)`-ed *before* the slow `requests.get()` call (line 170, before
   line 173), so a slow response cannot cause the same URL to be re-queued/re-processed. Outbound
   links are also filtered by `full_url not in visited` before enqueueing. `max_depth`/`max_pages`
   are never mutated, so no path exists where the loop's own bookkeeping breaks.
3. `get_robots_parser`'s fetch is wrapped in `try/except Exception`, so even a timeout there can't
   propagate into an unbounded wait — worst case it falls back to "assume allowed."

## The likely mechanism: `timeout=` in `requests` does not bound total transfer time

`requests`' `timeout` parameter is a **per-socket-operation** timeout (time-to-first-byte /
time-between-reads), not a wall-clock cap on the whole request. If a server accepts the connection
and then trickles the response body slowly enough that no single read stalls past 8 seconds (e.g.
a byte or a small chunk every few seconds, or a very slow-but-nonzero stream), `response.text` in
`crawl()` (line 173, via the implicit `response.text` access at line 179) can block for an
arbitrarily long time without ever tripping the timeout. This is a well-documented `requests`
gotcha and is consistent with the symptom pattern here: most of the ~15 `FASHION_SOURCES` hosts
respond normally (hence runs 63/63b completing cleanly), but if even one host is slow/misbehaving
in this specific way, that single `crawl()` call for that source stalls forever and the whole
`crawl_all_sources()` loop (which calls `crawl()` sequentially, no per-source timeout of its own)
never proceeds to `json.dump` or returns — matching "hangs indefinitely" and "processes still
running" from runs 62/65/66.

No other candidate mechanism was found in this file (no threads, no recursion, no unbounded
regex/string operations, no other network calls).

## Proposed fix (NOT applied — unverified without running)

Two complementary, minimal changes:
- Pass timeouts as a tuple `timeout=(8, 15)` (connect, read) is still per-read, so it doesn't fully
  fix this — the real fix is to cap total elapsed time per request, e.g. wrap the `requests.get()`
  call in `crawl()` with `signal.alarm` (POSIX-only) or, more portably, use
  `requests.get(url, headers=HEADERS, timeout=8, stream=True)` plus manually reading
  `response.iter_content()` with an overall deadline check (`time.monotonic()`), aborting/closing
  the connection if total elapsed time exceeds a cap (e.g. 20s).
- Simpler stopgap: run each `crawl_all_sources()` source call under a hard wall-clock watchdog
  (e.g. `concurrent.futures.ThreadPoolExecutor.submit(...).result(timeout=60)`), so one
  misbehaving host can't block the whole pipeline even if the underlying `requests` timeout gotcha
  isn't fixed.

## Alternative/complementary explanation

Even independent of the above, this is likely an **environment/host-conditional** issue rather
than a logic bug: one or more entries in `FASHION_SOURCES` may be an intermittently slow or
CDN-throttled host (e.g. behind aggressive rate limiting that responds just fast enough to avoid
the connect/read timeout but slow enough overall to appear to hang). Worth checking access logs /
timing on individual sources if this recurs, in addition to the code-level fix above.
