"""Tests for the EXP-006 statistics and comparison (src/exp006_vllm.py). Synthetic outputs in a temp
folder, no server, no store. The C2 side of a comparison reads the committed C2 outputs file.

usage: python src/test_exp006_vllm.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005_holdout as h  # noqa: E402
import exp006_vllm as e  # noqa: E402


def attempt(ms, valid, tokens=100):
    return {"attempt": 1, "latency_ms": ms, "schema_valid": valid, "usage": {"completion_tokens": tokens}}


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rows, name="outputs.jsonl"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return path

    def test_figures_from_a_mixed_run(self):
        rows = [{"status": "answered", "attempts": [attempt(1000, True)]},
                {"status": "answered", "attempts": [attempt(2000, False), attempt(3000, True)]},
                {"status": "rejected_schema", "attempts": [attempt(4000, False), attempt(4000, False)]},
                {"status": "provider_error", "attempts": []}]
        s = e.stats(self.write(rows))
        self.assertEqual((s["questions"], s["called"]), (4, 3))
        self.assertEqual(s["first_attempt_latency_ms"], {"median": 2000, "p95": 4000})
        self.assertEqual(s["per_question_latency_ms_with_retries"]["median"], 5000)
        self.assertEqual((s["first_attempt_schema_valid"], s["final_schema_valid"], s["schema_retries"]), ("1/3", "2/3", 2))
        self.assertEqual(s["output_tokens_per_s_median"], 50.0)
        self.assertEqual(s["integrity_failures"], 2)

    def test_a_run_where_no_call_returned_does_not_crash(self):
        s = e.stats(self.write([{"status": "provider_error", "attempts": []}] * 3))
        self.assertEqual((s["questions"], s["called"], s["integrity_failures"]), (3, 0, 3))
        self.assertEqual(s["first_attempt_latency_ms"], {"median": None, "p95": None})
        self.assertIsNone(s["output_tokens_per_s_median"])
        self.assertEqual(s["first_attempt_schema_valid"], "0/0")

    def test_compare_writes_once_and_refuses_changed_outputs(self):
        outputs = self.write([{"status": "answered", "attempts": [attempt(1500, True)]}])
        manifest = os.path.join(self.tmp, "run_manifest.json")
        comparison = os.path.join(self.tmp, "comparison.json")
        body = {"outputs_sha256": h.sha256_file(outputs), "inputs": {"packets_sha256": "p"}, "provider": {"model": "m"},
                "gpu": "g", "server": {"vllm_version": "v"}}
        with open(manifest, "w", encoding="utf-8") as f:
            json.dump(body, f)
        self.assertEqual(e.compare(outputs, os.path.join(self.tmp, "missing.json"), comparison), 1)
        self.assertEqual(e.compare(outputs, manifest, comparison), 0)
        with open(comparison, encoding="utf-8") as f:
            c = json.load(f)
        self.assertEqual(c["vllm_v1"]["first_attempt_latency_ms"]["median"], 1500)
        self.assertEqual(c["deepseek_c2"]["questions"], 30)
        self.assertEqual(e.compare(outputs, manifest, comparison), 1)  # never overwritten
        os.remove(comparison)
        with open(outputs, "a", encoding="utf-8") as f:
            f.write(json.dumps({"status": "answered", "attempts": [attempt(1, True)]}) + "\n")
        self.assertEqual(e.compare(outputs, manifest, comparison), 1)  # outputs no longer match the manifest
        self.assertFalse(os.path.exists(comparison))


if __name__ == "__main__":
    unittest.main()
