"""Tests for report preparation waiting on ingest and catching up missed windows
(src/report_prepare.py), and for mirrored feeds (src/mirrors.py). Temp folder and
throwaway store, no network.

usage: python src/test_report_prep_wait.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import mirrors  # noqa: E402
import report_prepare as rp  # noqa: E402
import report_review as rr  # noqa: E402

at = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


class WaitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.paths = rr.Paths(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ingest(self, started, finished):
        with open(self.paths.ingest_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"started_at": started, "finished_at": finished}) + "\n")

    def running(self, started):
        with open(self.paths.ingest_running, "w", encoding="utf-8") as f:
            f.write(started)

    def test_a_running_ingest_blocks_even_after_a_finished_one(self):
        self.ingest("2026-10-12T04:30:02Z", "2026-10-12T04:34:00Z")
        self.running("2026-10-12T08:30:00Z")
        ready, reason = rp.readiness(self.paths, "2026-10-05", "2026-10-11", at("2026-10-12T08:31:00"))
        self.assertFalse(ready)
        self.assertIn("ingest is running", reason)
        self.assertTrue(rp.readiness(self.paths, "2026-10-05", "2026-10-11", at("2026-10-12T10:00:00"))[0])  # stale marker

    def test_waits_through_a_wake_where_ingest_starts_at_the_same_moment(self):
        """The 2026-10-13 failure: both tasks start on wake; preparation must wait, not give up."""
        self.ingest("2026-10-11T12:30:02Z", "2026-10-11T12:34:00Z")   # last run before the machine went down
        clock = {"t": at("2026-10-13T07:07:00")}
        self.running("2026-10-13T07:07:00Z")

        def sleep(seconds):
            clock["t"] += timedelta(seconds=seconds)
            if clock["t"] >= at("2026-10-13T07:11:00") and os.path.exists(self.paths.ingest_running):
                os.remove(self.paths.ingest_running)                    # the catch-up ingest finishes
                self.ingest("2026-10-13T07:07:00Z", "2026-10-13T07:10:30Z")

        ready, reason = rp.wait_until_ready(self.paths, "2026-10-05", "2026-10-11", clock=lambda: clock["t"], sleep=sleep)
        self.assertTrue(ready, reason)
        self.assertLess(clock["t"], at("2026-10-13T07:20:00"))

    def test_gives_up_after_the_wait_so_a_later_trigger_retries(self):
        clock = {"t": at("2026-10-13T07:07:00")}
        slept = []

        def sleep(seconds):
            slept.append(seconds)
            clock["t"] += timedelta(seconds=seconds)

        ready, reason = rp.wait_until_ready(self.paths, "2026-10-05", "2026-10-11", max_minutes=10, clock=lambda: clock["t"], sleep=sleep)
        self.assertFalse(ready)
        self.assertEqual(sum(slept), 600)

    def test_does_not_wait_for_an_open_window(self):
        slept = []
        ready, _ = rp.wait_until_ready(self.paths, "2026-10-19", "2026-10-25", clock=lambda: at("2026-10-21T12:00:00"), sleep=slept.append)
        self.assertEqual((ready, slept), (False, []))

    def test_pending_windows_are_every_closed_unprepared_week_oldest_first(self):
        now = at("2026-10-21T12:00:00")
        self.assertEqual(rp.pending_windows(self.paths, now), [("2026-10-05", "2026-10-11"), ("2026-10-12", "2026-10-18")])
        os.makedirs(self.paths.drafts)
        open(self.paths.draft("2026-10-11"), "w").close()
        self.assertEqual(rp.pending_windows(self.paths, now), [("2026-10-12", "2026-10-18")])
        self.assertEqual(rp.pending_windows(self.paths, at("2026-10-18T23:59:00")), [])


class MirrorTests(unittest.TestCase):
    def test_copies_on_a_mirror_domain_are_marked_once_and_count_as_one_source(self):
        con = store.connect(":memory:")
        store.migrate(con)
        add = lambda url, title, excerpt, day: store.upsert_item(
            con, url=url, published_at=f"2026-10-{day}T10:00:00Z", source_method="rss", title=title,
            fetched_at=f"2026-10-{day}T12:00:00Z", text_excerpt=excerpt, lang="en")[0]
        com = add("https://fashionunited.com/news/a", "Same story", "Same excerpt.", "05")
        uk = add("https://fashionunited.uk/news/a", "Same story", "Same excerpt.", "05")
        uk_only = add("https://fashionunited.uk/news/b", "Only in the UK", "Different.", "06")
        other = add("https://example.com/c", "Same story", "Same excerpt.", "05")   # not a mirror domain
        con.commit()
        self.assertEqual(mirrors.mark(con), 1)
        self.assertEqual(mirrors.mark(con), 0)  # idempotent
        rows = dict(con.execute("select item_id, syndicated_of from items"))
        self.assertEqual((rows[uk], rows[uk_only], rows[com], rows[other]), (com, None, None, None))
        self.assertEqual({mirrors.source_of(d) for d in ("fashionunited.uk", "fashionunited.com")}, {"fashionunited.com"})
        self.assertEqual(mirrors.source_of("vogue.co.uk"), "vogue.co.uk")


if __name__ == "__main__":
    unittest.main()
