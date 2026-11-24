"""Tests for EXP-007 (src/exp007.py). Scripted provider, throwaway decks and files, no network.

usage: python src/test_exp007.py
"""

import builtins
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp007 as x  # noqa: E402
from llm_provider import ScriptedProvider  # noqa: E402

DEFS = "# Report decision definitions\n\n## Decision\n- keep: in the report\n"


def card(sid, name=None):
    return {"card_id": f"signal:{sid}", "kind": "signal", "signal_id": sid, "name": name or sid,
            "type": "footwear", "baseline_confidence": "medium", "items": 3, "outlets": 2,
            "sectors": {"editorial": 3}, "dates": ["2026-11-01", "2026-11-02"], "weaknesses": [],
            "evidence": [{"item_id": 11, "published": "2026-11-01", "outlet": "a.com", "sector": "editorial",
                          "title": "Loafers return", "url": "https://a.com/1"}]}


def queue(week="2026-11-08"):
    dup = {"card_id": "duplicate:1", "kind": "duplicate", "why": "same brand",
           "items": [{"item_id": 11, "outlet": "a.com", "published": "2026-11-01", "signals": ["loafer"], "title": "t"}]}
    return {"kind": "report_decisions", "report_date": week, "title": f"Report decisions 2026-11-02 to {week}",
            "cards": [card("loafer"), card("ballet-flat", "ballet flat"), dup, {"card_id": "report", "kind": "report"}]}


def keep(**kw):
    return json.dumps({"decision": "keep", "merge_into": None, "type": None, "confidence": "baseline (medium)",
                       "volatility": "seasonal", "origin": None, "name": None, "remove_item_ids": [],
                       "thoughts": "fall shoe", **kw})


DUP = json.dumps({"collapse": True, "thoughts": "same story"})


class RenderTests(unittest.TestCase):
    def test_prompt_is_the_card_plus_the_definitions(self):
        q = queue()
        system, user = x.render(q, q["cards"][0], DEFS)
        self.assertEqual(system, x.OPENING_SIGNAL)
        self.assertIn(x.rr.card_text(q["cards"][0]), user)
        self.assertTrue(user.startswith(q["title"] + "\n\nloafer\n\n"))
        self.assertIn("DEFINITIONS (your words)\n\n" + DEFS, user)
        self.assertIn("Decision: keep / drop / merge / watchlist", user)
        self.assertIn("Merge into (only for merge): ballet flat", user)
        self.assertNotIn("https://", user)  # the app shows no URLs on the card

    def test_swap_reverses_every_option_list_but_not_the_definitions(self):
        q = queue()
        _, user = x.render(q, q["cards"][0], DEFS, "swapped")
        self.assertIn("Decision: watchlist / merge / drop / keep", user)
        self.assertIn("Confidence: high / medium / low / baseline (medium)", user)
        self.assertIn("DEFINITIONS (your words)\n\n" + DEFS, user)
        _, dup = x.render(q, q["cards"][2], DEFS, "swapped")
        self.assertIn("Decision: separate pieces: count each / one story: count once", dup)


class PayloadTests(unittest.TestCase):
    def test_the_apps_save_rules_apply(self):
        q = queue()
        c = q["cards"][0]
        p = x.to_payload(q, c, json.loads(keep()))
        self.assertEqual((p["decision"], p["confidence"], p["volatility"]), ("keep", "", "seasonal"))
        for bad in (keep(volatility=None), keep(thoughts=""), keep(decision="maybe"),
                    keep(decision="merge", merge_into="nonexistent")):
            with self.assertRaises(ValueError):
                x.to_payload(q, c, json.loads(bad))
        m = x.to_payload(q, c, json.loads(keep(decision="merge", merge_into="ballet flat")))
        self.assertEqual(m["merge_into"], "ballet-flat")
        self.assertTrue(x.to_payload(q, q["cards"][2], json.loads(DUP))["collapse"])

    def test_one_retry_then_invalid(self):
        q = queue()
        p = ScriptedProvider(["not json", keep()])
        r = x.decide(q, q["cards"][0], DEFS, "original", p)
        self.assertEqual((r["status"], len(r["attempts"])), ("decided", 2))
        self.assertIn("could not save", p.calls[1][-1]["content"])
        r = x.decide(q, q["cards"][0], DEFS, "original", ScriptedProvider([keep(volatility=None)] * 2))
        self.assertEqual((r["status"], len(r["attempts"])), ("invalid", 2))


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out, self.man = os.path.join(self.tmp, "blind", "ai.jsonl"), os.path.join(self.tmp, "sealed.json")
        self.patches = [mock.patch.object(x, "WEEKS", ("2026-11-08",)),
                        mock.patch.object(x, "load_week", lambda w, queues=None: queue(w)),
                        mock.patch.object(x, "definitions_text", lambda: DEFS)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp)

    def test_run_seals_without_touching_the_editors_logs(self):
        real_open = builtins.open

        def guarded(path, *a, **k):
            if "reports-editing" in str(path):
                raise AssertionError(f"the run opened {path}")
            return real_open(path, *a, **k)
        provider = ScriptedProvider([keep(), keep(), keep(decision="drop"), keep(decision="drop"), DUP, DUP])
        with mock.patch("builtins.open", guarded):
            body = x.run("thinking_off", provider, self.out, self.man)
        self.assertEqual((body["records"], body["calls"], body["first_attempt_valid"]), (6, 6, 6))
        sealed = json.dumps(body)
        for word in ("keep", "drop", "payload", "seasonal", "fall shoe"):
            self.assertNotIn(word, sealed)  # the manifest reveals no decision
        with self.assertRaises(RuntimeError):
            x.run("thinking_off", ScriptedProvider([]), self.out, self.man)  # runs once

    def test_thinking_on_runs_app_order_only_and_keeps_reasoning(self):
        class Thinking(ScriptedProvider):
            def generate_json(self, messages):
                r = super().generate_json(messages)
                r.reasoning_content = "weighing the evidence"
                r.usage["reasoning_tokens"] = 7
                return r
        body = x.run("thinking_on", Thinking([keep(), keep(decision="drop"), DUP]), self.out, self.man)
        self.assertEqual((body["records"], body["tokens"]["reasoning"]), (3, 21))
        records = x.load_records(self.out)
        self.assertEqual({r["order"] for r in records}, {"original"})
        self.assertEqual(records[0]["attempts"][0]["reasoning_content"], "weighing the evidence")
        self.assertNotIn("weighing", json.dumps(body))

    def test_auth_failure_stops_the_run(self):
        from llm_provider import ProviderError
        with self.assertRaises(RuntimeError):
            x.run("thinking_off", ScriptedProvider([ProviderError("DeepSeek HTTP 401: invalid key")]), self.out, self.man)


