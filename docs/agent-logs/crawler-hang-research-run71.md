# Crawler hang bug -- research run 71 (no execution)

Status: research/code-review only. src/crawler.py was NOT executed. Only
`python -m py_compile src/crawler.py` was run, per standing rule -- confirmed
it compiles cleanly (`COMPILE_OK`).

## 1. Refined diagnosis

Re-read src/crawler.py in full. There are exactly two call sites that hit the
network:

- `get_robots_parser()`, line 125: `requests.get(robots_url, headers=HEADERS, timeout=8)`
- `crawl()`, line 173: `requests.get(url, headers=HEADERS, timeout=8)`

Both pass a single scalar `timeout=8`. Per `requests` semantics, a scalar
timeout is applied as **both** the connect timeout and the read timeout, and
critically the read timeout is a "time between bytes received" timer, not a
wall-clock cap on the whole response. `requests` (via urllib3) resets that
timer every time any new data arrives on the socket, however small. There is
no code path here that:

- uses `stream=True` with a chunked read loop enforcing a deadline,
- wraps the call in a watchdog thread / `future.result(timeout=...)`,
- sets `socket.setdefaulttimeout()` as a global backstop,
- or bounds redirects (both calls use default `allow_redirects=True` with no
  cap on `response.history` length or per-hop time).

So the original hypothesis holds and is confirmed, not just plausible: a host
that trickles bytes slowly enough (e.g. 1 byte every 7 seconds, forever) can
keep both `requests.get()` calls -- and therefore `crawl()` and
`crawl_all_sources()` -- blocked indefinitely, because no single inter-byte
gap ever exceeds 8s even though the total transfer never completes. This
applies independently to the robots.txt fetch and every page fetch; the
robots.txt path is arguably the more dangerous one since it runs first for
every domain and has no incremental-flush mitigation around it at all (the
run-67 flush in `crawl_all_sources()` only helps between *sources*, not
within a single stuck `crawl()` call -- if the hang happens on page 1 of
source 3, sources 1-2's results are safe but the process still hangs there
forever with no way to move on to source 4).

Additional smaller findings while re-reading:
- Redirects are unbounded in count/time; a redirect chain to a slow host has
  the same exposure as a direct request.
- `time.sleep(1)` niceness delay is irrelevant to the hang (it's after a
  successful fetch, not blocking on it).
- No per-source or per-page overall time budget exists anywhere in
  `crawl_all_sources()`, so there's also no outer safety net that could
  abort a single stuck source and move on.

## 2. Standard fix patterns (web research)

Searched for the standard/well-known patterns for this exact class of bug.

