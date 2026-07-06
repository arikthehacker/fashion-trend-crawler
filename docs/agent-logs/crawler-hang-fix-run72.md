# Crawler hang bug -- fix applied, run 72

Status: fix applied to src/crawler.py and validated with an isolated
localhost test. **No real network requests were executed** -- per the
standing rule, crawl()/crawl_all_sources() were never invoked against any
external site. Builds directly on docs/agent-logs/crawler-hang-research-run71.md,
which diagnosed the bug and drafted (but did not apply/test) this fix.

## 1. Diff summary

Applied run 71's drafted patch, with one correction (see section 2):

- Added `from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError`.
- Added `HARD_FETCH_DEADLINE = 20` (seconds) and a new helper
  `get_with_hard_deadline(url, **kwargs)` that runs `requests.get()` in a
  single-worker `ThreadPoolExecutor` and bounds the whole call with
  `future.result(timeout=HARD_FETCH_DEADLINE)`.
- Replaced both network call sites with the wrapper:
  - `get_robots_parser()`: `requests.get(robots_url, ...)` ->
    `get_with_hard_deadline(robots_url, ...)`
  - `crawl()`: `requests.get(url, ...)` -> `get_with_hard_deadline(url, ...)`
- Widened the two surrounding `except Exception` clauses to
  `except (Exception, FutureTimeoutError)` so a timed-out fetch is treated
  exactly like today's existing error path (robots.txt: assume allowed;
  page fetch: log + skip to the next URL). No change in caller-visible
  behavior other than "eventually returns" instead of "hangs forever."

## 2. Correction vs. the run-71 draft

The draft used `with ThreadPoolExecutor(max_workers=1) as executor:`. That's
a bug in the draft itself: `ThreadPoolExecutor.__exit__` calls
`shutdown(wait=True)`, which blocks until the worker thread finishes --
exactly the case that never happens when the request is stuck on a
trickling host. Using it as a context manager would silently re-introduce
the same hang the fix is meant to remove, just one level down.

Fixed by managing the executor manually and calling
`shutdown(wait=False)` in a `finally` block, so `get_with_hard_deadline()`
returns to the caller as soon as `future.result(timeout=...)` fires,
regardless of whether the worker thread is still blocked in the background.
This matches the draft's own caveat notes (worker thread may leak/linger)
but makes sure the *caller* is actually freed, which the `with` form did not
guarantee.

```python
def get_with_hard_deadline(url, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(requests.get, url, **kwargs)
        return future.result(timeout=HARD_FETCH_DEADLINE)
    finally:
        executor.shutdown(wait=False)
```

## 3. Compile check

```
python -m py_compile src/crawler.py
```
Passed cleanly (no output = success).

## 4. Isolated localhost test

New file: `src/test_crawler_timeout.py`. Not a live-network test -- it spins
up a `ThreadingHTTPServer` bound to `127.0.0.1` on an OS-assigned ephemeral
port, in-process, and a handler (`TrickleHandler`) that sends one byte per
second forever with no `Content-Length`, so the connection never completes
from the client's perspective. This reproduces exactly the failure mode
diagnosed in run 71 (each byte arrives well inside any per-read timeout, so
`requests`' own `timeout=` parameter never fires).

The test imports `crawler` directly, temporarily overrides
`crawler.HARD_FETCH_DEADLINE = 3` (for a fast test instead of waiting out
the real 20s default), calls `crawler.get_with_hard_deadline(url, timeout=8)`
against the trickle server, and asserts:
- a `concurrent.futures.TimeoutError` is raised (not a hang, not a silent
  success),
- it fires close to the 3s deadline (elapsed < 6s), not after some much
  longer or unbounded wait.

Does NOT call `crawl()` or `crawl_all_sources()` and never touches a real
external site -- server and client both live in this process on localhost.

### Test output

```
PASS: hard deadline fired after 3.00s (deadline was 3s)
```

Ran clean, twice (once via a `timeout 30 python ...` wrapper that itself
didn't fire, once via the plain fallback invocation) -- both runs passed
with elapsed times of 3.00s and 2.99s against a 3s deadline. The wrapper
correctly aborts a request that would otherwise hang forever.

## 5. Outcome

- Fix applied: yes.
- Localhost trickle test: **passed**.
- `crawler.py` is now, on this evidence, in a state worth a **human-supervised
  live test** against real fashion sources -- the specific hang mechanism
  identified in run 71 (trickle bytes defeat `requests`' inter-byte
  timeout) is now bounded by a real wall-clock deadline, proven against a
  local server that reproduces that exact failure mode.
- Remaining caveats (unchanged from run 71's notes, still true after this
  patch): a worker thread is leaked per timeout until the underlying
  `requests` call's own low-level timeout/socket eventually resolves it;
  `HARD_FETCH_DEADLINE = 20` is a guess and should be tuned against real
  observed page latencies for `FASHION_SOURCES` during the supervised live
  test; unbounded redirect chains are still wrapped by (not separately
  bounded within) the same deadline.
- Files touched: `src/crawler.py` (edited), `src/test_crawler_timeout.py`
  (new). No other agent's files, `TODO.md`, or `CHANGELOG.md` were touched.
  Not committed, per instructions -- leaving that to the coordinator after
  independent verification.