class CompareTests(unittest.TestCase):
    def test_kappa(self):
        self.assertEqual(x.kappa([("a", "a"), ("b", "b")]), 1.0)
        self.assertEqual(x.kappa([("a", "b"), ("b", "a")]), -1.0)
        self.assertEqual(x.kappa([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]), 0.0)

    def test_metrics(self):
        w = "2026-10-11"
        q = queue(w)
        q["cards"].insert(0, card("sneaker"))  # decided before the plan: reported separately
        rec = lambda cid, order, payload: {"week": w, "card_id": cid, "order": order, "status": "decided",
                                           "payload": payload, "attempts": [{}]}
        k = {"decision": "keep", "volatility": "seasonal", "merge_into": None}
        ai = [rec("signal:sneaker", "original", k), rec("signal:sneaker", "swapped", k),
              rec("signal:loafer", "original", k), rec("signal:loafer", "swapped", dict(k, decision="drop")),
              rec("signal:ballet-flat", "original", dict(k, decision="drop")),
              rec("signal:ballet-flat", "swapped", dict(k, decision="drop")),
              rec("duplicate:1", "original", {"collapse": True}), rec("duplicate:1", "swapped", {"collapse": True})]
        editor = {w: {"signal:sneaker": {"decision": "drop"},
                      "signal:loafer": {"decision": "keep", "volatility": "recurring", "thoughts": ""},
                      "signal:ballet-flat": {"decision": "drop", "thoughts": "[Looked up] the brand"},
                      "duplicate:1": {"collapse": True}}}
        with mock.patch.object(x, "WEEKS", (w,)), mock.patch.object(x, "load_week", lambda wk, queues=None: q):
            m = x.compare(ai, editor)
        self.assertEqual(m["decision"]["n"], 1)  # loafer only
        self.assertEqual(m["volatility_on_both_kept"]["agreement"], 0.0)
        self.assertEqual({r["why"] for r in m["reported_separately"]}, {"decided before the plan", "looked up"})
        self.assertEqual(m["duplicates"]["agreement"], 1.0)
        self.assertEqual(m["position_bias"]["changed_under_swap"], 1)

    def test_thinking_off_against_thinking_on_uses_app_order(self):
        w = "2026-11-08"
        q = queue(w)
        rec = lambda cid, order, payload: {"week": w, "card_id": cid, "order": order, "status": "decided",
                                           "payload": payload, "attempts": [{}]}
        k = {"decision": "keep", "volatility": "seasonal"}
        off = [rec("signal:loafer", "original", k), rec("signal:loafer", "swapped", dict(k, decision="drop")),
               rec("signal:ballet-flat", "original", dict(k, decision="drop")), rec("duplicate:1", "original", {"collapse": True})]
        on = [rec("signal:loafer", "original", k), rec("signal:ballet-flat", "original", k),
              rec("duplicate:1", "original", {"collapse": False})]
        with mock.patch.object(x, "WEEKS", (w,)), mock.patch.object(x, "load_week", lambda wk, queues=None: q):
            m = x.compare_ai(off, on)
        self.assertEqual((m["decision"]["n"], m["decision"]["agreement"], m["changed_by_thinking"]), (2, 0.5, 1))
        self.assertEqual(m["duplicates"]["agreement"], 0.0)
        self.assertEqual(m["per_week"][w]["kept_jaccard"], 0.5)


class ThinkingAdapterTests(unittest.TestCase):
    def test_reasoning_text_and_tokens_are_kept(self):
        import llm_deepseek_thinking as t

        class Resp:
            status_code = 200

            def json(self):
                return {"model": "deepseek-flash", "id": "r1",
                        "choices": [{"finish_reason": "stop",
                                     "message": {"content": "{}", "reasoning_content": "think sk-SECRET"}}],
                        "usage": {"prompt_tokens": 5, "completion_tokens": 9,
                                  "completion_tokens_details": {"reasoning_tokens": 6}}}
        p = t.DeepSeekThinkingProvider(model="deepseek-flash", allow_live=False)
        self.assertEqual(p._payload([])["thinking"], {"type": "enabled"})
        r = p._result(Resp(), 1, 0.1, "sk-SECRET")
        self.assertEqual((r.reasoning_content, r.usage["reasoning_tokens"]), ("think [redacted]", 6))


if __name__ == "__main__":
    unittest.main()
