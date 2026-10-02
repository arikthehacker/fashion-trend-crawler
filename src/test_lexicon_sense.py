"""Tests for the Lexicon v1 sense-check deck (src/lexicon_sense.py). Throwaway store, no network.

usage: python src/test_lexicon_sense.py
"""

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import lexicon  # noqa: E402
import lexicon_sense as ls  # noqa: E402


class SenseDeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.con = store.connect(os.path.join(self.tmp, "s.db"))
        store.migrate(self.con)
        self.con.execute("INSERT INTO lexicon_versions (lexicon_version, created_at, note) VALUES (1, 'x', 'v1')")
        for term, flag in (("lace", 1), ("corset", 0)):
            self.con.execute("INSERT INTO terms (term_id, canonical, signal_type, introduced_in) VALUES (?,?,?,1)",
                             (term, term, "material"))
            self.con.execute("INSERT INTO term_variants (term_id, variant, lexicon_version) VALUES (?,?,1)", (term, term))
            self.con.execute("INSERT INTO term_rules (term_id, editor_note, needs_sense_check, decided_at) "
                             "VALUES (?,?,?,'x')", (term, "needs sense check" if flag else None, flag))
        for url, title, ex in (("https://a.example/1", "A lace corset dress", "Red lace and more lace."),
                               ("https://a.example/2", "Lace up your running shoes", "Trainers.")):
            store.upsert_item(self.con, url=url, published_at="2026-09-01T00:00:00Z", source_method="rss",
                              title=title, fetched_at="2026-09-01T01:00:00Z", text_excerpt=ex, lang="en")
        self.con.commit()
        with contextlib.redirect_stdout(io.StringIO()):
            lexicon.cmd_extract(self.con)

    def tearDown(self):
        self.con.close()
        shutil.rmtree(self.tmp)

    def test_one_card_per_flagged_mention_with_marked_match(self):
        flagged, cards, misaligned = ls.inventory(self.con)
        self.assertEqual((flagged, len(cards), misaligned), (["lace"], 4, []))
        tasks = ls.build_tasks(cards)
        self.assertEqual(len({t["task_id"] for t in tasks}), 4)
        self.assertTrue(all("«" in t["body"] and "»" in t["body"] for t in tasks))
        self.assertEqual([o["value"] for o in tasks[0]["options"]], ["YES", "NO", "UNSURE"])
        self.assertNotIn("corset|", " ".join(t["task_id"] for t in tasks))

    def test_changed_text_is_reported_not_carded(self):
        self.con.execute("UPDATE items SET title='Running shoes' WHERE url='https://a.example/2'")
        _, cards, misaligned = ls.inventory(self.con)
        self.assertEqual(len(misaligned), 1)
        self.assertEqual(len(cards), 3)

    def test_task_id_binds_the_text_fingerprint(self):
        _, cards, _ = ls.inventory(self.con)
        c = cards[0]
        self.assertTrue(ls.task_id(c).endswith(c["context_sha256"][:12]))
        self.assertNotEqual(ls.inventory_sha(cards), ls.inventory_sha(cards[1:]))


if __name__ == "__main__":
    unittest.main()
