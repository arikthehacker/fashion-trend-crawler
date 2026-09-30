"""Tests for src/rag_questions.py: owner review decisions and the one-time question freeze.

usage: python src/test_rag_questions.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rag_questions as rq  # noqa: E402


def draft(qid, answerable=True, lang="en", filters=None):
    return {"question_id": qid, "question": f"Question {qid}?", "query": "ballet flats",
            "answerable_expected": answerable, "language": lang, "query_type": "term", "filters": filters or {},
            "reference_time": "2026-09-30T08:00:00Z", "dataset_version": "v1", "drafted_by": "machine_draft"}


class QuestionReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.p = {k: os.path.join(self.tmp, k) for k in ("drafts", "reviews", "frozen", "manifest")}
        with open(self.p["drafts"], "w", encoding="utf-8") as f:
            for row in (draft("q001"), draft("q002", False), draft("q003", lang="ja"), draft("q004")):
                f.write(json.dumps(row) + "\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def review(self, qid, action, **kw):
        return rq.record_review(qid, action, drafts=self.p["drafts"], reviews=self.p["reviews"], **kw)

    def status(self):
        return rq.review_status(self.p["drafts"], self.p["reviews"])

    def freeze(self):
        return rq.freeze(**self.p)

    def test_invalid_decisions_are_refused(self):
        with self.assertRaises(ValueError):
            self.review("q999", "approve")
        with self.assertRaises(ValueError):
            self.review("q001", "edit")
        with self.assertRaises(ValueError):
            self.review("q001", "approve", edits={"query": "x"})
        with self.assertRaises(ValueError):
            self.review("q001", "duplicate")
        with self.assertRaises(ValueError):
            self.review("q001", "maybe")
        with self.assertRaises(ValueError):
            self.review("q001", "edit", edits={"filters": {"as_of": "tomorrow"}})
        self.assertFalse(os.path.exists(self.p["reviews"]))

    def test_freeze_needs_every_question_reviewed_and_none_ambiguous(self):
        self.review("q001", "approve")
        with self.assertRaises(RuntimeError):
            self.freeze()
        for qid in ("q002", "q003"):
            self.review(qid, "approve")
        self.review("q004", "ambiguous", note="unclear scope")
        self.assertFalse(self.status()["ready_to_freeze"])
        with self.assertRaises(RuntimeError):
            self.freeze()
        self.review("q004", "approve")  # the latest decision counts
        self.assertTrue(self.status()["ready_to_freeze"])

    def test_freeze_applies_edits_drops_rejects_and_runs_once(self):
        self.review("q001", "edit", edits={"question": "What is said about ballet flats?", "query": "ballet flat",
                                           "filters": {"languages": ["en"]}})
        self.review("q002", "reject", note="too vague")
        self.review("q003", "approve")
        self.review("q004", "duplicate", duplicate_of="q001")
        body = self.freeze()
        self.assertEqual(body["question_ids"], ["q001", "q003"])
        self.assertEqual((body["total"], body["answerable_expected"], body["unanswerable_expected"]), (2, 2, 0))
        self.assertEqual(body["languages"], {"en": 1, "ja": 1})
        frozen, manifest = rq.load_frozen(self.p["frozen"], self.p["manifest"])
        self.assertEqual(frozen[0].question, "What is said about ballet flats?")
        self.assertEqual(frozen[0].filters.languages, ["en"])
        self.assertEqual(frozen[0].review_status, "edited")
        self.assertEqual(frozen[1].review_status, "approved")
        self.assertEqual(manifest["questions_sha256"], body["questions_sha256"])
        with self.assertRaises(RuntimeError):
            self.freeze()

    def test_reviews_of_an_older_draft_file_block_the_freeze(self):
        for qid in ("q001", "q002", "q003", "q004"):
            self.review(qid, "approve")
        with open(self.p["drafts"], "a", encoding="utf-8") as f:
            f.write(json.dumps(draft("q005")) + "\n")
        self.assertTrue(self.status()["stale_reviews"])
        with self.assertRaises(RuntimeError):
            self.freeze()

    def test_a_changed_frozen_file_is_detected(self):
        for qid in ("q001", "q002", "q003", "q004"):
            self.review(qid, "approve")
        self.freeze()
        with open(self.p["frozen"], "a", encoding="utf-8") as f:
            f.write(json.dumps(draft("q009")) + "\n")
        with self.assertRaises(RuntimeError):
            rq.load_frozen(self.p["frozen"], self.p["manifest"])


if __name__ == "__main__":
    unittest.main()
