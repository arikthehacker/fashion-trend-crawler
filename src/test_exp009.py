"""Tests for EXP-009 (src/exp009.py). Throwaway decks, no network, no editor logs.

usage: python src/test_exp009.py
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp009 as x  # noqa: E402
import test_exp007 as t7  # noqa: E402

W = x.WEEKS


def deck(week, terms):
    return {"kind": "report_decisions", "report_date": week, "title": f"Report decisions {week}",
            "cards": [t7.card(t) for t in terms]}


DECKS = {W[0]: deck(W[0], ["loafer", "denim"]), W[1]: deck(W[1], ["loafer", "corset"]),
         W[2]: deck(W[2], ["loafer", "denim", "corset"])}


def fake_load(week, *a):
    return DECKS.get(week) or deck(week, [])


def pay(decision, volatility="", confidence=""):
    return {"decision": decision, "volatility": volatility, "confidence": confidence, "thoughts": "t"}


EDITOR = {W[0]: {"signal:loafer": pay("keep", "seasonal"), "signal:denim": pay("drop")},
          W[1]: {"signal:loafer": pay("drop"), "signal:corset": pay("keep", "emerging", "high")},
          W[2]: {"signal:loafer": pay("keep", "seasonal"), "signal:denim": pay("keep", "stable"),
                 "signal:corset": pay("watchlist")}}


class WithDecks(unittest.TestCase):
    def setUp(self):
        x.signal_cards.cache_clear()
        self.patch = mock.patch.object(x.e7, "load_week", fake_load)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        x.signal_cards.cache_clear()


class HistoryTests(WithDecks):
    def test_history_uses_only_earlier_weeks(self):
        self.assertEqual([w for w, _ in x.history("loafer", W[2], EDITOR)], [W[0], W[1]])
        self.assertEqual(x.history("loafer", W[0], EDITOR), [])

    def test_same_as_last_time_and_its_fallback(self):
        self.assertEqual(x.same_as_last_time("loafer", W[2], EDITOR), "drop")
        self.assertEqual(x.same_as_last_time("denim", W[2], EDITOR), "drop")  # most recent earlier card: week 1
        self.assertEqual(x.same_as_last_time("corset", W[1], EDITOR), "keep")  # new term: fallback

    def test_memory_has_decisions_and_labels_only(self):
        m = x.memory_lines("corset", W[2], EDITOR)
        self.assertEqual(m, f"- week ending {W[1]}: keep, volatility emerging, confidence high")
        self.assertNotIn("t", m.replace("week", "").replace("emerging", "").replace("confidence", "")
                         .replace("ending", "").replace("high", "").replace("keep", "").replace("volatility", ""))
        self.assertEqual(x.memory_lines("corset", W[1], EDITOR), x.NO_MEMORY)

    def test_features_see_no_target_week_decision(self):
        card = x.signal_cards(W[2])[0]
        changed = dict(EDITOR, **{W[2]: {"signal:loafer": pay("drop")}})
        self.assertEqual(x.features(card, W[2], EDITOR), x.features(card, W[2], changed))


class ModelTests(unittest.TestCase):
    def test_fit_learns_a_separable_rule_and_is_deterministic(self):
        X = [[float(i), 1.0] for i in range(20)]
        y = [1.0 if i >= 10 else 0.0 for i in range(20)]
        a, b = x.fit(X, y), x.fit(X, y)
        self.assertEqual(a, b)
        self.assertGreater(x.predict_proba(a, [18.0, 1.0]), 0.5)
        self.assertLess(x.predict_proba(a, [1.0, 1.0]), 0.5)

    def test_constant_feature_gets_no_weight(self):
        params = x.fit([[1.0, 5.0], [2.0, 5.0], [3.0, 5.0]], [0.0, 1.0, 1.0])
        self.assertEqual(params[2][1], 0.0)


class RenderTests(unittest.TestCase):
    def test_memory_is_the_only_change(self):
        q = t7.queue()
        s7, u7 = x.e7.render(q, q["cards"][0], t7.DEFS)
        s9, u9 = x.render(q, q["cards"][0], t7.DEFS, "MEMORY")
        self.assertEqual(s9, s7.replace(x.OPENING_FROM, x.OPENING_TO))
        self.assertEqual(u9.replace(f"\n\n{x.MEMORY_HEADING}\n\nMEMORY", ""), u7)

    def test_decide_restores_render(self):
        from llm_provider import ScriptedProvider
        q = t7.queue()
        rec = x._decide(q, q["cards"][0], t7.DEFS, "MEMORY", ScriptedProvider([t7.keep()]), None)
        self.assertIs(x.e7.render, x._E7_RENDER)
        self.assertEqual(rec["status"], "decided")


class ScoreTests(unittest.TestCase):
    def test_delta_ci_and_score(self):
        rows = []
        for i in range(40):
            ed = "keep" if i % 2 else "drop"
            rows.append({"week": x.TARGET_WEEKS[0], "editor": {"decision": ed}, "seen_before": bool(i % 3),
                         "four": {m: "keep" for m in x.METHODS},
                         "keep": {**{m: True for m in x.METHODS}, "M2_taste_model": ed == "keep"}})
        r = x.delta_ci(rows, "M2_taste_model", "M3_deepseek", dict(x.BOOTSTRAP, resamples=200))
        self.assertEqual(r["kappa_a"], 1.0)
        self.assertEqual(r["kappa_b"], 0.0)  # an always-keep reader scores kappa 0
        self.assertEqual(r["verdict"], "supported")
        s = x.score(rows)
        self.assertEqual(s["M2_taste_model"]["keep_vs_not"]["agreement"], 1.0)
        self.assertNotIn("four_way", s["M2_taste_model"])


if __name__ == "__main__":
    unittest.main()
