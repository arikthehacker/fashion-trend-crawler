# Crawler daemon-thread fix -- run 73

Status: fix applied to `src/crawler.py`, validated with the existing
localhost trickle test (extended with a new assertion). Builds on
`docs/agent-logs/crawler-hang-fix-run72.md`, which fixed the hang itself
but left a documented side effect: the leaked worker thread inside
`ThreadPoolExecutor` was non-daemon, so after a timeout the `python.exe`
process wouldn't exit on its own.

## 1. Root cause

`concurrent.futures.ThreadPoolExecutor` (Python 3.13.2, confirmed via
`python -c "import sys; print(sys.version)"`) does not expose a `daemon=`
kwarg -- its internal `_worker` threads are created as plain non-daemon
`threading.Thread` objects. `executor.shutdown(wait=False)` (used by the
run-72 fix to avoid re-introducing the hang) detaches the caller from the
thread pool's bookkeeping but does not change that threads' daemon status.
Result: any leaked worker (one still blocked inside `requests.get()` on a
trickling host after the deadline fires) keeps the interpreter alive at
process exit until its own socket/timeout eventually resolves it.

## 2. Fix applied

Replaced the `ThreadPoolExecutor` usage in `get_with_hard_deadline()` with
a hand-rolled daemon thread + a `queue.Queue(maxsize=1)` to hand back the
result (or exception) from the worker to the caller:

```python
def get_with_hard_deadline(url, **kwargs):
    result_q = _queue.Queue(maxsize=1)

    def _worker():
        try:
            result_q.put(("ok", requests.get(url, **kwargs)))
        except Exception as exc:
            result_q.put(("error", exc))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    try:
        status, value = result_q.get(timeout=HARD_FETCH_DEADLINE)
    except _queue.Empty:
        raise FutureTimeoutError(
            f"get_with_hard_deadline: {url} did not complete within "
            f"{HARD_FETCH_DEADLINE}s"
        )
    if status == "error":
        raise value
    return value
```

`threading.Thread(daemon=True)` is a first-class kwarg (unlike
`ThreadPoolExecutor`), so this is the minimal correct fix for this
environment -- no new dependency, no subclassing an executor. Daemon
threads are killed outright by the interpreter when the main thread ends,
so a still-blocked worker can no longer prevent process exit. Behavior on
the happy path and on timeout is otherwise identical to the run-72 version
(`FutureTimeoutError` from `concurrent.futures` is still raised on
deadline, so the two `except (Exception, FutureTimeoutError)` call sites
in `get_robots_parser()` and `crawl()` did not need to change).

Import changes: dropped `ThreadPoolExecutor` from the
`concurrent.futures` import (kept `TimeoutError as FutureTimeoutError`),
added `import threading` and `import queue as _queue`.

## 3. Test update

`src/test_crawler_timeout.py`: after the existing assertion that
`get_with_hard_deadline()` raises `FutureTimeoutError` near the 3s test
deadline, added a new assertion that inspects `threading.enumerate()` for
any non-daemon thread still alive besides the current thread (this would
be the leaked trickle-request worker if it weren't a daemon):

```python
leaked_non_daemon = [
    t for t in threading.enumerate()
    if t is not threading.current_thread() and not t.daemon and t.is_alive()
]
assert not leaked_non_daemon, ...
```

Still localhost-only, still does not call `crawl()` / `crawl_all_sources()`,
no real network traffic.

## 4. Compile check

```
python -m py_compile src/crawler.py
```
Passed cleanly (no output = success).

## 5. Test run + exit-code/timing check

```
cd src && timeout 8 python test_crawler_timeout.py; echo EXIT:$?
```

Output:
```
PASS: hard deadline fired after 3.02s (deadline was 3s)
PASS: no leaked non-daemon threads after hard deadline fired
EXIT:0
```

Measured wall-clock time for the whole script (start-to-finish, including
Python startup and the 3s deadline wait): **4 seconds**. Exit code **0**
(not the 124 that `timeout` would report on a hang). This confirms the
process exits promptly on its own after the hard deadline fires -- the
daemon-thread fix removes the run-72 side effect.

## 6. Outcome

- Fix applied: yes -- `get_with_hard_deadline()` now uses a daemon
  `threading.Thread` + `queue.Queue` instead of `ThreadPoolExecutor`.
- New test assertion: passed (no leaked non-daemon threads after timeout).
- Process exit: confirmed prompt (exit code 0, ~4s total, no manual kill
  needed).
- `python -m py_compile src/crawler.py`: passed.
- Remaining caveat (unchanged in nature from run 72, just now harmless):
  the worker thread itself is still leaked in the background until the
  underlying `requests` call's own low-level timeout/socket eventually
  resolves it -- that memory/socket is not reclaimed early, but since the
  thread is now a daemon it no longer blocks process shutdown.
- Files touched: `src/crawler.py` (edited), `src/test_crawler_timeout.py`
  (edited). `TODO.md`, `CHANGELOG.md`, and no other agent's files were
  touched. Not committed, per instructions.
