"""Tests for the EXP-005 context-only adjudication (src/exp005_adjudicate.py). Throwaway corpus,
no network, no provider.

usage: python src/test_exp005_adjudicate.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005 as v1  # noqa: E402
import exp005_adjudicate as adj  # noqa: E402
import exp005_review as r1  # noqa: E402
import exp005_review_v2 as rv2  # noqa: E402
import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
from test_exp005 import question  # noqa: E402
from test_rag import ITEMS  # noqa: E402


class AdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        db = os.path.join(cls.tmp, "store.db")
        con = store.connect(db)
        store.migrate(con)
        cls.ids = [store.upsert_item(con, url=u, published_at=p, source_method="rss", title=t, fetched_at=f,
                                     text_excerpt=e, lang=lang)[0] for u, p, f, t, e, lang in ITEMS]
        con.commit()
        con.close()
        cls.corpus = rc.open_corpus(db)

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def record(self, qid, role, status, answer, ids=None):
        ids = ids or self.ids[:3]
        q = question(qid)
        packet = v1.serialize_context(rc.get_items(self.corpus, ids), q.filters)
        return {"question_id": qid, "question": q.question, "role": role, "status": status, "answer": answer,
                "filters": q.filters.model_dump(mode="json", exclude_none=True),
                "retrieval": {"item_ids": ids}, "context_sha256": adj._sha(packet)}

    def batch(self):
        a, b = self.ids[0], self.ids[1]
        abstain = {"insufficient_evidence": True, "claims": [],
                   "limitations": [{"text": "No item mentions it.", "supporting_item_ids": []}]}
        answered = {"insufficient_evidence": False,
                    "claims": [{"text": "Finding 0.", "supporting_item_ids": [a]},
                               {"text": "Finding 1.", "supporting_item_ids": [b]}],
                    "limitations": [{"text": "Sparse.", "supporting_item_ids": []}]}
        records = [self.record("q013", "regression_probe", "answered", answered),
                   self.record("q017", "fresh", "model_abstention", abstain),
                   self.record("q023", "fresh", "model_abstention", abstain),
                   self.record("q031", "fresh", "answered", answered)]
        return records, {r["question_id"]: question(r["question_id"]) for r in records}

    def test_tasks_are_the_listed_ones_with_original_options(self):
        records, questions = self.batch()
        tasks = adj.build_tasks(records, questions, self.corpus)
        self.assertEqual([t["task_id"] for t in tasks], list(adj.TASKS))
        original = {t["task_id"]: t for t in rv2.fresh_tasks(records, self.corpus) + rv2.probe_tasks(records, self.corpus)}
        for t in tasks:
            self.assertEqual(t["options"], original[t["task_id"]]["options"])
            self.assertEqual(t["kind"], original[t["task_id"]]["kind"])

    def test_cards_hold_the_packet_and_no_outside_material(self):
        records, questions = self.batch()
        tasks = {t["task_id"]: t for t in adj.build_tasks(records, questions, self.corpus)}
        body = tasks["q017:abstention"]["body"]
        self.assertTrue(body.startswith(adj.HEADER))
        self.assertIn("Do not open links", body)
        self.assertIn("MODEL ABSTAINED", body)
        for e in rc.get_items(self.corpus, self.ids[:3]):
            self.assertIn(f"item {e.item_id}", body)
            self.assertIn(f"url: {e.url}   (text only, do not open)", body)
        for t in tasks.values():
            self.assertNotIn("utm_source", t["body"])
            self.assertNotIn("INCORRECT", t["body"])  # no earlier judgment is shown
        claim = tasks["q031:claim 1"]["body"]
        self.assertIn("CITED ITEMS FROM THE PACKET", claim)
        self.assertNotIn(f"item {self.ids[0]}\n", claim)  # only the cited item
        self.assertIn("REGRESSION PROBE", tasks["q013:regression:summary_detail"]["body"])

    def test_packet_that_does_not_verify_is_refused(self):
        records, questions = self.batch()
        records[1]["context_sha256"] = "0" * 64
        with self.assertRaises(RuntimeError):
            adj.build_tasks(records, questions, self.corpus)

    def test_merge_replaces_only_adjudicated_judgments(self):
        row = lambda t, v, at="2026-10-01T00:00:00Z", kind="x": {"task_id": t, "kind": kind, "value": v,
                                                                 "reviewed_at": at, "reviewer": "ariella"}
        original = [row("q017:abstention", "INCORRECT", kind="abstention"), row("q005:claim 0", "SUPPORTED"),
                    row("q017:abstention", "outside note", kind="note")]
        adjudicated = [row("q017:abstention", "CORRECT", "2026-10-02T00:00:00Z", "abstention"),
                       row("q017:abstention", "packet only", kind="note")]
        rows, changes = adj.merge(original, adjudicated)
        self.assertEqual(changes, [{"task_id": "q017:abstention", "mixed_boundary": "INCORRECT",
                                    "context_only": "CORRECT"}])
        self.assertEqual({r["task_id"]: r["value"] for r in rows},
                         {"q017:abstention": "CORRECT", "q005:claim 0": "SUPPORTED"})
        self.assertNotIn("note", {r["kind"] for r in rows})
        self.assertEqual(original[0]["value"], "INCORRECT")  # the original rows are not mutated
        with self.assertRaises(RuntimeError):
            adj.merge(original, [row("q099:abstention", "CORRECT")])

    def test_context_grounded_metrics_use_the_frozen_formula(self):
        records = [{"question_id": "q017", "status": "model_abstention", "role": "fresh"},
                   {"question_id": "q031", "status": "answered", "role": "fresh"}]
        rv = lambda t, v: {"task_id": t, "kind": "x", "value": v, "reviewed_at": "2026-10-01T00:00:00Z",
                           "reviewer": "ariella"}
        original = [rv("q017:abstention", "INCORRECT"), rv("q031:claim 0", "SUPPORTED"),
                    rv("q031:sufficiency", "NO"), rv("q031:completeness", "PARTIAL")]
        before = rv2.metrics_v2(records, original)
        merged, _ = adj.merge(original, [rv("q017:abstention", "CORRECT"), rv("q031:sufficiency", "YES")])
        after = rv2.metrics_v2(records, merged)
        self.assertEqual((before["abstention"]["incorrect"], before["abstention"]["missed"]), (1, 1))
        self.assertEqual((after["abstention"]["correct"], after["abstention"]["missed"]), (1, 0))
        self.assertEqual((before["grounded"], after["grounded"]), (1, 2))

    def test_freeze_and_log_paths_are_separate_from_the_original_review(self):
        self.assertNotIn(adj.LOG, (rv2.FRESH_REVIEWS, rv2.PROBE_REVIEWS))
        self.assertNotIn(adj.FROZEN, adj.ORIGINAL.values())
        self.assertNotEqual(adj.RESULT, adj.ORIGINAL_SCORES)
        queue = {"reviews_path": os.path.relpath(adj.LOG, store.ROOT), "outputs_sha256": "a" * 64}
        self.assertEqual(r1.reviews_file(queue), os.path.join(store.ROOT, os.path.relpath(adj.LOG, store.ROOT)))


if __name__ == "__main__":
    unittest.main()
