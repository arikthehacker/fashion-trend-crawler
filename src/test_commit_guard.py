"""Tests for src/commit_guard.py.

Fake credentials are assembled at runtime, so this file never contains a string the
guard would block, and none of them could be mistaken for a real key.

usage: python src/test_commit_guard.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import commit_guard as g  # noqa: E402

FAKE_SK = "sk-" + "0" * 40
FAKE_ANT = "sk-" + "ant-" + "x" * 30
FAKE_GH = "gh" + "p_" + "A" * 36
FAKE_LOCAL = "fixture" + "-not-a-real-secret-" + "7" * 8
KEY = "DEEPSEEK" + "_API_KEY"
PEM = "-----BEGIN " + "RSA PRIVATE KEY-----"
GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commit_guard.py")


class ScanLineTests(unittest.TestCase):
    def test_empty_placeholder_passes(self):
        self.assertEqual(g.scan_line(f"{KEY}="), [])
        self.assertEqual(g.scan_line("# Server-side only. Never expose through NEXT_PUBLIC_*."), [])

    def test_fake_placeholder_value_is_blocked(self):
        self.assertIn("env_assignment", g.scan_line(f"{KEY}=your-api-key-here"))

    def test_real_looking_values_are_blocked(self):
        self.assertIn("env_assignment", g.scan_line(f"export {KEY}={FAKE_SK}"))
        self.assertIn("known_prefix", g.scan_line(f"key = '{FAKE_SK}'"))
        self.assertIn("known_prefix", g.scan_line(f"see {FAKE_ANT} here"))
        self.assertIn("known_prefix", g.scan_line(f"token {FAKE_GH}"))
        self.assertIn("code_literal", g.scan_line('api_key = "' + "q" * 24 + '"'))
        self.assertIn("code_literal", g.scan_line('{"access_token": "' + "q" * 24 + '"}'))
        self.assertIn("private_key", g.scan_line(PEM))

    def test_authorization_headers_are_blocked(self):
        self.assertIn("authorization", g.scan_line("Authorization: Bearer " + "a1" * 12))
        self.assertIn("bearer_token", g.scan_line("curl -H 'bearer " + "b2" * 12 + "'"))

    def test_references_pass(self):
        for line in (f'api_key = os.environ["{KEY}"]', f"{KEY}=${{{KEY}}}", f'env_var = "{KEY}"',
                     'headers = {"Authorization": f"Bearer {key}"}', "max_tokens = 1024",
                     'tokenizer = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"',
                     'SORT_KEY = "published_at"', "input_tokens: 512", "f'TOKEN=\"{value}-suffix-text\"'"):
            self.assertEqual(g.scan_line(line), [], line)

    def test_local_env_value_is_matched_without_being_reported(self):
        self.assertEqual(g.scan_line(f"note: {FAKE_LOCAL}", {FAKE_LOCAL}), ["local_env_value"])


class LocalValueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_only_long_secret_named_values_are_used(self):
        self.write(".env", f"{KEY}={FAKE_LOCAL}\nSHORT_TOKEN=abc123\nSITE_URL=https://www.example.com/long/path\n"
                           "PLACEHOLDER_API_KEY=your-api-key-here-for-docs\nSAME_SECRET=aaaaaaaaaaaaaaaa\n")
        self.write(os.path.join("web", ".env.local"), f'OTHER_TOKEN="{FAKE_LOCAL}-web"\n')
        self.write(".env.example", f"{KEY}=ignored-because-example-file\n")
        self.assertEqual(g.local_secret_values([self.tmp]), {FAKE_LOCAL, FAKE_LOCAL + "-web"})


class DiffTests(unittest.TestCase):
    def test_added_lines_track_paths_and_line_numbers(self):
        diff = ("diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -3,0 +4,2 @@\n+ok = 1\n"
                f"+key = '{FAKE_SK}'\n-removed = '{FAKE_SK}'\n"
                "diff --git a/img.png b/img.png\nBinary files /dev/null and b/img.png differ\n")
        self.assertEqual(list(g.added_lines(diff)), [("x.py", 4, "ok = 1"), ("x.py", 5, f"key = '{FAKE_SK}'")])
        self.assertEqual(g.scan_diff(diff), [("x.py", 5, "known_prefix")])


class MessageTests(unittest.TestCase):
    def test_clean_messages_pass(self):
        for text in ("Add DeepSeek provider behind the provider interface\n\nThe key is read from the "
                     "environment and never logged.\n",
                     "Amend EXP-003A eligibility before any holdout label exists\n",
                     "Fix: Claude-free subject line mentioning OpenAI-compatible endpoints\n"):
            self.assertEqual(g.check_message(text), [], text)

    def test_attribution_is_blocked(self):
        cases = {
            "Fix thing\n\nCo-Authored-By: Someone <noreply@example.com>\n": "attribution_trailer",
            "Fix thing\n\nAssisted-by: a tool\n": "attribution_trailer",
            "Fix thing\n\nGenerated with Claude Code\n": "generated_by_ai",
            "Fix thing\n\nThis change was written by an AI model.\n": "generated_by_ai",
            "Fix thing\n\nReviewed-by: ChatGPT\n": "vendor_trailer",
            "Fix thing\n\n\U0001F916 made here\n": "ai_marker",
        }
        for text, rule in cases.items():
            self.assertIn(rule, [r for _, r in g.check_message(text)], text)

    def test_git_comment_lines_are_ignored(self):
        self.assertEqual(g.check_message("Fix thing\n# Co-Authored-By: in a git comment\n"), [])


class GitIntegrationTests(unittest.TestCase):
    """Runs the guard as the hooks do, inside a throwaway repository."""

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        self.git("config", "user.name", "arikthehacker")
        self.git("config", "user.email", "128088661+arikthehacker@users.noreply.github.com")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, check=True)

    def guard(self, *args):
        return subprocess.run([sys.executable, GUARD, *args], cwd=self.repo, capture_output=True, text=True)

    def stage(self, name, text):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as f:
            f.write(text)
        self.git("add", name)

    def test_staged_secret_blocks_without_printing_it(self):
        self.stage("config.py", f"key = '{FAKE_SK}'\n")
        result = self.guard("staged")
        self.assertEqual(result.returncode, 1)
        self.assertIn("config.py:1 (rule: known_prefix)", result.stderr)
        self.assertNotIn(FAKE_SK, result.stderr + result.stdout)

    def test_local_env_value_blocks_without_printing_it(self):
        with open(os.path.join(self.repo, ".env"), "w", encoding="utf-8") as f:
            f.write(f"{KEY}={FAKE_LOCAL}\n")
        self.stage("notes.md", f"pasted by accident: {FAKE_LOCAL}\n")
        result = self.guard("staged")
        self.assertEqual(result.returncode, 1)
        self.assertIn("rule: local_env_value", result.stderr)
        self.assertNotIn(FAKE_LOCAL, result.stderr + result.stdout)

    def test_clean_stage_and_empty_example_pass(self):
        self.stage(".env.example", f"{KEY}=\n")
        self.stage("app.py", f'key = os.environ["{KEY}"]\n')
        self.assertEqual(self.guard("staged").returncode, 0)

    def test_identity(self):
        self.assertEqual(self.guard("identity").returncode, 0)
        self.git("config", "user.email", "someone-else@example.com")
        result = self.guard("identity")
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected", result.stderr)

    def test_message_file(self):
        path = os.path.join(self.repo, "MSG")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Fix thing\n\nCo-Authored-By: x <y@example.com>\n")
        self.assertEqual(self.guard("message", path).returncode, 1)

    def test_unknown_command_fails_closed(self):
        self.assertEqual(self.guard("bogus").returncode, 1)


if __name__ == "__main__":
    unittest.main()
