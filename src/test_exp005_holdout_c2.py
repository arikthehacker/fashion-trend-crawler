"""Tests for the EXP-005 holdout C2 runner (src/exp005_holdout_c2.py): record-for-record parity
with exp005_v2.answer_question on scripted responses, the cost-cap stop, the frozen-packet
check and the review deck. Throwaway corpus, scripted provider, no network.

usage: python src/test_exp005_holdout_c2.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_holdout as h  # noqa: E402
import exp005_holdout_c2 as c2  # noqa: E402
import exp005_v2 as v2  # noqa: E402
import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ScriptedProvider  # noqa: E402
from rag_answer import AppQuestion  # noqa: E402
from rag_schema import Filters  # noqa: E402
from test_exp005_v2 import ABSTAIN, answer  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402

PROMPT = "Return JSON."
TEXT = "What is said about ballet flats?"


def comparable(record):
    attempts = [{k: v for k, v in a.items() if k not in ("latency_ms", "messages_sha256")} for a in record["attempts"]]
    keep = ("status", "answer", "rendered_answer", "validation", "context_sha256", "error", "question_id")
    return {"attempts": attempts, "item_ids": record["retrieval"]["item_ids"], **{k: record.get(k) for k in keep}}


class C2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        db = os.path.join(cls.tmp, "store.db")
        con = store.connect(db)
        store.migrate(con)
        for u, p, f, t, e, lang in ITEMS:
            store.upsert_item(con, url=u, published_at=p, source_method="rss", title=t, fetched_at=f, text_excerpt=e, lang=lang)
        con.commit()
        con.close()
        cls.corpus = rc.open_corpus(db)
        ri.build_index(cls.corpus, os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.index = ri.Index(os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.q = h.HoldoutQuestion(question_id="h001", question=TEXT, retrieval_query=TEXT, filters=Filters(),
                                  categories=["direct"], primary_category="direct", probes="A test question.")
        cls.packet = h.build_packet(cls.q, cls.corpus, cls.index, PROMPT)
        cls.ids = cls.packet["item_ids"]

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def both(self, responses):
        ref = v2.answer_question(AppQuestion("h001", TEXT, TEXT, Filters()), ScriptedProvider(list(responses)),
                                 self.corpus, self.index, PROMPT)
        p = ScriptedProvider(list(responses))
        mine = c2.generate(self.q, self.packet, p, self.corpus, PROMPT, c2.Budget())
        return ref, mine, p

    def test_parity_with_answer_question(self):
        self.assertEqual(self.packet["status"], "packet_built")
        self.assertGreaterEqual(len(self.ids), 2)
        a, b = self.ids[0], self.ids[1]
        cases = {"answered": [answer([a, b], lim_ids=[a])],
                 "retry then answered": ["not json", answer([a])],
                 "rejected_schema": ["not json", "still not json"],
                 "model_abstention": [ABSTAIN],
                 "rejected_citation": [answer([a], lim_ids=[987654])],
                 "provider_error": []}
        for name, responses in cases.items():
            ref, mine, _ = self.both(responses)
            self.assertEqual(comparable(mine), comparable(ref), name)

    def test_the_retry_messages_match_too(self):
        ref_p = ScriptedProvider(["not json", answer([self.ids[0]])])
        v2.answer_question(AppQuestion("h001", TEXT, TEXT, Filters()), ref_p, self.corpus, self.index, PROMPT)
        _, _, p = self.both(["not json", answer([self.ids[0]])])
        self.assertEqual(p.calls, ref_p.calls)
        self.assertEqual(h.sha256_json(p.calls[0]), self.packet["messages_sha256"])

    def test_cost_cap_stops_before_the_call(self):
        p = ScriptedProvider([answer([self.ids[0]])])
        budget = c2.Budget(cap=0.0)
        r = c2.generate(self.q, self.packet, p, self.corpus, PROMPT, budget)
        self.assertEqual((r["status"], len(p.calls), budget.stopped), ("cost_cap_stop", 0, True))

    def test_a_changed_packet_is_refused_before_the_call(self):
        bad = dict(self.packet, messages_sha256="0" * 64)
        p = ScriptedProvider([answer([self.ids[0]])])
        with self.assertRaises(RuntimeError):
            c2.generate(self.q, bad, p, self.corpus, PROMPT, c2.Budget())
        self.assertEqual(p.calls, [])

    def test_review_cards_follow_the_protocol_and_hide_the_c1_label(self):
        a = self.ids[0]
        _, rec, _ = self.both([answer([a], lim_ids=[a], n_claims=2)])
        _, abst, _ = self.both([ABSTAIN])
        abst = dict(abst, question_id="h002")
        packets = [self.packet, dict(self.packet, question_id="h002")]
        tasks = c2.review_tasks([rec, abst], packets)
        kinds = sorted((t["question_id"], t["kind"], t["target"]) for t in tasks)
        self.assertEqual(kinds, [("h001", "answer_completeness", "answer"), ("h001", "claim_support", "claim 0"),
                                 ("h001", "claim_support", "claim 1"), ("h001", "claim_support", "limitation 1"),
                                 ("h001", "limitation_uncited", "limitation 0"),
                                 ("h002", "limitation_uncited", "limitation 0")])
        for t in tasks:
            self.assertNotIn("SUFFICIENT", t["body"])
            self.assertTrue(t["options"] and t["prompt"])

    def test_summary_counts_failures_and_schema_validity(self):
        _, ok, _ = self.both([answer([self.ids[0]])])
        _, bad, _ = self.both(["x", "y"])
        bad = dict(bad, question_id="h002")
        s = c2.summarize([ok, bad], c2.Budget())
        self.assertEqual(s["final_schema_valid"], "1/2")
        self.assertEqual(s["first_attempt_schema_valid"], "1/2")
        self.assertEqual(s["deterministic_integrity_failures"], {"h002": "rejected_schema"})
        self.assertEqual(json.loads(json.dumps(s))["schema_retries"], 1)


if __name__ == "__main__":
    unittest.main()
