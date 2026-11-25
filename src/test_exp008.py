"""Tests for EXP-008 (src/exp008.py). Throwaway decks and files, no network, no editor logs.

usage: python src/test_exp008.py
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp008 as x  # noqa: E402
import test_exp007 as t7  # noqa: E402

VOCAB = (["ballet flat", "loafer", "wide-leg"], ["a.com", "vogue", "vogue.com"],
         {tuple("loafers return to the office".split())})


class LeakTests(unittest.TestCase):
    def test_clean_profile_passes(self):
        self.assertEqual(x.leak_problems("The editor keeps cards spread across many outlets. "
                                         "Seasonal labels follow the calendar.", VOCAB), [])

    def test_names_plurals_and_spacing_are_caught(self):
        p = x.leak_problems("Loafers and ballet-flats and wide leg cuts.", VOCAB)
        self.assertIn("signal name: loafer", p)
        self.assertIn("signal name: ballet flat", p)
        self.assertIn("signal name: wide-leg", p)

    def test_outlets_and_headline_words_are_caught(self):
        p = x.leak_problems("Coverage in Vogue: loafers return to the office again.", VOCAB)
        self.assertIn("outlet: vogue", p)
        self.assertIn("headline words: loafers return to the office", p)

    def test_word_inside_another_word_is_not_a_hit(self):
        self.assertEqual(x.leak_problems("The editor values vogueish confidence.", VOCAB), [])

    def test_length_cap(self):
        self.assertTrue(any(s.startswith("too long") for s in x.leak_problems("word " * 801, VOCAB)))
        self.assertIn("empty", x.leak_problems("  ", VOCAB))


def transcript(calls):
    lines = [json.dumps({"message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": n, "input": {"file_path": p}}]}}) for n, p in calls]
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    f.write("\n".join(lines))
    f.close()
    return f.name


class AuditTests(unittest.TestCase):
    held = "2026-11-22"

    def test_only_inputs_read_and_profile_written(self):
        reads = [("Read", p) for p in x.input_paths(self.held).values()]
        path = transcript(reads + [("Write", os.path.join(x.PROFILES, f"{self.held}.md"))])
        self.assertEqual(x.audit_transcript(path, self.held)[1], [])

    def test_reading_the_held_out_week_fails(self):
        reads = [("Read", p) for p in x.input_paths(self.held).values()]
        bad = os.path.join(x.INPUTS, "2026-11-15", f"week-{self.held}.md")
        path = transcript(reads + [("Read", bad), ("Write", os.path.join(x.PROFILES, f"{self.held}.md"))])
        self.assertTrue(any("not allowed" in p for p in x.audit_transcript(path, self.held)[1]))

    def test_other_tools_and_missing_reads_fail(self):
        path = transcript([("Grep", None), ("Write", os.path.join(x.PROFILES, f"{self.held}.md"))])
        problems = x.audit_transcript(path, self.held)[1]
        self.assertTrue(any("Grep" in p for p in problems))
        self.assertTrue(any("not read" in p for p in problems))

    def test_held_out_week_is_never_an_input(self):
        for w in x.WEEKS:
            self.assertNotIn(w, x.input_paths(w))
            self.assertEqual(len(x.input_paths(w)), 6)


class RenderTests(unittest.TestCase):
    def test_profile_is_the_only_change(self):
        q = t7.queue()
        for c in (q["cards"][0], q["cards"][2]):
            for order in ("original", "swapped"):
                s7, u7 = x.e7.render(q, c, t7.DEFS, order)
                s8, u8 = x.render(q, c, t7.DEFS, "PROFILE TEXT", order)
                self.assertEqual(s8, s7.replace(x.OPENING_FROM, x.OPENING_TO))
                self.assertEqual(u8.replace(f"\n\n{x.PROFILE_HEADING}\n\nPROFILE TEXT", ""), u7)
                self.assertEqual(u8.count("PROFILE TEXT"), 1)

    def test_decide_uses_the_profile_and_restores_render(self):
        from llm_provider import ScriptedProvider
        q = t7.queue()
        original = x.e7.render
        rec = x._decide(q, q["cards"][0], t7.DEFS, "PROFILE TEXT", "original", ScriptedProvider([t7.keep()]), None)
        self.assertIs(x.e7.render, original)
        self.assertEqual(rec["status"], "decided")
        s, u = x.render(q, q["cards"][0], t7.DEFS, "PROFILE TEXT")
        self.assertEqual(rec["prompt_sha256"], x.e7.sha_text(s + "\n\n" + u))


class PairedTests(unittest.TestCase):
    def setUp(self):
        week = x.WEEKS[-1]
        self.q = {"kind": "report_decisions", "report_date": week, "title": "t",
                  "cards": [t7.card(f"s{i}") for i in range(40)]}
        self.week = week
        self.patch = mock.patch.object(x.e7, "load_week", lambda w, *a: self.q if w == week else
                                       {"kind": "report_decisions", "report_date": w, "title": "t", "cards": []})
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def recs(self, decisions):
        return [{"week": self.week, "card_id": f"signal:s{i}", "order": "original", "status": "decided",
                 "payload": {"decision": d}} for i, d in enumerate(decisions)]

    def test_better_reader_is_supported_and_mcnemar_counts(self):
        editor_d = ["keep", "drop"] * 20
        editor = {self.week: {f"signal:s{i}": {"decision": d, "thoughts": ""} for i, d in enumerate(editor_d)}}
        p = x.paired(self.recs(["keep"] * 40), self.recs(editor_d), editor,
                     dict(x.BOOTSTRAP, resamples=500))
        self.assertEqual(p["n"], 40)
        self.assertEqual(p["kappa_exp008"], 1.0)
        self.assertEqual(p["H1_decision_kappa"], "supported")
        self.assertEqual(p["mcnemar"], {"exp007_right_exp008_wrong": 0, "exp007_wrong_exp008_right": 20,
                                        "p_exact": x.mcnemar_exact(0, 20)})
        self.assertEqual(p["ai_drops"], {"exp007": 0, "exp008": 20, "editor": 20})

    def test_bootstrap_is_seeded(self):
        editor_d = ["keep", "drop", "keep", "watchlist"] * 10
        editor = {self.week: {f"signal:s{i}": {"decision": d, "thoughts": ""} for i, d in enumerate(editor_d)}}
        ai = ["keep", "drop", "drop", "keep"] * 10
        b = dict(x.BOOTSTRAP, resamples=300)
        self.assertEqual(x.paired(self.recs(["keep"] * 40), self.recs(ai), editor, b),
                         x.paired(self.recs(["keep"] * 40), self.recs(ai), editor, b))

    def test_mcnemar(self):
        self.assertEqual(x.mcnemar_exact(0, 0), 1.0)
        self.assertAlmostEqual(x.mcnemar_exact(0, 6), 0.03125)


if __name__ == "__main__":
    unittest.main()
