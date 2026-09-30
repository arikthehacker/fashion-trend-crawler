"""Tests for migration 0004 (first-seen provenance) and src/backfill_first_seen.py.

Every test runs on a throwaway database file.

usage: python src/test_backfill_first_seen.py
"""

import glob
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import backfill_first_seen as bf  # noqa: E402
import item_store as store  # noqa: E402

U1 = "https://www.vogue.com/article/fixture-one"
U2 = "https://www.vogue.com/article/fixture-two"


class FirstSeenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "store.db")
        self.backups = os.path.join(self.tmp, "backups")
        os.makedirs(self.backups)
        # build the store as it was before 0004, whatever db/migrations holds now
        self._migrations_dir = store.MIGRATIONS_DIR
        pre = os.path.join(self.tmp, "migrations")
        os.makedirs(pre)
        for version in ("0001", "0002", "0003"):
            for path in glob.glob(os.path.join(self._migrations_dir, f"{version}_*.sql")):
                shutil.copy(path, pre)
        store.MIGRATIONS_DIR = pre
        self.con = store.connect(self.db)
        store.migrate(self.con)

    def tearDown(self):
        store.MIGRATIONS_DIR = self._migrations_dir
        self.con.close()
        shutil.rmtree(self.tmp)

    def add(self, url, published_at, fetched_at, basis="a"):
        return store.upsert_item(self.con, url=url, published_at=published_at, source_method="rss",
                                 title="Fixture", fetched_at=fetched_at, hash_basis=basis, text_excerpt="x")[0]

    def backup(self, name):
        self.con.commit()
        self.con.execute("VACUUM INTO ?", (os.path.join(self.backups, name),))

    def migrate_0004(self):
        if not bf.has_first_seen(self.con):
            self.con.executescript("BEGIN;\n" + bf.migration_sql() + "\nCOMMIT;")

    def old_store(self):
        """Two items stored before 0004. Item 1 was edited later, so its fetched_at moved."""
        a = self.add(U1, "2026-09-24T10:00:00Z", "2026-09-24T12:00:00Z")
        b = self.add(U2, "2026-09-25T10:00:00Z", "2026-09-25T12:00:00Z")
        self.backup("ari3lla-2026-09-25T1300Z.db")
        self.add(U1, "2026-09-24T10:00:00Z", "2026-09-28T08:00:00Z", basis="edited")
        self.con.commit()
        return a, b

    def test_dry_run_takes_earliest_evidence_and_reports(self):
        a, b = self.old_store()
        plan, report = bf.build_plan(self.con, [os.path.join(self.backups, "ari3lla-2026-09-25T1300Z.db")])
        got = {i: (t, s) for i, t, s in plan}
        self.assertEqual(got[a], ("2026-09-24T12:00:00Z", "backup:ari3lla-2026-09-25T1300Z.db"))
        self.assertEqual(got[b], ("2026-09-25T12:00:00Z", "current_fetched_at"))
        self.assertEqual(report["earlier_than_current_fetched_at"]["items"], 1)
        self.assertEqual(report["first_seen_at_or_before_freeze_but_fetched_after"]["items"], 1)
        self.assertEqual(report["invariant_failures"], [])
        self.assertEqual(len(report["fingerprint"]), 64)

    def test_ledger_and_label_evidence_and_rejections(self):
        a, b = self.old_store()
        self.con.execute("INSERT INTO label_predictions (item_id, task, model_version, predicted_label, created_at) "
                         "VALUES (?, 't', 'm1', 'yes', '2026-09-24T11:00:00Z')", (a,))
        self.con.execute("INSERT INTO labels (item_id, task, label, source, labeler, split, created_at) "
                         "VALUES (?, 't', 'yes', 'human', 'x', 'train', '2026-09-20T00:00:00Z')", (b,))
        plan, report = bf.build_plan(self.con, [])
        got = {i: (t, s) for i, t, s in plan}
        self.assertEqual(got[a], ("2026-09-24T11:00:00Z", "prediction_ledger:m1"))
        self.assertEqual(got[b], ("2026-09-25T12:00:00Z", "current_fetched_at"))
        self.assertEqual(report["rejected_evidence"], {"before_published_at": 1})

    def test_id_only_evidence_rejected_when_a_backup_shows_another_url(self):
        a, _ = self.old_store()
        path = os.path.join(self.backups, "odd.db")
        odd = sqlite3.connect(path)
        odd.execute("CREATE TABLE items (item_id INTEGER, url TEXT, fetched_at TEXT)")
        odd.execute("INSERT INTO items VALUES (?, 'https://elsewhere.example/other', '2026-09-24T11:30:00Z')", (a,))
        odd.commit()
        odd.close()
        self.con.execute("INSERT INTO label_predictions (item_id, task, model_version, predicted_label, created_at) "
                         "VALUES (?, 't', 'm1', 'yes', '2026-09-24T11:00:00Z')", (a,))
        plan, report = bf.build_plan(self.con, [path])
        self.assertNotIn("prediction_ledger:m1", [s for i, _, s in plan if i == a])
        self.assertEqual(report["rejected_evidence"]["prediction_ledger_url_conflict"], 1)

    def test_apply_needs_migration_and_matching_fingerprint(self):
        self.old_store()
        paths = [os.path.join(self.backups, "ari3lla-2026-09-25T1300Z.db")]
        plan, report = bf.build_plan(self.con, paths)
        self.con.commit()
        self.con.isolation_level = None
        with self.assertRaises(RuntimeError):
            bf.apply_plan(self.con, plan, report["fingerprint"], report["science_counts"])
        self.migrate_0004()
        plan2, report2 = bf.build_plan(self.con, paths)
        self.assertEqual(report2["fingerprint"], report["fingerprint"])
        with self.assertRaises(RuntimeError):
            bf.apply_plan(self.con, plan2, "0" * 64, report2["science_counts"])
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM items WHERE first_seen_at IS NULL").fetchone()[0], 2)

    def test_apply_then_database_enforces_provenance(self):
        a, b = self.old_store()
        paths = [os.path.join(self.backups, "ari3lla-2026-09-25T1300Z.db")]
        _, dry = bf.build_plan(self.con, paths)
        self.con.commit()
        self.migrate_0004()
        self.con.isolation_level = None
        plan, report = bf.build_plan(self.con, paths)
        checks = bf.apply_plan(self.con, plan, dry["fingerprint"], report["science_counts"])
        self.assertTrue(all(checks.values()))
        row = self.con.execute("SELECT first_seen_at, first_seen_basis, first_seen_evidence FROM items "
                               "WHERE item_id=?", (a,)).fetchone()
        self.assertEqual(row, ("2026-09-24T12:00:00Z", "reconstructed", "backup:ari3lla-2026-09-25T1300Z.db"))
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("UPDATE items SET first_seen_at='2026-09-26T00:00:00Z' WHERE item_id=?", (a,))
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("UPDATE items SET first_seen_evidence='current_fetched_at' WHERE item_id=?", (b,))
        # a new row is stamped by the database, and an edit keeps its first-seen value
        c = self.add("https://www.vogue.com/article/fixture-three", "2026-09-30T06:00:00Z", "2026-09-30T08:30:00Z")
        self.add("https://www.vogue.com/article/fixture-three", "2026-09-30T06:00:00Z", "2026-09-30T12:30:00Z",
                 basis="edited")
        self.assertEqual(self.con.execute("SELECT first_seen_at, first_seen_basis, fetched_at FROM items "
                                          "WHERE item_id=?", (c,)).fetchone(),
                         ("2026-09-30T08:30:00Z", "live_insert", "2026-09-30T12:30:00Z"))
        # a second run finds nothing left to do
        plan3, _ = bf.build_plan(self.con, paths)
        self.assertEqual(plan3, [])

    def test_writer_cannot_supply_first_seen(self):
        self.migrate_0004()
        outlet = store.upsert_outlet(self.con, "www.vogue.com")
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("INSERT INTO items (outlet_id, url, published_at, ts_precision, fetched_at, content_hash, "
                             "source_method, first_seen_at) VALUES (?, ?, '2026-09-30T06:00:00Z', 'exact', "
                             "'2026-09-30T07:00:00Z', 'h', 'rss', '2026-01-01T00:00:00Z')", (outlet, U1))

    def test_fetched_at_cannot_move_before_first_seen(self):
        self.migrate_0004()
        a = self.add(U1, "2026-09-30T06:00:00Z", "2026-09-30T07:00:00Z")
        with self.assertRaises(sqlite3.DatabaseError):
            self.con.execute("UPDATE items SET fetched_at='2026-09-30T06:30:00Z' WHERE item_id=?", (a,))


if __name__ == "__main__":
    unittest.main()