**The core problem is well-documented**: `requests`' `timeout` parameter
bounds inter-byte read latency and connect latency, not total transfer wall
time -- "a slow server that trickles data can never trigger the read
timeout... requests's timeout parameter does not guarantee the total time."
([FixDevs](https://fixdevs.com/blog/python-requests-timeout/),
[ScrapingBee](https://www.scrapingbee.com/blog/python-requests-timeout/))

Recognized mitigations, roughly in order of how commonly recommended they are:

1. **Watchdog via `concurrent.futures.ThreadPoolExecutor` +
   `future.result(timeout=...)`.** Run the blocking `requests.get()` call in
   a worker thread and bound the whole call with `future.result(timeout=N)`
   in the calling thread. This is the most portable pattern (works on
   Windows, where this project runs) since it doesn't depend on
   `signal.alarm`, which is Unix-only. Caveat widely noted: `future.cancel()`
   cannot actually kill an in-flight `requests.get()` -- the worker thread
   keeps running/leaking until the OS-level socket eventually times out or
   errors, but the *calling* code is freed to move on, which is exactly what
   `crawl_all_sources()` needs (skip a stuck source, don't hang the whole
   pipeline).
2. **`signal.alarm()`-based hard timeout.** True OS-level interrupt, but
   Unix-only -- not viable here directly since dev/CI environment is Windows
   (win32), noted explicitly in this task's env info.
3. **Switch to `httpx` with explicit connect/read/write/pool timeout
   objects** (`httpx.Timeout(connect=..., read=..., write=..., pool=...)`).
   httpx still does not have a true "total" timeout distinct from its
   per-phase timeouts, so this alone does not fully solve the trickle case
   either -- same read-timeout-resets-per-chunk issue as requests. Only
   async httpx via `asyncio.wait_for()` gets a genuine wall-clock total. Not
   a drop-in fix without also restructuring to async or adding a watchdog.
4. **`socket.setdefaulttimeout()` global backstop.** Blunt instrument, only
   helps if `requests` doesn't override it per-call (it does, since it
   always passes an explicit timeout to the underlying socket), so this is
   not reliable here and not recommended as the primary fix.

Sources:
- https://fixdevs.com/blog/python-requests-timeout/
- https://www.scrapingbee.com/blog/python-requests-timeout/
- https://proxiesapi.com/articles/why-your-python-requests-timeout-may-not-be-timing-out-as-expected
- https://www.python-httpx.org/advanced/timeouts/
- https://docs.python.org/3/library/concurrent.futures.html
- https://superfastpython.com/threadpoolexecutor-timeouts/

## 3. Proposed patch draft (NOT applied -- for human review/testing only)

Minimal, Windows-portable approach: wrap each `requests.get()` call in a
`ThreadPoolExecutor(max_workers=1)` and enforce a hard wall-clock deadline
via `future.result(timeout=HARD_DEADLINE)`. On timeout, treat it exactly like
today's existing `except Exception` path (log + skip), so behavior for the
caller doesn't change -- only the never-returns case is now bounded.

```diff
--- a/src/crawler.py
+++ b/src/crawler.py
@@
 import requests
 from bs4 import BeautifulSoup
 from collections import deque
+from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
 from urllib.parse import urljoin, urlparse, urldefrag
 from urllib.robotparser import RobotFileParser
 import json
 import time
 import sys
+
+# per-call hard wall-clock deadline, independent of requests' own timeout=.
+# requests' timeout only bounds gaps *between* bytes, not total transfer
+# time -- a host that trickles data can stall forever without ever
+# tripping that per-read timeout. This bounds the whole call.
+# See docs/agent-logs/crawler-hang-research-run71.md.
+HARD_FETCH_DEADLINE = 20  # seconds, wall clock, per HTTP call
+
+def get_with_hard_deadline(url, **kwargs):
+    """requests.get() wrapped with a total wall-clock deadline.
+
+    Runs the blocking call in a worker thread so a slow-trickling host
+    cannot hang the crawler indefinitely -- the caller gets control back
+    after HARD_FETCH_DEADLINE seconds even though the worker thread (and
+    its socket) may still be alive in the background until the OS or
+    requests' own low-level timeout eventually cleans it up.
+    """
+    with ThreadPoolExecutor(max_workers=1) as executor:
+        future = executor.submit(requests.get, url, **kwargs)
+        return future.result(timeout=HARD_FETCH_DEADLINE)
@@
-        resp = requests.get(robots_url, headers=HEADERS, timeout=8)
+        resp = get_with_hard_deadline(robots_url, headers=HEADERS, timeout=8)
@@
-    except Exception:
+    except (Exception, FutureTimeoutError):
         # if we cant read it just assume we're allowed
         pass
@@
-            response = requests.get(url, headers=HEADERS, timeout=8)
+            response = get_with_hard_deadline(url, headers=HEADERS, timeout=8)
@@
-        except Exception as e:
+        except (Exception, FutureTimeoutError) as e:
             # log any error & continue
             print(f"error crawling {url}: {e}")
             continue
```

Notes for the human reviewer before testing live:
- `ThreadPoolExecutor` per call has overhead (thread spawn per request); for
  this crawler's request volume (tens of pages) that's negligible, but if a
  future revision wants to reduce overhead, one shared executor could be
  created once in `crawl_all_sources()` and passed down instead of one per
  call.
- A leaked worker thread per timeout will pin a socket open until whatever
  the underlying `timeout=8` eventually does at the OS/urllib3 level (or the
  process exits) -- this doesn't leak forever, but repeated hangs on the
  same bad host across a long crawl could accumulate lingering threads. Not
  a correctness bug, but worth watching in a live test.
- `HARD_FETCH_DEADLINE = 20` is a guess; should be tuned against real
  observed page sizes/latencies for the current FASHION_SOURCES list rather
  than assumed.
- This patch does not address unbounded redirect chains explicitly, but
  since redirects happen inside the same `requests.get()` call, the hard
  deadline wraps them too.
