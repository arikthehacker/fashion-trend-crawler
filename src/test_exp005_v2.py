"""Tests for EXP-005 Prompt v2 (src/exp005_v2.py, src/exp005_review_v2.py). Scripted
provider, throwaway corpus, no network.

usage: python src/test_exp005_v2.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_review_v2 as rv2  # noqa: E402
import exp005_v2 as v2  # noqa: E402
import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ScriptedProvider  # noqa: E402
from test_exp005 import question  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402


def answer(claim_ids, lim_ids=(), n_claims=1):
    return json.dumps({"insufficient_evidence": False,
                       "claims": [{"text": f"Finding {k}.", "supporting_item_ids": list(claim_ids)} for k in range(n_claims)],
                       "limitations": [{"text": "Evidence is sparse.", "supporting_item_ids": []},
                                       {"text": "One item is only a headline.", "supporting_item_ids": list(lim_ids)}]})


ABSTAIN = json.dumps({"insufficient_evidence": True, "claims": [],
                      "limitations": [{"text": "Nothing in the evidence covers this.", "supporting_item_ids": []}]})


class SchemaV2Tests(unittest.TestCase):
    def test_valid(self):
        self.assertIsNotNone(v2.parse(answer([1] * 10, n_claims=4))[0])
        self.assertIsNotNone(v2.parse(ABSTAIN)[0])

    def test_invalid(self):
        bad = [answer([1], n_claims=5), answer([1] * 11),
               json.dumps({"insufficient_evidence": False, "answer_summary": {"text": "s", "supporting_item_ids": [1]},
                           "claims": [{"text": "x", "supporting_item_ids": [1]}]}),
               json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": [1]}],
                           "limitations": ["a plain string"]}),
               json.dumps({"insufficient_evidence": True, "claims": [{"text": "x", "supporting_item_ids": [1]}]}),
               json.dumps({"insufficient_evidence": False, "claims": []})]
        for raw in bad:
            self.assertIsNone(v2.parse(raw)[0], raw[:90])

    def test_rendered_answer_is_the_claims_only(self):
        a, _ = v2.parse(answer([1], n_claims=2))
        self.assertEqual(v2.render(a), "Finding 0. Finding 1.")


class PipelineV2Tests(unittest.TestCase):
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
        ri.build_index(cls.corpus, os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.index = ri.Index(os.path.join(cls.tmp, "index"), encoder=fake_encoder)

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_q(self, provider, q=None):
        return v2.answer_question(q or question(), provider, self.corpus, self.index, "Return JSON.")

    def test_answered_with_cited_limitation_validated(self):
        a, b = self.ids[0], self.ids[2]
        r = self.run_q(ScriptedProvider([answer([a, b], lim_ids=[a])]))
        self.assertEqual(r["status"], "answered")
        self.assertEqual(r["rendered_answer"], "Finding 0.")
        self.assertEqual(r["validation"]["citations"], 3)

    def test_limitation_citation_outside_context_is_caught(self):
        a, shop = self.ids[0], self.ids[3]
        r = self.run_q(ScriptedProvider([answer([a], lim_ids=[shop])]), question(languages=["en"]))
        self.assertEqual(r["status"], "rejected_citation")
        self.assertIn("limitation 1", {v["where"] for v in r["validation"]["violations"]})

    def test_retry_policy_unchanged(self):
        p = ScriptedProvider(["not json", answer([self.ids[0]])])
        self.assertEqual(self.run_q(p)["status"], "answered")
        self.assertEqual(len(p.calls), 2)
        p = ScriptedProvider([ABSTAIN])
        self.assertEqual((self.run_q(p)["status"], len(p.calls)), ("model_abstention", 1))

    def test_probe_and_fresh_tasks_are_separate(self):
        a = self.ids[0]
        probe = dict(self.run_q(ScriptedProvider([answer([a])]), question("q013")), role="regression_probe")
        fresh = dict(self.run_q(ScriptedProvider([answer([a], lim_ids=[a], n_claims=2)]), question("q005")), role="fresh")
        abstain = dict(self.run_q(ScriptedProvider([ABSTAIN]), question("q023")), role="fresh")
        f = rv2.fresh_tasks([probe, fresh, abstain], self.corpus)
        p = rv2.probe_tasks([probe, fresh, abstain], self.corpus)
        self.assertEqual({t["question_id"] for t in f}, {"q005", "q023"})
        self.assertEqual([t["task_id"] for t in p], ["q013:regression:summary_detail", "q013:regression:coverage",
                                                     "q013:regression:uncited_limitation"])
        kinds = {t["task_id"]: t["kind"] for t in f}
        self.assertEqual(kinds["q005:limitation 0"], "limitation_uncited")
        self.assertEqual(kinds["q005:limitation 1"], "claim_support")
        self.assertEqual(kinds["q023:abstention"], "abstention")
        self.assertIn("q023:limitation 0", kinds)
        self.assertIn("POST-TUNING REGRESSION PROBE", p[0]["body"])


class ReviewV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.queue = {"reviews_path": os.path.join(self.tmp, "log.jsonl"), "outputs_sha256": "a" * 64}
        self.task = {"task_id": "q005:claim 0", "question_id": "q005", "target": "claim 0",
                     "options": [{"value": "SUPPORTED"}, {"value": "UNSUPPORTED"}, {"value": "UNSURE"}]}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_notes_do_not_complete_tasks_or_enter_metrics(self):
        import exp005_review as r1
        rv2.record_note(self.queue, self.task, "cites the wrong item")
        self.assertEqual(rv2.done(self.queue), set())
        with self.assertRaises(ValueError):
            rv2.record_note(self.queue, self.task, "   ")
        r1.record(self.queue, dict(self.task, kind="claim_support"), "SUPPORTED")
        self.assertEqual(rv2.done(self.queue), {"q005:claim 0"})
        reviews = r1.load_reviews(self.queue["reviews_path"])
        m = rv2.metrics_v2([{"question_id": "q005", "status": "answered", "role": "fresh"},
                            {"question_id": "q013", "status": "answered", "role": "regression_probe"}], reviews)
        self.assertEqual((m["supported"], m["notes"], m["claim_support_precision"]), (1, 1, 1.0))
        self.assertEqual(m["evaluable_outputs"], 0)  # q005 has no sufficiency judgment yet; q013 is never counted

    def test_metrics_v2(self):
        rv = lambda t, v: {"task_id": t, "kind": "x", "value": v, "reviewed_at": "2026-10-01T00:00:00Z", "reviewer": "a"}
        records = [{"question_id": "q1", "status": "answered", "role": "fresh"},
                   {"question_id": "q2", "status": "model_abstention", "role": "fresh"},
                   {"question_id": "q13", "status": "answered", "role": "regression_probe"}]
        reviews = [rv("q1:claim 0", "SUPPORTED"), rv("q1:limitation 1", "UNSUPPORTED"), rv("q1:limitation 0", "YES"),
                   rv("q1:sufficiency", "YES"), rv("q1:completeness", "COMPLETE"), rv("q2:abstention", "CORRECT"),
                   rv("q13:claim 0", "UNSUPPORTED")]
        m = rv2.metrics_v2(records, reviews)
        self.assertEqual((m["supported"], m["unsupported"]), (1, 1))  # the probe's judgment never counts
        self.assertEqual((m["evaluable_outputs"], m["grounded"]), (2, 1))
        self.assertEqual(m["uncited_item_specific_limitations"], 1)


if __name__ == "__main__":
    unittest.main()
