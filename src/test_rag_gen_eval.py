"""Tests for the EXP-004 generation harness (src/rag_gen_eval.py). No network, no key.

usage: python src/test_rag_gen_eval.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_gen_eval as ge  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ScriptedProvider  # noqa: E402
from rag_eval import Question  # noqa: E402
from rag_schema import Filters  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402


def question(qid, query, answerable=True, **filters):
    return Question(question_id=qid, question=f"What is said about {query}?", query=query,
                    answerable_expected=answerable, language="en", query_type="term", filters=Filters(**filters),
                    reference_time="2026-09-30T08:00:00Z", dataset_version="v1", drafted_by="test")


class GenerationHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        db = os.path.join(self.tmp, "store.db")
        con = store.connect(db)
        store.migrate(con)
        self.ids = [store.upsert_item(con, url=u, published_at=p, source_method="rss", title=t, fetched_at=f,
                                      text_excerpt=e, lang=lang)[0] for u, p, f, t, e, lang in ITEMS]
        con.commit()
        con.close()
        self.corpus = rc.open_corpus(db)
        ri.build_index(self.corpus, os.path.join(self.tmp, "index"), encoder=fake_encoder)
        self.index = ri.Index(os.path.join(self.tmp, "index"), encoder=fake_encoder)
        self.out = os.path.join(self.tmp, "results")
        self.questions = [question("q001", "ballet flats"), question("q002", "cashmere"),
                          question("q003", "denim", answerable=False, end_date="2010-01-01")]

    def tearDown(self):
        self.corpus.close()
        self.index.fts.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_offline_run_writes_audit_metrics_and_template(self):
        body = ge.run(self.questions, ge.RefuseAllProvider(), self.corpus, self.index, self.out, "dev-check")
        m = body["metrics"]
        self.assertEqual(m["status_counts"], {"insufficient_evidence": 3})
        self.assertEqual(m["answerability_source"], "drafted_expectation_not_gold")
        self.assertEqual(m["correct_refusal_rate_unanswerable"], 1.0)
        self.assertEqual(m["false_refusal_rate_answerable"], 1.0)
        audit = [json.loads(line) for line in open(os.path.join(self.out, "dev-check.audit.jsonl"), encoding="utf-8")]
        self.assertEqual([r["question_id"] for r in audit], ["q001", "q002", "q003"])
        for key in ("retrieval", "provider", "prompt_version", "schema_version", "validation", "answer", "latency_s",
                    "timestamp", "tool_calls"):
            self.assertIn(key, audit[0])
        self.assertEqual(audit[2]["attempts"], [])  # no evidence, so no model call
        self.assertNotIn("debug", audit[0]["answer"])

    def test_grounding_metrics_count_invalid_citations(self):
        a = self.ids[0]
        good = json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": [a]}]})
        bad = json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": [999999]}]})
        provider = ScriptedProvider([good, bad])
        m = ge.run(self.questions[:2], provider, self.corpus, self.index, self.out, "dev-mixed",
                   cost_fn=lambda model, usage, at: 0.001)["metrics"]
        self.assertEqual(m["status_counts"], {"answered": 1, "rejected": 1})
        self.assertEqual((m["citations"], m["citation_validity"]), (2, 0.5))
        self.assertEqual(m["estimated_cost_usd"]["total"], 0.002)
        template = [json.loads(line) for line in open(os.path.join(self.out, "dev-mixed.human_review.jsonl"),
                                                      encoding="utf-8")]
        self.assertEqual(len(template), 1)
        self.assertEqual(template[0]["claims"], [{"text": "x", "grade": None}])

    def test_gold_answerability_is_used_when_judgments_cover_every_question(self):
        judged = {"q001": {self.ids[0]: "relevant"}, "q002": {self.ids[1]: "not_relevant"}}
        m = ge.run(self.questions[:2], ge.RefuseAllProvider(), self.corpus, self.index, self.out, "dev-gold",
                   judged=judged)["metrics"]
        self.assertEqual(m["answerability_source"], "gold")
        self.assertEqual((m["correct_refusal_rate_unanswerable"], m["false_refusal_rate_answerable"]), (1.0, 1.0))

    def test_a_run_is_never_overwritten(self):
        ge.run(self.questions[:1], ge.RefuseAllProvider(), self.corpus, self.index, self.out, "test-generation-v1")
        with self.assertRaises(FileExistsError):
            ge.run(self.questions[:1], ge.RefuseAllProvider(), self.corpus, self.index, self.out, "test-generation-v1")

    def test_human_summary_counts_unsupported_claims(self):
        path = os.path.join(self.tmp, "review.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"question_id": "q001", "correctness": 3, "completeness": 2, "usefulness": None,
                                "claims": [{"text": "a", "grade": "supported"}, {"text": "b", "grade": "unsupported"},
                                           {"text": "c", "grade": None}], "reviewer": "ariella",
                                "reviewed_at": "2026-10-01T00:00:00Z", "notes": ""}) + "\n")
        s = ge.human_summary(path)
        self.assertEqual((s["claims"], s["unsupported_claims"], s["unreviewed_claims"]), (3, 1, 1))
        self.assertEqual((s["mean_correctness"], s["mean_usefulness"]), (3, None))


if __name__ == "__main__":
    unittest.main()
