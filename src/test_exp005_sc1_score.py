"""Tests for the SC-1 review freeze and scoring (src/exp005_sc1_score.py). Synthetic rows, no
network, no provider.

usage: python src/test_exp005_sc1_score.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_review_v2 as rv2  # noqa: E402
import exp005_sc1_score as s  # noqa: E402
import exp005_schema as sc  # noqa: E402

OPTS = {"options": [{"value": v} for v in ("SUPPORTED", "UNSUPPORTED", "UNSURE", "YES", "NO", "COMPLETE",
                                           "PARTIAL", "CORRECT", "INCORRECT")]}


def row(task_id, value, at="2026-10-03T00:00:00Z", kind="x"):
    return {"task_id": task_id, "question_id": task_id.split(":")[0], "kind": kind, "value": value,
            "reviewed_at": at, "reviewer": "ariella"}


class FreezeTests(unittest.TestCase):
    def test_final_judgments(self):
        expected = {"q1:sufficiency": OPTS, "q1:ans-a:claim 0": OPTS}
        rows = [row("q1:sufficiency", "YES"), row("q1:ans-a:claim 0", "UNSURE"),
                row("q1:ans-a:claim 0", "SUPPORTED", "2026-10-03T00:01:00Z"), row("q1:ans-a:claim 0", "a note", kind="note")]
        final, notes, repeated = s.final_judgments(rows, expected)
        self.assertEqual({r["task_id"]: r["value"] for r in final}, {"q1:sufficiency": "YES", "q1:ans-a:claim 0": "SUPPORTED"})
        self.assertEqual((len(notes), repeated), (1, 1))

    def test_incomplete_or_conflicting_review_is_refused(self):
        expected = {"q1:sufficiency": OPTS, "q1:ans-a:claim 0": OPTS}
        with self.assertRaises(RuntimeError):
            s.final_judgments([row("q1:sufficiency", "YES")], expected)
        with self.assertRaises(RuntimeError):
            s.final_judgments([row("q1:sufficiency", "YES"), row("q1:ans-a:claim 0", "SUPPORTED"),
                               row("q1:ans-a:claim 0", "UNSUPPORTED")], expected)
        with self.assertRaises(RuntimeError):
            s.final_judgments([row("q1:sufficiency", "YES"), row("q1:ans-a:claim 0", "SUPPORTED"),
                               row("q9:ans-z:claim 0", "SUPPORTED")], expected)


class UnblindAndScoreTests(unittest.TestCase):
    def setUp(self):
        self.key = {sc.blind_id("q1", "A"): {"question_id": "q1", "condition": "A"},
                    sc.blind_id("q1", "B"): {"question_id": "q1", "condition": "B"},
                    sc.blind_id("q2", "A"): {"question_id": "q2", "condition": "A"},
                    sc.blind_id("q2", "B"): {"question_id": "q2", "condition": "B"}}
        a1, b1, a2, b2 = (sc.blind_id(q, c) for q, c in (("q1", "A"), ("q1", "B"), ("q2", "A"), ("q2", "B")))
        self.final = [row("q1:sufficiency", "YES"), row(f"q1:{a1}:claim 0", "SUPPORTED"),
                      row(f"q1:{b1}:claim 0", "UNSUPPORTED"), row(f"q1:{a1}:completeness", "COMPLETE"),
                      row(f"q1:{b1}:completeness", "PARTIAL"), row("q2:sufficiency", "NO"),
                      row(f"q2:{a2}:abstention", "CORRECT"), row(f"q2:{b2}:abstention", "CORRECT")]
        self.records = [{"question_id": q, "status": st, "role": "fresh", "condition": c, "attempts": [], "answer": {"claims": []}}
                        for q, st in (("q1", "answered"), ("q2", "model_abstention")) for c in "AB"]

    def test_unblind_maps_conditions_and_shares_sufficiency(self):
        rows = s.unblind(self.final, self.key)
        self.assertEqual(sum(r["task_id"] == "q1:sufficiency" for r in rows), 2)
        self.assertEqual({r["condition"] for r in rows if r["task_id"] == "q1:claim 0"}, {"A", "B"})
        self.assertTrue(all(r["blind_task_id"] for r in rows))
        with self.assertRaises(RuntimeError):
            s.unblind([row("q1:ans-ffffff:claim 0", "SUPPORTED")], self.key)

    def test_metrics_per_condition_use_the_frozen_formula(self):
        rows = s.unblind(self.final, self.key)
        m = {c: rv2.metrics_v2([r for r in self.records if r["condition"] == c], [x for x in rows if x["condition"] == c])
             for c in "AB"}
        self.assertEqual((m["A"]["supported"], m["A"]["unsupported"], m["A"]["grounded"]), (1, 0, 2))
        self.assertEqual((m["B"]["supported"], m["B"]["unsupported"], m["B"]["grounded"]), (0, 1, 1))
        pq = s.per_question(self.records, rows)
        self.assertEqual((pq["q1"]["A"]["completeness"], pq["q1"]["B"]["completeness"]), ("COMPLETE", "PARTIAL"))

    def test_frozen_rule_cannot_select_b_without_a_format_gain(self):
        fmt = {"A": {"first_attempt_valid": 8, "first_attempts_with_cap_violation": 0, "integrity_failures": 0},
               "B": {"first_attempt_valid": 8, "first_attempts_with_cap_violation": 0, "integrity_failures": 0}}
        h = {"grounded": 8, "unsupported": 0, "abstention": {"incorrect": 0, "missed": 0},
             "completeness": {"PARTIAL": 0, "INSUFFICIENT": 0}}
        worse = dict(h, grounded=5, unsupported=4)
        self.assertEqual(sc.classify(fmt, {"A": h, "B": h}), "INCONCLUSIVE")
        self.assertEqual(sc.classify(fmt, {"A": h, "B": worse}), "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
