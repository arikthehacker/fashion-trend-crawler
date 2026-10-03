"""Tests for the C1 holdout question records (src/exp005_holdout.py). No store, no network.

usage: python src/test_exp005_holdout.py
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_holdout as h  # noqa: E402
from rag_schema import Filters  # noqa: E402

BASE = {"question_id": "h001", "question": "What are outlets saying about cargo pants?",
        "retrieval_query": "What are outlets saying about cargo pants?", "filters": Filters(),
        "categories": ["direct"], "primary_category": "direct", "probes": "A single garment named in plain words."}


class HoldoutRecordTests(unittest.TestCase):
    def test_valid_record(self):
        h.HoldoutQuestion(**BASE)

    def test_retrieval_query_must_equal_the_question_byte_for_byte(self):
        for q in ("cargo pants", "What are outlets saying about cargo pants? ", "what are outlets saying about cargo pants?"):
            with self.assertRaises(ValueError):
                h.HoldoutQuestion(**dict(BASE, retrieval_query=q))

    def test_no_answer_citations_or_answerability_fields(self):
        for extra in ({"expected_answer": "x"}, {"expected_citations": [1]}, {"answerable_expected": True}):
            with self.assertRaises(ValueError):
                h.HoldoutQuestion(**BASE, **extra)

    def test_primary_category_must_be_listed(self):
        with self.assertRaises(ValueError):
            h.HoldoutQuestion(**dict(BASE, primary_category="stress"))

    def test_deck_checks_count_ids_and_mix(self):
        deck = [h.HoldoutQuestion(**dict(BASE, question_id=f"h{n:03d}", question=f"Question {n} about cargo pants?",
                                         retrieval_query=f"Question {n} about cargo pants?")) for n in range(1, 31)]
        errors = h.deck_errors(deck)
        self.assertTrue(any("synthesis" in e for e in errors))
        self.assertFalse(any("questions, not" in e for e in errors))
        self.assertTrue(h.deck_errors(deck[:29]))

    def test_frozen_deck_passes_its_own_checks(self):
        deck = h.load_deck()
        self.assertEqual(h.deck_errors(deck), [])
        self.assertTrue(all(q.retrieval_query == q.question for q in deck))

    def test_app_question_refuses_a_rewritten_query(self):
        q = h.HoldoutQuestion(**BASE).model_copy(update={"retrieval_query": "cargo pants"})
        with self.assertRaises(ValueError):
            h.app_question(q)

    def test_deck_cards_are_blind_and_in_a_fixed_order(self):
        deck = h.load_deck()
        packets = []
        for q in deck:
            context = [{"item_id": 1, "outlet": "example.com", "sector_group": "editorial", "published_at": "2026-09-01",
                        "language": "en", "headline": "Headline", "excerpt": "Excerpt", "url": "https://example.com/a"}]
            payload = {"question": q.question, "constraints": {"description": "no constraints", "filters": {}},
                       "evidence": context}
            packets.append({"question_id": q.question_id, "question": q.question, "status": "packet_built",
                            "context": context, "messages": [{"role": "system", "content": "p"},
                                                             {"role": "user", "content": json.dumps(payload)}]})
        tasks = h.deck_tasks(packets)
        self.assertEqual(len(tasks), 30)
        self.assertEqual([t["task_id"] for t in tasks], [t["task_id"] for t in h.deck_tasks(packets)])
        self.assertNotEqual([t["question_id"] for t in tasks], [q.question_id for q in deck])
        probes = {q.question_id: q.probes for q in deck}
        for t in tasks:
            self.assertNotIn(probes[t["question_id"]], t["body"])
            self.assertNotIn("stress", t["body"])
            self.assertEqual([o["value"] for o in t["options"]], ["SUFFICIENT", "INSUFFICIENT", "UNSURE"])

    def test_empty_packet_card_says_the_model_would_not_be_called(self):
        text = h.packet_text({"status": "system_abstention", "context": [], "messages": None})
        self.assertIn("EMPTY PACKET", text)

    def test_duplicate_screen_flags_exact_repeats(self):
        prior = {"What are outlets saying about cargo pants?": {"id": "q999", "filters": {}}}
        row = h.duplicate_report([h.HoldoutQuestion(**BASE)], prior)[0]
        self.assertTrue(row["exact_duplicate"] and row["flag_for_owner"])


if __name__ == "__main__":
    unittest.main()
