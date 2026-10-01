"""Tests for EXP-005 protocol v1 (src/exp005.py, src/exp005_review.py). Scripted provider,
throwaway corpus, no network.

usage: python src/test_exp005.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005 as x  # noqa: E402
import exp005_review as xr  # noqa: E402
import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ProviderError, ScriptedProvider  # noqa: E402
from rag_eval import Question  # noqa: E402
from rag_schema import Filters  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402

PROMPT = "Return JSON."


def answer(*ids, n_claims=1):
    return json.dumps({"insufficient_evidence": False,
                       "answer_summary": {"text": "Ballet flats appear in coverage.", "supporting_item_ids": list(ids)},
                       "claims": [{"text": f"Claim {k}.", "supporting_item_ids": list(ids)} for k in range(n_claims)],
                       "limitations": ["Excerpts only."]})


ABSTAIN = json.dumps({"insufficient_evidence": True, "answer_summary": None, "claims": [],
                      "limitations": ["No item covers this."]})


def question(qid="q001", query="ballet flats", **filters):
    return Question(question_id=qid, question=f"What is said about {query}?", query=query, answerable_expected=True,
                    language="en", query_type="term", filters=Filters(**filters),
                    reference_time="2026-09-30T08:00:00Z", dataset_version="v1", drafted_by="test")


class SchemaTests(unittest.TestCase):
    def test_valid_answers(self):
        self.assertIsNotNone(x.parse(answer(1, n_claims=4))[0])
        self.assertIsNotNone(x.parse(ABSTAIN)[0])

    def test_invalid_answers_are_rejected(self):
        bad = [answer(1, n_claims=5), "", "not json",
               json.dumps({"insufficient_evidence": False, "answer_summary": None,
                           "claims": [{"text": "x", "supporting_item_ids": [1]}]}),
               json.dumps({"insufficient_evidence": False, "answer_summary": {"text": "s", "supporting_item_ids": [1]},
                           "claims": [{"text": "uncited", "supporting_item_ids": []}]}),
               json.dumps({"insufficient_evidence": True, "answer_summary": None,
                           "claims": [{"text": "x", "supporting_item_ids": [1]}]}),
               json.dumps({"insufficient_evidence": False, "answer_summary": {"text": "s", "supporting_item_ids": [1]},
                           "claims": [{"text": "x", "supporting_item_ids": [1], "url": "https://made.up"}]}),
               json.dumps({"insufficient_evidence": True, "answer_summary": None, "claims": [],
                           "limitations": ["x" * 301]})]
        for raw in bad:
            self.assertIsNone(x.parse(raw)[0], raw[:80])

    def test_schema_fingerprint_is_stable(self):
        self.assertEqual(x.schema_json(), x.schema_json())


class PipelineTests(unittest.TestCase):
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
        cls.db = db
        cls.corpus = rc.open_corpus(db)
        ri.build_index(cls.corpus, os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.index = ri.Index(os.path.join(cls.tmp, "index"), encoder=fake_encoder)

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_q(self, provider, q=None):
        return x.answer_question(q or question(), provider, self.corpus, self.index, PROMPT)

    def test_serializer_is_ordered_bounded_and_deterministic(self):
        ev = rc.get_items(self.corpus, self.ids)
        ctx = x.serialize_context(ev, Filters())
        self.assertEqual([c["item_id"] for c in ctx], self.ids)
        self.assertNotIn("first_seen_at", ctx[0])
        self.assertIn("first_seen_at", x.serialize_context(ev, Filters(as_of="2026-09-30", temporal_mode="replay"))[0])
        self.assertEqual(ctx, x.serialize_context(ev, Filters()))
        self.assertEqual(list(ctx[0]), ["item_id", "outlet", "sector_group", "published_at", "language", "headline",
                                        "excerpt", "url"])

    def test_answered_with_store_provenance(self):
        a = self.ids[0]
        r = self.run_q(ScriptedProvider([answer(a)]))
        self.assertEqual(r["status"], "answered")
        self.assertTrue(r["validation"]["valid"])
        self.assertEqual(r["validation"]["citation_urls"], {a: ITEMS[0][0]})
        self.assertEqual(len(r["attempts"]), 1)

    def test_one_retry_only_for_unparseable_output(self):
        a = self.ids[0]
        p = ScriptedProvider(["not json", answer(a)])
        self.assertEqual(self.run_q(p)["status"], "answered")
        self.assertEqual(len(p.calls), 2)
        self.assertIn("did not match", p.calls[1][-1]["content"])
        r = self.run_q(ScriptedProvider(["", "still not json"]))
        self.assertEqual((r["status"], len(r["attempts"])), ("rejected_schema", 2))

    def test_no_retry_for_abstention_or_bad_citations(self):
        p = ScriptedProvider([ABSTAIN])
        self.assertEqual(self.run_q(p)["status"], "model_abstention")
        self.assertEqual(len(p.calls), 1)
        p = ScriptedProvider([answer(999999)])
        r = self.run_q(p)
        self.assertEqual((r["status"], len(p.calls)), ("rejected_citation", 1))
        self.assertEqual(r["validation"]["nonexistent_citations"], 2)

    def test_out_of_context_and_temporal_citations_are_caught(self):
        a, b, old, shop, ja = self.ids
        q = question(as_of="2026-09-24T23:00:00Z", temporal_mode="replay")
        r = self.run_q(ScriptedProvider([answer(old)]), q)
        self.assertEqual(r["status"], "rejected_citation")
        self.assertGreater(r["validation"]["temporal_violations"], 0)
        r = self.run_q(ScriptedProvider([answer(shop)]), question(languages=["en"]))
        self.assertFalse(r["validation"]["membership_valid"])

    def test_empty_context_is_a_system_abstention_without_a_call(self):
        p = ScriptedProvider([])
        r = self.run_q(p, question(end_date="2010-01-01"))
        self.assertEqual((r["status"], p.calls), ("system_abstention", []))

    def test_provider_error_is_recorded(self):
        r = self.run_q(ScriptedProvider([ProviderError("DeepSeek HTTP 503")]))
        self.assertEqual(r["status"], "provider_error")

    def test_review_tasks_follow_the_rubric(self):
        a = self.ids[0]
        answered = self.run_q(ScriptedProvider([answer(a, n_claims=2)]))
        abstained = dict(self.run_q(ScriptedProvider([ABSTAIN]), question("q002")), question_id="q002")
        tasks = xr.build_tasks([answered, abstained], self.corpus)
        kinds = [(t["task_id"], t["kind"]) for t in tasks]
        self.assertEqual(kinds, [("q001:summary", "claim_support"), ("q001:claim 0", "claim_support"),
                                 ("q001:claim 1", "claim_support"), ("q001:completeness", "answer_completeness"),
                                 ("q001:sufficiency", "context_sufficiency"), ("q001:limitations", "limitations"),
                                 ("q002:abstention", "abstention")])
        self.assertIn(ITEMS[0][3], tasks[0]["body"])  # the cited headline is shown

    def test_nothing_is_written_to_the_store(self):
        def read():
            with open(self.db, "rb") as f:
                return f.read()
        before = read()
        self.run_q(ScriptedProvider([answer(self.ids[0])]))
        self.assertEqual(read(), before)


class MetricTests(unittest.TestCase):
    def test_protocol_metrics(self):
        records = [{"question_id": "q1", "status": "answered"}, {"question_id": "q2", "status": "answered"},
                   {"question_id": "q3", "status": "model_abstention"}, {"question_id": "q4", "status": "rejected_citation"},
                   {"question_id": "q5", "status": "system_abstention"}, {"question_id": "q6", "status": "answered"}]
        rv = lambda t, v, at="2026-10-01T00:00:00Z": {"task_id": t, "value": v, "reviewed_at": at, "reviewer": "a"}
        reviews = [rv("q1:summary", "SUPPORTED"), rv("q1:claim 0", "SUPPORTED"), rv("q1:sufficiency", "YES"),
                   rv("q1:completeness", "COMPLETE"),
                   rv("q2:summary", "UNSURE"), rv("q2:claim 0", "UNSUPPORTED"), rv("q2:sufficiency", "NO"),
                   rv("q3:abstention", "INCORRECT", "2026-10-01T00:00:00Z"),
                   rv("q3:abstention", "CORRECT", "2026-10-01T00:05:00Z"),
                   rv("q6:claim 0", "SUPPORTED"), rv("q6:sufficiency", "UNSURE")]
        m = xr.metrics(records, reviews)
        self.assertEqual((m["supported"], m["unsupported"], m["claims_unsure"]), (3, 1, 1))
        self.assertEqual(m["claim_support_precision"], 0.75)
        self.assertEqual((m["evaluable_outputs"], m["grounded"]), (4, 2))  # q1, q2, q3, q4; q6 not evaluable
        self.assertEqual(m["abstention"], {"correct": 1, "incorrect": 0, "missed": 1, "precision": 1.0, "recall": 0.5})
        self.assertEqual(m["system_abstentions"], 1)


if __name__ == "__main__":
    unittest.main()
