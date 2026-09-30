"""Tests for the DeepSeek adapter (src/llm_deepseek.py) with a fake HTTP session.
No request leaves the machine, and the fake key is assembled at runtime.

usage: python src/test_llm_deepseek.py
"""

import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests  # noqa: E402

import llm_deepseek as ds  # noqa: E402
from llm_provider import LiveCallNotAllowed, ProviderError  # noqa: E402

FAKE_KEY = "sk-" + "test" + "0" * 28
MESSAGES = [{"role": "user", "content": "{}"}]


class FakeResponse:
    def __init__(self, status, body):
        self.status_code = status
        self.body = body

    def json(self):
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


class FakeSession:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.requests.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


OK = FakeResponse(200, {"id": "req-1", "model": "deepseek-flash",
                        "choices": [{"message": {"content": '{"insufficient_evidence": true, "claims": []}'},
                                     "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 1000, "completion_tokens": 200, "prompt_cache_hit_tokens": 400,
                                  "prompt_cache_miss_tokens": 600}})


class DeepSeekTests(unittest.TestCase):
    def setUp(self):
        self.saved = {k: os.environ.pop(k, None) for k in ("DEEPSEEK_API_KEY", ds.GATE_VARIABLE)}

    def tearDown(self):
        for k, v in self.saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    def live(self, session, **kw):
        os.environ[ds.GATE_VARIABLE] = "approved"
        os.environ["DEEPSEEK_API_KEY"] = FAKE_KEY
        return ds.DeepSeekProvider(allow_live=True, session=session, sleep=lambda s: None, **kw)

    def test_gate_blocks_before_any_network_activity(self):
        session = FakeSession(OK)
        for allow, gate in ((False, "approved"), (True, None), (True, "yes")):
            os.environ.pop(ds.GATE_VARIABLE, None)
            if gate:
                os.environ[ds.GATE_VARIABLE] = gate
            os.environ["DEEPSEEK_API_KEY"] = FAKE_KEY
            with self.assertRaises(LiveCallNotAllowed):
                ds.DeepSeekProvider(allow_live=allow, session=session).generate_json(MESSAGES)
        self.assertEqual(session.requests, [])

    def test_missing_key_fails_cleanly(self):
        os.environ[ds.GATE_VARIABLE] = "approved"
        with self.assertRaises(ProviderError) as ctx:
            ds.DeepSeekProvider(allow_live=True, session=FakeSession()).generate_json(MESSAGES)
        self.assertIn("DEEPSEEK_API_KEY is not set", str(ctx.exception))

    def test_request_shape_and_result(self):
        session = FakeSession(OK)
        out = self.live(session).generate_json(MESSAGES)
        sent = session.requests[0]
        self.assertEqual(sent["url"], "https://api.deepseek.com/chat/completions")
        self.assertEqual(sent["json"]["model"], "deepseek-flash")
        self.assertEqual(sent["json"]["temperature"], 0.0)
        self.assertEqual(sent["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(sent["json"]["thinking"], {"type": "disabled"})
        self.assertEqual(sent["timeout"], 60.0)
        self.assertEqual((out.request_id, out.finish_reason, out.attempts), ("req-1", "stop", 1))
        self.assertEqual(out.usage["prompt_cache_hit_tokens"], 400)

    def test_retries_transient_failures_only(self):
        session = FakeSession(requests.Timeout(), FakeResponse(429, {}), OK)
        self.assertEqual(self.live(session).generate_json(MESSAGES).attempts, 3)
        session = FakeSession(FakeResponse(400, {"error": {"message": "bad request"}}), OK)
        with self.assertRaises(ProviderError):
            self.live(session).generate_json(MESSAGES)
        self.assertEqual(len(session.requests), 1)
        session = FakeSession(FakeResponse(503, {}), FakeResponse(503, {}), FakeResponse(503, {}))
        with self.assertRaises(ProviderError) as ctx:
            self.live(session).generate_json(MESSAGES)
        self.assertIn("after 3 attempts", str(ctx.exception))

    def test_secrets_never_appear_in_errors_or_config(self):
        echo = FakeResponse(401, {"error": {"message": f"invalid key {FAKE_KEY} in Bearer {FAKE_KEY}"}})
        provider = self.live(FakeSession(echo))
        with self.assertRaises(ProviderError) as ctx:
            provider.generate_json(MESSAGES)
        self.assertNotIn(FAKE_KEY, str(ctx.exception))
        self.assertIn("[redacted]", str(ctx.exception))
        self.assertNotIn(FAKE_KEY, repr(provider.config()) + repr(vars(provider)))

    def test_malformed_success_is_an_error(self):
        with self.assertRaises(ProviderError):
            self.live(FakeSession(FakeResponse(200, {"choices": []}))).generate_json(MESSAGES)

    def test_cost_depends_on_peak_hours(self):
        usage = OK.body["usage"]
        peak = datetime(2026, 9, 30, 2, 0, tzinfo=timezone.utc)  # Wednesday 02:00 UTC
        off = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)
        self.assertAlmostEqual(ds.estimate_cost("deepseek-flash", usage, off),
                               (400 * 0.003 + 600 * 0.15 + 200 * 0.60) / 1e6)
        self.assertAlmostEqual(ds.estimate_cost("deepseek-flash", usage, peak),
                               2 * ds.estimate_cost("deepseek-flash", usage, off))
        self.assertIsNone(ds.estimate_cost("unknown-model", usage))


if __name__ == "__main__":
    unittest.main()
