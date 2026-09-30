"""Tests for src/rag_review.py: the blind EXP-004 relevance queue and its judgment log.

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
import rag_questions as rq  # noqa: E402
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
        self.p = {k: os.path.join(self.tmp, k) for k in ("drafts", "reviews", "frozen", "manifest")}
        with open(self.p["drafts"], "w", encoding="utf-8") as f:
            for qid, filters in (("q001", {}), ("q002", {"as_of": "2026-09-24", "temporal_mode": "replay"})):
                f.write(json.dumps({"question_id": qid, "question": "What?", "query": "x",
                                    "answerable_expected": True, "language": "en", "query_type": "term",
                                    "filters": filters, "reference_time": "2026-09-30T08:00:00Z",
                                    "dataset_version": "v1", "drafted_by": "machine_draft"}) + "\n")
        for qid in ("q001", "q002"):
            rq.record_review(qid, "approve", drafts=self.p["drafts"], reviews=self.p["reviews"])
        rq.freeze(**self.p)
        rows = [{"question_id": "q001", "item_id": self.items[0], "pool_source": ["dense"]},
                {"question_id": "q001", "item_id": self.items[1], "pool_source": ["bm25:words"]},
                {"question_id": "q001", "item_id": self.items[2], "pool_source": ["dense", "hybrid:auto"]},
                {"question_id": "q002", "item_id": self.items[3], "pool_source": ["bm25:auto"]}]
        self.pool = os.path.join(self.tmp, "pool.jsonl")
        with open(self.pool, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        self.pool_manifest = os.path.join(self.tmp, "pool.manifest.json")
        with open(self.pool_manifest, "w", encoding="utf-8") as f:
            json.dump({"questions_sha256": ev.sha256_file(self.p["frozen"]), "pool_sha256": ev.pool_fingerprint(rows),
                       "pool_file_sha256": ev.sha256_file(self.pool)}, f)
        self.log = os.path.join(self.tmp, "judgments", "log.jsonl")

    def tearDown(self):
        label_tool.QUEUE_DIR = self._queue_dir
        shutil.rmtree(self.tmp)

    def queue(self):
        path = rv.make_queue(self.pool, self.pool_manifest, self.log, self.p["frozen"], self.p["manifest"])
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_cards_are_blind_to_methods(self):
        q = self.queue()
        self.assertEqual(sorted((c["question_id"], c["item_id"]) for c in q["cards"]),
                         sorted([("q001", i) for i in self.items[:3]] + [("q002", self.items[3])]))
        for card in q["cards"]:
            self.assertEqual(set(card), {"question_id", "question", "filters", "item_id"})
        self.assertNotIn("pool_source", json.dumps(q))
        self.assertEqual(q["cards"], self.queue()["cards"])
        self.assertEqual(q["cards"][-1]["filters"], "known to ARI3 by 2026-09-24")

    def test_pool_must_match_frozen_questions_and_its_manifest(self):
        with open(self.pool, "a", encoding="utf-8") as f:
            f.write(json.dumps({"question_id": "q002", "item_id": self.items[0], "pool_source": ["dense"]}) + "\n")
        with self.assertRaises(RuntimeError):
            self.queue()

    def test_judgments_append_and_latest_wins(self):
        q = self.queue()
        card = q["cards"][0]
        rv.record(self.con, q, card, "relevant")
        rv.record(self.con, q, card, "not_relevant")
        rv.record(self.con, q, q["cards"][1], "unsure")
        lines = ev.load_jsonl(self.log, ev.Judgment)
        self.assertEqual(len(lines), 3)
        self.assertEqual({j.task for j in lines}, {"rag_relevance"})
        self.assertEqual({j.pool_sha256 for j in lines}, {q["pool_sha256"]})
        self.assertEqual(rv.left(q), (2, 4))
        self.assertEqual(ev.judgments_by_question(lines)["q001"][card["item_id"]], "not_relevant")

    def test_invalid_judgment_value_is_rejected(self):
        q = self.queue()
        with self.assertRaises(ValueError):
            rv.record(self.con, q, q["cards"][0], "maybe")
        self.assertFalse(os.path.exists(self.log))


if __name__ == "__main__":
    unittest.main()
