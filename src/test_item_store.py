"""Tests for the item store (src/item_store.py, db/migrations/).

usage: python src/test_item_store.py
"""

import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402

URL = "https://www.vogue.com/article/fixture-sheer-layering"


class ItemStoreTests(unittest.TestCase):
    def setUp(self):
        self.con = store.connect(":memory:")
        store.migrate(self.con)

    def add(self, **kw):
        args = dict(url=URL, published_at="2026-09-18T10:00:00Z", source_method="rss",
                    title="Fixture", fetched_at="2026-09-20T08:00:00Z")
        args.update(kw)
        return store.upsert_item(self.con, **args)

    def test_migrate_is_idempotent(self):
        self.assertEqual(store.migrate(self.con), [])
        self.assertEqual(store.applied_versions(self.con), {1})

    def test_same_item_twice_is_one_row(self):
        first = self.add()
        second = self.add(fetched_at="2026-09-21T08:00:00Z")
        self.assertEqual(first[1], "inserted")
        self.assertEqual(second, (first[0], "unchanged"))
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM items").fetchone()[0], 1)

    def test_tracking_params_and_fragment_collapse(self):
        item_id, _ = self.add()
        again = self.add(url=URL + "/?utm_source=x&utm_medium=y#top")
        self.assertEqual(again[0], item_id)

    def test_changed_content_updates(self):
        item_id, _ = self.add()
        self.assertEqual(self.add(title="Fixture, corrected")[1], "updated")
        self.assertEqual(self.con.execute("SELECT title FROM items WHERE item_id=?", (item_id,)).fetchone()[0],
                         "Fixture, corrected")

    def test_outlet_sector_from_taxonomy(self):
        self.add()
        self.add(url="https://unmapped-outlet.example/post/1")
        rows = dict(self.con.execute(
            "SELECT o.domain, h.sector_id FROM outlets o JOIN outlet_sector_history h USING(outlet_id)"))
        self.assertEqual(rows["vogue.com"], "editorial")
        self.assertEqual(rows["unmapped-outlet.example"], "unclear")

    def test_published_after_fetched_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add(published_at="2026-09-25T00:00:00Z")

    def test_non_http_url_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.add(url="vogue.com/article/x")

    def test_future_report_is_rejected(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("INSERT INTO reports (report_date, window_start, window_end) "
                             "VALUES ('2099-01-04', '2098-12-29', '2099-01-04')")

    def test_publish_requires_evidence(self):
        self.con.execute("INSERT INTO reports (report_date, window_start, window_end) "
                         "VALUES ('2026-09-21', '2026-09-15', '2026-09-21')")
        self.con.execute("INSERT INTO report_signals (report_date, signal_id, name, confidence, volatility, "
                         "origin_classification) VALUES ('2026-09-21', 'fixture', 'Fixture', 'low', 'emerging', 'unclear')")
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("UPDATE reports SET status='published' WHERE report_date='2026-09-21'")
        item_id, _ = self.add()
        self.con.execute("INSERT INTO signal_evidence VALUES ('2026-09-21', 'fixture', ?)", (item_id,))
        self.con.execute("UPDATE reports SET status='published' WHERE report_date='2026-09-21'")

    def test_exposure_view_counts_items(self):
        self.add()
        self.assertEqual(store.stats(self.con)["items_by_coarse_sector"], {"editorial": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
