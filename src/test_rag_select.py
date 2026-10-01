"""Tests for the EXP-004 retriever-selection rule (src/rag_select.py). Synthetic numbers only.

usage: python src/test_rag_select.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rag_select as rs  # noqa: E402

RULE = {"clear_winner": {"bootstrap_resamples": 2000, "seed": 7},
        "practical_tie": {"recall_margin": 0.03, "hit_margin": 0.03},
        "subgroup_safeguard": {"min_answerable_questions": 3}}


def summary(recall, hit, p95, median=10.0, latency_ok=True, integrity_ok=True):
    return {"all": {"recall@10": recall, "hit@10": hit}, "latency_ms": {"p95": p95, "median": median},
            "eligible": {"latency_ok": latency_ok, "integrity_ok": integrity_ok}}


def hits(**values):
    return {"all": {"n_answerable": 10, "hit@10": values}}


class MetricTests(unittest.TestCase):
    def test_fixed_ranks_with_unsure(self):
        # rank 1 relevant, rank 2 unsure, rank 3 relevant: ranks stay 1, 2, 3
        m = rs.question_metrics([11, 12, 13, 14], {11: "relevant", 12: "unsure", 13: "relevant", 99: "relevant"})
        self.assertEqual(m["n_relevant"], 3)
        self.assertEqual((m["hit@5"], m["mrr"]), (1.0, 1.0))
        self.assertAlmostEqual(m["recall@5"], 2 / 3)
        self.assertAlmostEqual(m["unsure@5"], 1 / 4)  # one of the four retrieved items
        m = rs.question_metrics([12, 13], {12: "unsure", 13: "relevant"})
        self.assertEqual(m["mrr"], 0.5)  # the unsure item still occupies rank 1

    def test_questions_without_relevant_are_excluded_from_recall(self):
        m = rs.question_metrics([1, 2], {1: "not_relevant", 2: "unsure"})
        self.assertNotIn("recall@10", m)
        self.assertEqual(m["unsure@10"], 0.5)
        agg = rs.aggregate([m, rs.question_metrics([3], {3: "relevant"})])
        self.assertEqual((agg["recall@10"], agg["n_recall@10"], agg["questions_without_relevant"]), (1.0, 1, 1))
        self.assertEqual(agg["n_unsure@10"], 2)

    def test_bootstrap_is_paired_and_deterministic(self):
        a, b = [1, 1, 0.5, 1, 0.8], [0.5, 0.6, 0.5, 0.2, 0.4]
        first, second = rs.paired_bootstrap(a, b, 2000, 7), rs.paired_bootstrap(a, b, 2000, 7)
        self.assertEqual(first, second)
        self.assertGreater(first["ci95"][0], 0)
        reverse = rs.paired_bootstrap(b, a, 2000, 7)
        self.assertAlmostEqual(reverse["mean_difference"], -first["mean_difference"])


class UnsureBreakdownTests(unittest.TestCase):
    def test_breakdown_by_question_and_item_language(self):
        class Q:
            def __init__(self, qid, lang):
                self.question_id, self.language = qid, lang
        judged = {"q001": {1: "unsure", 2: "relevant", 3: "unsure"}, "q002": {4: "not_relevant", 3: "unsure"}}
        langs = {1: "ja", 2: "en", 3: None, 4: "ja"}
        out = rs.unsure_breakdown([Q("q001", "en"), Q("q002", "ja")], judged, langs)
        self.assertEqual(out["question_language"]["en"], {"judgments": 3, "unsure": 2, "unsure_rate": 0.6667})
        self.assertEqual(out["item_language"]["unknown"]["judgments"], 2)
        self.assertEqual(out["item_english_vs_non_english"]["non-en"], {"judgments": 2, "unsure": 1, "unsure_rate": 0.5})
        match = out["question_item_language_match"]
        self.assertEqual((match["match"]["judgments"], match["mismatch"]["judgments"], match["unknown"]["judgments"]),
                         (2, 1, 2))


class RuleTests(unittest.TestCase):
    def test_clear_winner(self):
        s = {"bm25": summary(0.4, 0.6, 50), "dense": summary(0.5, 0.7, 40), "hybrid": summary(0.9, 1.0, 60)}
        r = {"bm25": [0.4] * 10, "dense": [0.5] * 10, "hybrid": [0.9] * 10}
        out = rs.apply_rule(s, r, RULE, hits(bm25=0.6, dense=0.7, hybrid=1.0))
        self.assertEqual((out["outcome"], out["selected"]), ("CLEAR_SELECTION", "hybrid"))

    def test_practical_tie_uses_hit_then_latency(self):
        noisy = [0.0, 1.0] * 5
        s = {"bm25": summary(0.50, 0.70, 30), "dense": summary(0.52, 0.80, 45), "hybrid": summary(0.51, 0.79, 40)}
        r = {"bm25": noisy, "dense": noisy[::-1], "hybrid": noisy}
        out = rs.apply_rule(s, r, RULE, hits(bm25=0.7, dense=0.8, hybrid=0.79))
        self.assertEqual(out["outcome"], "PRACTICAL_TIE_SELECTION")
        self.assertEqual(out["selected"], "hybrid")  # dense and hybrid tie on Hit@10 within 0.03; hybrid is faster

    def test_ineligible_candidates_are_not_selected(self):
        s = {"bm25": summary(0.4, 0.6, 50), "hybrid": summary(0.9, 1.0, 900, latency_ok=False)}
        out = rs.apply_rule(s, {"bm25": [0.4] * 10, "hybrid": [0.9] * 10}, RULE, hits(bm25=0.6, hybrid=1.0))
        self.assertEqual(out["selected"], "bm25")
        none = rs.apply_rule({"bm25": summary(0.4, 0.6, 50, integrity_ok=False)}, {"bm25": [0.4]}, RULE, {})
        self.assertEqual(none["outcome"], "HARD_STOP_OTHER")

    def test_subgroup_safeguard_stops_the_freeze(self):
        s = {"bm25": summary(0.4, 0.6, 50), "dense": summary(0.5, 0.7, 40), "hybrid": summary(0.9, 1.0, 60)}
        r = {"bm25": [0.4] * 10, "dense": [0.5] * 10, "hybrid": [0.9] * 10}
        groups = {"japanese": {"n_answerable": 3, "hit@10": {"bm25": 0.67, "dense": 0.33, "hybrid": 0.0}},
                  "tiny": {"n_answerable": 2, "hit@10": {"bm25": 1.0, "dense": 1.0, "hybrid": 0.0}}}
        out = rs.apply_rule(s, r, RULE, groups)
        self.assertEqual((out["outcome"], out["candidate"], out["subgroups"]), ("HARD_STOP_SUBGROUP", "hybrid",
                                                                                 ["japanese"]))


if __name__ == "__main__":
    unittest.main()
