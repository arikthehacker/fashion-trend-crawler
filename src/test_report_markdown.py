"""Tests for src/report_markdown.py: exporting a report to Markdown and
applying the editor's edits back without losing or corrupting any field.

usage: python src/test_report_markdown.py
"""

import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_markdown as rm  # noqa: E402
from test_publish_gate import GOOD  # noqa: E402


class ReportMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.report = copy.deepcopy(GOOD)
        self.report["review_status"] = "draft"

    def test_round_trip_without_edits_changes_nothing(self):
        new, changes, approved = rm.apply_markdown(rm.export_markdown(self.report), self.report)
        self.assertEqual(changes, [])
        self.assertFalse(approved)
        self.assertEqual(new, self.report)

    def test_edits_to_prose_are_applied(self):
        md = rm.export_markdown(self.report)
        md = md.replace("Fixture.\n\n### ✏️ Your editor note", "Rewritten index note.\n\n### ✏️ Your editor note", 1)
        md = md.replace("## ✏️ Executive summary\n\nFixture.", "## ✏️ Executive summary\n\nA new summary.", 1)
        new, changes, _ = rm.apply_markdown(md, self.report)
        self.assertEqual(new["executive_summary"], "A new summary.")
        self.assertEqual(new["top_signals"][0]["index_note"], "Rewritten index note.")
        self.assertEqual(len(changes), 2)

    def test_editor_note_is_written_only_where_the_editor_wrote_it(self):
        md = rm.export_markdown(self.report)
        marker = "### ✏️ Your editor note (only you write this; leave empty if none)\n\n"
        md = md.replace(marker, marker + "Worth watching into resort season.", 1)
        new, _, _ = rm.apply_markdown(md, self.report)
        self.assertEqual(new["top_signals"][0]["human_editor_note"], "Worth watching into resort season.")

    def test_locked_lines_cannot_change_evidence_or_dates(self):
        md = rm.export_markdown(self.report)
        md = md.replace("https://example.com/2026/09/18/fixture-article", "https://evil.example/", )
        md = md.replace("2026-09-15", "2030-01-01")
        new, _, _ = rm.apply_markdown(md, self.report)
        self.assertEqual(new["top_signals"][0]["evidence_items"], self.report["top_signals"][0]["evidence_items"])
        self.assertEqual(new["collection_window"], self.report["collection_window"])

    def test_approval_marks_reviewed(self):
        md = rm.export_markdown(self.report).replace("Approved: no", "Approved: yes")
        new, _, approved = rm.apply_markdown(md, self.report)
        self.assertTrue(approved)
        self.assertEqual(new["review_status"], "reviewed")

    def test_limitations_edit(self):
        md = rm.export_markdown(self.report).replace("- Fixture.", "- First limit.\n- Second limit.")
        new, _, _ = rm.apply_markdown(md, self.report)
        self.assertEqual(new["limitations"], ["First limit.", "Second limit."])


if __name__ == "__main__":
    unittest.main(verbosity=2)
