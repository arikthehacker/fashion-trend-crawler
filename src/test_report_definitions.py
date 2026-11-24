"""Tests for the editor's report definitions (src/report_definitions.py) and the named merge list.

usage: python src/test_report_definitions.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_definitions as d  # noqa: E402
import report_review  # noqa: E402


class DefinitionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "defs.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def filled(self):
        lines = []
        for section, keys in d.expected_keys().items():
            lines += [f"## {section}"] + [f"- {k}: means {k}." for k in keys] + [""]
        return "\n".join(lines + ["## Rules", "- two items from two outlets", ""])

    def test_empty_render_covers_every_app_option_and_is_unwritten(self):
        self.write(d.render({}))
        parsed = d.parse(d.text(self.path))
        for section, keys in d.expected_keys().items():
            self.assertEqual([k for k, _ in parsed[section]], keys, section)
        self.assertEqual(len(d.problems(self.path)), sum(len(k) for k in d.expected_keys().values()) + 1)

    @unittest.skipUnless(os.path.exists(d.PATH), "the definitions file is local to the editor's PC")
    def test_live_file_has_every_option(self):
        parsed = d.parse(d.text())  # the editor's real file: only its shape is checked, never its words
        for section, keys in d.expected_keys().items():
            self.assertEqual([k for k, _ in parsed[section]], keys, section)

    def test_filled_file_has_no_problems(self):
        self.write(self.filled())
        self.assertEqual(d.problems(self.path), [])
        self.assertNotIn("not written yet", d.panel_text(self.path))

    def test_definition_with_a_colon_is_kept_whole(self):
        self.write(self.filled().replace("- keep: means keep.", "- keep: in the report: yes"))
        self.assertIn(("keep", "in the report: yes"), d.parse(d.text(self.path))["Decision"])

    def test_unknown_and_missing_options_are_reported(self):
        self.write(self.filled().replace("- drop: means drop.", "- discard: no"))
        issues = d.problems(self.path)
        self.assertIn("Decision: 'drop' is missing", issues)
        self.assertIn("Decision: 'discard' is not an option the app offers", issues)

    def test_hash_ignores_line_endings(self):
        self.write("a\nb\n")
        a = d.sha256(self.path)
        with open(self.path, "wb") as f:
            f.write(b"a\r\nb\r\n")
        self.assertEqual(a, d.sha256(self.path))


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.log, self.path = os.path.join(self.tmp, "log.jsonl"), os.path.join(self.tmp, "defs.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_one_card_per_option_plus_rules(self):
        cards = d.cards()
        self.assertEqual(len(cards), sum(len(k) for k in d.expected_keys().values()) + 1)
        self.assertEqual(cards[-1]["card_id"], "Rules")

    @unittest.skipUnless(os.path.exists(d.PATH), "the definitions file is local to the editor's PC")
    def test_live_file_matches_the_log(self):
        self.assertEqual(d.text(), d.render(d.final_answers()))

    def test_brain_dump_kept_exactly_and_latest_wins(self):
        dump = "In the report.\nOnly if I would stand behind it:\nit has to feel real."
        d.record("Decision:keep", "first try", self.log, self.path)
        d.record("Decision:keep", dump, self.log, self.path)
        d.record("Rules", "two items from two outlets\n\nno single-event bursts", self.log, self.path)
        parsed = d.parse(d.text(self.path))
        self.assertEqual(dict(parsed["Decision"])["keep"], dump)
        self.assertEqual([r for _, r in parsed["Rules"]], ["two items from two outlets", "no single-event bursts"])
        self.assertEqual(len(d.load_log(self.log)), 3)  # append-only
        self.assertEqual(d.left(self.log), (len(d.cards()) - 2, len(d.cards())))
        with self.assertRaises(ValueError):
            d.record("Decision:discard", "x", self.log, self.path)


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        j = lambda n: os.path.join(self.tmp, n)
        self.kw = {"log": j("log.jsonl"), "path": j("defs.md"), "copyedit": j("copyedit.json"),
                   "approvals": j("approvals.jsonl")}
        d.record("Decision:keep", "kep it if its real", **self.kw)
        d.record("Decision:drop", "not style", **self.kw)
        with open(self.kw["copyedit"], "w", encoding="utf-8") as f:
            json.dump({"Decision:keep": {"original_sha256": d.text_sha("kep it if its real"),
                                         "copyedit": "Keep it if it's real.", "flag": None},
                       "Decision:drop": {"original_sha256": d.text_sha("not style"), "copyedit": None,
                                         "flag": "'not style' could mean two things"}}, f)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def defs(self):
        return dict(d.parse(d.text(self.kw["path"]))["Decision"])

    def test_only_approved_copyedits_reach_the_file(self):
        self.assertEqual(self.defs()["keep"], "kep it if its real")
        d.record_approval("Decision:keep", "copyedit", **self.kw)
        self.assertEqual(self.defs()["keep"], "Keep it if it's real.")
        d.record_approval("Decision:keep", "original", **self.kw)
        self.assertEqual(self.defs()["keep"], "kep it if its real")
        d.record_approval("Decision:keep", "rewrite", "Keep: I would stand behind it.", **self.kw)
        self.assertEqual(self.defs()["keep"], "Keep: I would stand behind it.")
        self.assertEqual(len(d.load_log(self.kw["approvals"])), 3)  # append-only

    def test_flagged_card_cannot_take_a_copyedit(self):
        with self.assertRaises(ValueError):
            d.record_approval("Decision:drop", "copyedit", **self.kw)
        d.record_approval("Decision:drop", "rewrite", "Not about clothing.", **self.kw)
        self.assertEqual(self.defs()["drop"], "Not about clothing.")

    def test_changing_the_dump_voids_the_copyedit_and_the_approval(self):
        d.record_approval("Decision:keep", "copyedit", **self.kw)
        d.record("Decision:keep", "keep it if i believe it", **self.kw)
        row = next(r for r in d.approval_rows(self.kw["log"], self.kw["copyedit"], self.kw["approvals"])
                   if r["card_id"] == "Decision:keep")
        self.assertIsNone(row["copyedit"])
        self.assertTrue(row["stale_copyedit"])
        self.assertIsNone(row["approval"])
        self.assertEqual(self.defs()["keep"], "keep it if i believe it")

    def test_approval_count(self):
        n = len(d.cards())
        self.assertEqual(d.approval_left(self.kw["log"], self.kw["copyedit"], self.kw["approvals"]), (n, n))
        d.record_approval("Decision:keep", "copyedit", **self.kw)
        self.assertEqual(d.approval_left(self.kw["log"], self.kw["copyedit"], self.kw["approvals"]), (n - 1, n))


class MergeChoicesTests(unittest.TestCase):
    def test_names_shown_ids_kept(self):
        q = {"cards": [{"kind": "signal", "signal_id": "loafer", "name": "Loafers"},
                       {"kind": "signal", "signal_id": "denim", "name": "Denim"},
                       {"kind": "duplicate", "card_id": "duplicate:1"}]}
        self.assertEqual(report_review.merge_choices(q, q["cards"][0]), [("Denim", "denim")])
        q["cards"].append({"kind": "signal", "signal_id": "denim-2", "name": "Denim"})
        self.assertEqual([s for s, _ in report_review.merge_choices(q, q["cards"][0])], ["Denim [denim]", "Denim [denim-2]"])


if __name__ == "__main__":
    unittest.main()
