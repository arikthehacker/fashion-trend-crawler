"""Tests for EXP-005 SC-1 (src/exp005_schema.py). Scripted provider, throwaway corpus and
paths, no network.

usage: python src/test_exp005_schema.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_schema as sc  # noqa: E402
import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ScriptedProvider  # noqa: E402
from test_exp005 import question  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402


def answer(ids, n_claims=1, claim_len=10):
    return json.dumps({"insufficient_evidence": False,
                       "claims": [{"text": "x" * claim_len, "supporting_item_ids": list(ids)} for _ in range(n_claims)],
                       "limitations": [{"text": "Evidence is sparse.", "supporting_item_ids": []}]})


ABSTAIN = json.dumps({"insufficient_evidence": True, "claims": [],
                      "limitations": [{"text": "Nothing in the evidence covers this.", "supporting_item_ids": []}]})


class UnitTests(unittest.TestCase):
    def test_violation_categories(self):
        err = ("claims: List should have at most 4 items after validation, not 6; claims.3.text: String should have "
               "at most 400 characters; limitations.0.text: String should have at most 300 characters; answer: bad")
        self.assertEqual(sc.violations(err), ["claim_count", "claim_length", "limitation_length", "other"])
        self.assertEqual(sc.violations(None), [])

    def test_prompt_v21_is_v2_plus_an_appended_section(self):
        d = sc.prompt_difference()
        self.assertIn("at most 400 characters", d["appended_text"])
        self.assertIn("at most 300 characters", d["appended_text"])

    def test_comparison_rule(self):
        f = lambda va, vb, capb, ia=0, ib=0: {"A": {"first_attempt_valid": va, "first_attempts_with_cap_violation": 8 - va,
                                                     "integrity_failures": ia},
                                               "B": {"first_attempt_valid": vb, "first_attempts_with_cap_violation": capb,
                                                     "integrity_failures": ib}}
        h = lambda g, u=0, part=0, wa=0: {"grounded": g, "unsupported": u, "abstention": {"incorrect": wa, "missed": 0},
                                          "completeness": {"PARTIAL": part, "INSUFFICIENT": 0}}
        self.assertEqual(sc.classify(f(4, 8, 0)), "PENDING_HUMAN_REVIEW")
        self.assertEqual(sc.classify(f(4, 8, 0), {"A": h(8), "B": h(7)}), "SCHEMA_AWARENESS")
        self.assertEqual(sc.classify(f(4, 8, 0), {"A": h(8), "B": h(6)}), "FORMAT_GROUNDING_TRADEOFF")
        self.assertEqual(sc.classify(f(4, 8, 0, 0, 1), {"A": h(8), "B": h(8)}), "INCONCLUSIVE")
        self.assertEqual(sc.classify(f(4, 5, 3), {"A": h(8), "B": h(8)}), "SCHEMA_CAPACITY_CONFIRMED")
        self.assertEqual(sc.classify(f(4, 6, 2), {"A": h(8), "B": h(8)}), "INCONCLUSIVE")


class RunAndDeckTests(unittest.TestCase):
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
        cls.questions = {"q101": question("q101"), "q102": question("q102", query="quiet luxury")}

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_batch(self, responses):
        d = tempfile.mkdtemp(dir=self.tmp)
        paths = {"RUN": d, "BATCH": os.path.join(d, "batch.json"), "OUTPUTS": os.path.join(d, "outputs.jsonl"),
                 "SUMMARY": os.path.join(d, "summary.json"), "PROTOCOL": os.path.join(d, "protocol.json")}
        with open(paths["BATCH"], "w", encoding="utf-8") as f:
            json.dump({"question_ids": ["q101", "q102"]}, f)
        with open(paths["PROTOCOL"], "w", encoding="utf-8") as f:
            f.write("{}")
        provider = ScriptedProvider(responses)
        with mock.patch.multiple(sc, **paths), mock.patch.object(sc, "check_frozen", lambda: None):
            body = sc.run(provider, self.corpus, self.index, self.questions)
            records = sc.v1_load(paths["OUTPUTS"])
        return body, records, provider

    def test_paired_run_keeps_first_attempts_and_identical_packets(self):
        a = self.ids[0]
        body, records, provider = self.run_batch([
            answer([a], n_claims=5), answer([a]),   # q101 A: 5 claims, then a valid retry
            answer([a]),                             # q101 B
            answer([a], claim_len=450), answer([a]),  # q102 A: long claim, then valid
            ABSTAIN])                                # q102 B
        self.assertEqual(len(provider.calls), 6)
        self.assertEqual([(r["question_id"], r["condition"]) for r in records],
                         [("q101", "A"), ("q101", "B"), ("q102", "A"), ("q102", "B")])
        for q in ("q101", "q102"):
            pa, pb = [r for r in records if r["question_id"] == q]
            self.assertEqual(pa["context_sha256"], pb["context_sha256"])
            self.assertEqual(provider.calls[0][1], provider.calls[2][1])  # same user message, A and B
        self.assertNotEqual(provider.calls[0][0]["content"], provider.calls[2][0]["content"])  # prompts differ
        first = records[0]["attempts"][0]
        self.assertFalse(first["schema_valid"])
        self.assertIn('"claims"', first["raw_output"])
        fmt = body["format"]
        self.assertEqual((fmt["A"]["first_attempt_valid"], fmt["A"]["retries"], fmt["A"]["final_schema_valid"]), (0, 2, 2))
        self.assertEqual(fmt["A"]["first_attempt_violations"]["claim_count"], 1)
        self.assertEqual(fmt["A"]["first_attempt_violations"]["claim_length"], 1)
        self.assertEqual((fmt["B"]["first_attempt_valid"], fmt["B"]["retries"]), (2, 0))

    def test_pair_with_different_evidence_is_refused(self):
        a = {"question_id": "q1", "retrieval": {"item_ids": [1, 2]}, "context_sha256": "x"}
        with self.assertRaises(RuntimeError):
            sc.check_pair(a, dict(a, context_sha256="y"))

    def test_blind_deck_hides_condition_and_shares_sufficiency(self):
        a = self.ids[0]
        _, records, _ = self.run_batch([answer([a], n_claims=2), answer([a]), answer([a]), ABSTAIN])
        tasks = sc.build_blind_tasks(records, self.questions, self.corpus)
        self.assertEqual(sum(t["kind"] == "context_sufficiency" for t in tasks), 2)
        for t in tasks:
            text = json.dumps(t)
            for leak in ("v2.1", "Prompt v2", "condition", "retry", "schema_valid", ":A:", ":B:"):
                self.assertNotIn(leak, text)
            self.assertTrue(t["body"].startswith(sc.adj.HEADER))
        blind = {t["task_id"].split(":")[1] for t in tasks if t["kind"] != "context_sufficiency"}
        self.assertEqual(blind, {sc.blind_id(q, c) for q in ("q101", "q102") for c in "AB"})
        again = sc.build_blind_tasks(records, self.questions, self.corpus)
        self.assertEqual([t["task_id"] for t in tasks], [t["task_id"] for t in again])
        kinds = {t["task_id"]: t["kind"] for t in tasks}
        self.assertEqual(kinds[f"q102:{sc.blind_id('q102', 'B')}:abstention"], "abstention")


if __name__ == "__main__":
    unittest.main()
