"""
Isolated unit test for the hard wall-clock deadline fix in crawler.py
(run 72, see docs/agent-logs/crawler-hang-fix-run72.md).

Spins up a local HTTP server on localhost that trickles a single byte per
second and never finishes the response. Proves that
get_with_hard_deadline() aborts within its configured deadline instead of
hanging indefinitely, the way a bare requests.get(timeout=8) would not
(requests' timeout only bounds gaps *between* bytes, not total transfer
time -- see run 71's research doc).

Safe to execute: localhost only, no real network traffic, server and client
both live in this process. Does NOT import or call crawl()/crawl_all_sources()
and never touches a real external site.
"""

import http.server
import threading
import time
import socket
from concurrent.futures import TimeoutError as FutureTimeoutError

import crawler


class TrickleHandler(http.server.BaseHTTPRequestHandler):
    """Sends a 200 + one byte per second, forever (until the client gives up)."""

    def log_message(self, format, *args):
        pass  # keep test output quiet

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        # deliberately NOT sending Content-Length, so the connection stays
        # open indefinitely from the client's point of view
        self.end_headers()
        try:
            while True:
                self.wfile.write(b"x")
                self.wfile.flush()
                time.sleep(1)
        except (BrokenPipeError, ConnectionAbortedError, OSError):
            # client gave up / socket closed -- expected once the test ends
            pass


def start_trickle_server():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), TrickleHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def test_hard_deadline_aborts_on_trickle():
    server, port = start_trickle_server()
    url = f"http://127.0.0.1:{port}/trickle"

    # use a short deadline for a fast test, instead of the real 20s default
    original_deadline = crawler.HARD_FETCH_DEADLINE
    crawler.HARD_FETCH_DEADLINE = 3
    try:
        start = time.monotonic()
        raised = False
        try:
            # note: requests' own timeout=8 here would NOT fire on its own --
            # each byte arrives well within that per-read window forever.
            # It's the wrapper's future.result(timeout=3) that must fire.
            crawler.get_with_hard_deadline(url, timeout=8)
        except FutureTimeoutError:
            raised = True
        elapsed = time.monotonic() - start

        assert raised, "expected FutureTimeoutError from the hard deadline wrapper"
        # must abort close to the configured deadline (3s), not hang forever,
        # and must not silently take significantly longer than the deadline
        assert elapsed < 6, f"took {elapsed:.1f}s, expected to abort near 3s deadline"
        print(f"PASS: hard deadline fired after {elapsed:.2f}s (deadline was 3s)")

        # run 73: the leaked worker thread (still blocked inside
        # requests.get() against the trickle server) must be a daemon
        # thread, so it cannot block interpreter/process exit on its own.
        leaked_non_daemon = [
            t for t in threading.enumerate()
            if t is not threading.current_thread() and not t.daemon and t.is_alive()
        ]
        assert not leaked_non_daemon, (
            f"found non-daemon thread(s) still alive after timeout: "
            f"{[t.name for t in leaked_non_daemon]} -- these would block "
            f"process exit"
        )
        print("PASS: no leaked non-daemon threads after hard deadline fired")
    finally:
        crawler.HARD_FETCH_DEADLINE = original_deadline
        server.shutdown()


if __name__ == "__main__":
    test_hard_deadline_aborts_on_trickle()
