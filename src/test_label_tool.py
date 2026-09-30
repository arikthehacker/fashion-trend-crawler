"""Tests for the EXP-003A time-holdout selector in src/label_tool.py.

The rule under test is models/ari3-v0.0.3/AMENDMENT_2026-09-30_holdout_eligibility.md:
published after the freeze, section 5 filters, first_seen_at after the freeze, and no
record from before the freeze showing the item.

usage: python src/test_label_tool.py
"""

import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import label_tool as lt  # noqa: E402

FREEZE = "2026-09-26T19:25:40Z"


class HoldoutQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._queue_dir = lt.QUEUE_DIR
        lt.QUEUE_DIR = os.path.join(self.tmp, "queues")
        self.con = store.connect(":memory:")
        store.migrate(self.con)
        self.n = 0

    def tearDown(self):
        lt.QUEUE_DIR = self._queue_dir
        self.con.close()
        shutil.rmtree(self.tmp)

    def add(self, published_at, fetched_at, excerpt="A cropped wool jacket.", **kw):
        self.n += 1
        url = kw.pop("url", f"https://www.vogue.com/article/fixture-{self.n}")
        item_id, _ = store.upsert_item(self.con, url=url, published_at=published_at, source_method="rss",
                                       title=f"Fixture {self.n}", fetched_at=fetched_at,
                                       hash_basis=kw.pop("hash_basis", "a"), text_excerpt=excerpt, **kw)
        return item_id

    def add_first_seen(self):
        """Stand-in for migration 0004: first_seen_at = fetched_at for every row."""
        self.con.execute("ALTER TABLE items ADD COLUMN first_seen_at TEXT")
        self.con.execute("UPDATE items SET first_seen_at = fetched_at")

    def backup_with(self, rows):
        path = os.path.join(self.tmp, f"backup-{len(os.listdir(self.tmp))}.db")
        b = sqlite3.connect(path)
        b.execute("CREATE TABLE items (item_id INTEGER, url TEXT, fetched_at TEXT)")
        b.executemany("INSERT INTO items VALUES (?,?,?)", rows)
        b.commit()
        b.close()
        return path

    def queue(self, **kw):
        kw.setdefault("backup_paths", [])
        with open(lt.make_holdout_queue(self.con, FREEZE, **kw), encoding="utf-8") as f:
            return json.load(f)

    def test_pre_freeze_item_with_later_fetched_at_is_rejected(self):
        old = self.add("2026-09-25T10:00:00Z", "2026-09-25T12:00:00Z")
        store.upsert_item(self.con, url="https://www.vogue.com/article/fixture-1",
                          published_at="2026-09-25T10:00:00Z", source_method="rss",
                          title="Fixture 1, edited", fetched_at="2026-09-28T08:00:00Z", hash_basis="b")
        self.assertGreater(self.con.execute("SELECT fetched_at FROM items WHERE item_id=?", (old,)).fetchone()[0],
                           FREEZE)
        new = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.assertEqual(lt.holdout_pool(self.con, FREEZE), [new])

    def test_post_freeze_item_scored_by_frozen_model_stays_eligible(self):
        item = self.add("2026-09-26T20:29:00Z", "2026-09-26T20:30:30Z")
        self.con.execute("INSERT INTO label_predictions (item_id, task, model_version, predicted_label, created_at) "
                         "VALUES (?, 'is_style_signal', 'ari3-v0.0.2', 'yes', '2026-09-26T20:40:23Z')", (item,))
        self.add_first_seen()
        snapshot = self.backup_with([(item, "https://www.vogue.com/article/fixture-1", "2026-09-26T20:30:30Z")])
        self.assertEqual(self.queue(backup_paths=[snapshot])["item_ids"], [item])

    def test_section_5_filters_still_apply(self):
        keep = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z", excerpt=None)
        synd = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.con.execute("UPDATE items SET syndicated_of=? WHERE item_id=?", (keep, synd))
        labeled = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.con.execute("INSERT INTO labels (item_id, task, label, source, labeler, split, created_at) "
                         "VALUES (?, 'is_style_signal', 'yes', 'human', 'ariella', 'train', '2026-09-27T13:00:00Z')",
                         (labeled,))
        other_task = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.con.execute("INSERT INTO labels (item_id, task, label, source, labeler, split, created_at) "
                         "VALUES (?, 'is_forecast', 'no', 'human', 'ariella', 'train', '2026-09-27T13:00:00Z')",
                         (other_task,))
        self.assertEqual(lt.holdout_pool(self.con, FREEZE), [keep, other_task])

    def test_refuses_without_first_seen(self):
        self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        with self.assertRaises(lt.HoldoutIntegrityError):
            self.queue()
        self.assertFalse(os.path.exists(lt.queue_path("is_style_signal_holdout_exp003")))

    def test_stops_when_first_seen_is_not_after_freeze(self):
        item = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.add_first_seen()
        self.con.execute("UPDATE items SET first_seen_at=? WHERE item_id=?", (FREEZE, item))
        with self.assertRaises(lt.HoldoutIntegrityError):
            self.queue()

    def test_stops_when_a_backup_shows_the_item_before_the_freeze(self):
        item = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.add_first_seen()
        by_url = self.backup_with([(999, "https://www.vogue.com/article/fixture-1", "2026-09-25T00:00:00Z")])
        with self.assertRaises(lt.HoldoutIntegrityError):
            self.queue(backup_paths=[by_url])
        self.assertEqual(lt.pre_freeze_evidence(self.con, [item], FREEZE, [by_url]),
                         {item: [f"backup:{os.path.basename(by_url)}"]})

    def test_stops_when_a_pre_freeze_prediction_or_label_names_the_item(self):
        item = self.add("2026-09-27T10:00:00Z", "2026-09-27T12:00:00Z")
        self.add_first_seen()
        self.con.execute("INSERT INTO label_predictions (item_id, task, model_version, predicted_label, created_at) "
                         "VALUES (?, 'is_style_signal', 'jev', 'yes', '2026-09-23T07:53:46Z')", (item,))
        self.assertEqual(lt.pre_freeze_evidence(self.con, [item], FREEZE), {item: ["prediction_ledger"]})
        with self.assertRaises(lt.HoldoutIntegrityError):
            self.queue()

    def test_queue_is_deterministic_and_fingerprinted(self):
        for day in range(27, 30):
            for _ in range(5):
                self.add(f"2026-09-{day}T10:00:00Z", f"2026-09-{day}T12:00:00Z")
        self.add_first_seen()
        first = self.queue(n=6)
        second = self.queue(n=6)
        self.assertEqual(first["item_ids"], second["item_ids"])
        self.assertEqual(len(first["item_ids"]), 6)
        self.assertEqual(first["split"], "time_holdout")
        self.assertEqual(first["published_after"], FREEZE)
        self.assertEqual(first["eligible_pool"], 15)
        self.assertEqual(len(first["item_ids_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
