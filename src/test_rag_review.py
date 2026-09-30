"""Tests for src/rag_review.py: the EXP-004 relevance queue and its judgment log.

usage: python src/test_rag_review.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import label_tool  # noqa: E402
import rag_eval as ev  # noqa: E402
import rag_review as rv  # noqa: E402


class RelevanceQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._queue_dir = label_tool.QUEUE_DIR
        label_tool.QUEUE_DIR = os.path.join(self.tmp, "queues")
        self.con = store.connect(":memory:")
        store.migrate(self.con)
        self.items = [store.upsert_item(self.con, url=f"https://www.vogue.com/article/f{n}", title=f"F{n}",
                                        published_at="2026-09-25T10:00:00Z", fetched_at="2026-09-25T12:00:00Z",
                                        source_method="rss", text_excerpt="x")[0] for n in range(4)]
        self.questions = os.path.join(self.tmp, "q.jsonl")
        with open(self.questions, "w", encoding="utf-8") as f:
            for qid, filters in (("q001", {}), ("q002", {"as_of": "2026-09-24", "temporal_mode": "replay"})):
                f.write(json.dumps({"question_id": qid, "question": "What?", "query": "x",
                                    "answerable_expected": True, "language": "en", "query_type": "term",
                                    "filters": filters, "reference_time": "2026-09-30T08:00:00Z",
                                    "dataset_version": "v1", "drafted_by": "machine_draft"}) + "\n")
        self.pool = os.path.join(self.tmp, "pool.jsonl")
        with open(self.pool, "w", encoding="utf-8") as f:
            for qid, item, src in (("q001", self.items[0], ["dense"]), ("q001", self.items[1], ["bm25:words"]),
                                   ("q001", self.items[2], ["dense", "hybrid:auto"]),
                                   ("q002", self.items[3], ["bm25:auto"])):
                f.write(json.dumps({"question_id": qid, "item_id": item, "pool_source": src}) + "\n")
        self.log = os.path.join(self.tmp, "judgments", "log.jsonl")

    def tearDown(self):
        label_tool.QUEUE_DIR = self._queue_dir
        shutil.rmtree(self.tmp)

    def queue(self):
        with open(rv.make_queue(self.pool, self.questions, self.log), encoding="utf-8") as f:
            return json.load(f)

    def test_queue_holds_every_pooled_pair_and_is_deterministic(self):
        q = self.queue()
        self.assertEqual(q["kind"], "rag_relevance")
        self.assertEqual(sorted((c["question_id"], c["item_id"]) for c in q["cards"]),
                         sorted([("q001", i) for i in self.items[:3]] + [("q002", self.items[3])]))
        self.assertEqual(q["cards"], self.queue()["cards"])
        self.assertEqual(q["cards"][-1]["filters"], "known to ARI3 by 2026-09-24")

    def test_judgments_append_and_latest_wins(self):
        q = self.queue()
        card = q["cards"][0]
        rv.record(self.con, q, card, "relevant")
        rv.record(self.con, q, card, "not_relevant")
        rv.record(self.con, q, q["cards"][1], "unsure")
        lines = ev.load_jsonl(self.log, ev.Judgment)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].url.startswith("https://"))
        self.assertEqual(rv.left(q), (2, 4))
        self.assertEqual(ev.gold(lines), {"q001": set()})

    def test_invalid_judgment_value_is_rejected(self):
        q = self.queue()
        with self.assertRaises(ValueError):
            rv.record(self.con, q, q["cards"][0], "maybe")
        self.assertFalse(os.path.exists(self.log))


if __name__ == "__main__":
    unittest.main()
