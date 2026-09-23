"""Tests for the publish gate (src/validate_all_reports.py) and the
evidence_items schema check (src/report_schema.py).

Each bad fixture is a way the simulated archive, or a domain-only citation,
could slip back into data/reports/. Every one must fail.

usage: python src/test_publish_gate.py
"""

import copy
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_schema  # noqa: E402
import validate_all_reports  # noqa: E402
from report_schema import SchemaValidationError, validate_report  # noqa: E402
from validate_all_reports import publish_gate_errors  # noqa: E402

TODAY = "2026-09-22"

GOOD = {
    "report_date": "2026-09-21",
    "collection_window": {"start": "2026-09-15", "end": "2026-09-21"},
    "sources_scanned": 3,
    "items_collected": 1,
    "source_sector_breakdown": {"editorial": 1},
    "executive_summary": "Fixture.",
    **{k: [] for k in ("repeated_keywords", "garments", "silhouettes", "materials", "colors",
                       "aesthetic_terms", "cultural_references", "archive_tags")},
    "limitations": ["Fixture."],
    "top_signals": [
        {
            "name": "Fixture signal",
            "type": "aesthetic_term",
            "source_sectors": ["editorial"],
            "confidence": "low",
            "volatility": "emerging",
            "origin_classification": "unclear",
            "evidence": "One dated article.",
            "index_note": "Fixture.",
            "source_domains": ["example.com"],
            "evidence_items": [
                {
                    "url": "https://example.com/2026/09/18/fixture-article",
                    "published_at": "2026-09-18",
                    "retrieved_at": "2026-09-20",
                }
            ],
        }
    ],
}


def bad(mutate):
    d = copy.deepcopy(GOOD)
    mutate(d)
    return d


class PublishGateTests(unittest.TestCase):
    def test_good_fixture_passes_schema_and_gate(self):
        validate_report(GOOD)
        self.assertEqual(publish_gate_errors(GOOD, TODAY), [])

    def test_future_report_date_fails(self):
        d = bad(lambda d: d.update(report_date="2028-04-17"))
        self.assertTrue(any("after today" in e for e in publish_gate_errors(d, TODAY)))

    def test_signal_without_evidence_fails(self):
        d = bad(lambda d: d["top_signals"][0].pop("evidence_items"))
        self.assertTrue(any("no evidence_items" in e for e in publish_gate_errors(d, TODAY)))

    def test_empty_evidence_list_fails(self):
        d = bad(lambda d: d["top_signals"][0].update(evidence_items=[]))
        self.assertTrue(publish_gate_errors(d, TODAY))

    def test_homepage_url_fails(self):
        for url in ("https://vogue.com", "https://www.vogue.com/"):
            d = bad(lambda d, u=url: d["top_signals"][0]["evidence_items"][0].update(url=u))
            self.assertTrue(any("homepage" in e for e in publish_gate_errors(d, TODAY)), url)

    def test_bare_domain_url_fails_schema(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(url="vogue.com"))
        with self.assertRaises(SchemaValidationError):
            validate_report(d)

    def test_evidence_published_after_report_fails(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(
            published_at="2026-09-22", retrieved_at="2026-09-22"))
        self.assertTrue(any("after the report date" in e for e in publish_gate_errors(d, TODAY)))

    def test_missing_dates_fail_schema(self):
        for key in ("published_at", "retrieved_at"):
            d = bad(lambda d, k=key: d["top_signals"][0]["evidence_items"][0].pop(k))
            with self.assertRaises(SchemaValidationError):
                validate_report(d)

    def test_published_after_retrieved_fails_schema(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(
            published_at="2026-09-20", retrieved_at="2026-09-18"))
        with self.assertRaises(SchemaValidationError):
            validate_report(d)

    def test_thin_report_without_evidence_fails(self):
        d = bad(lambda d: d.update(top_signals=[]))
        self.assertTrue(any("no signals" in e for e in publish_gate_errors(d, TODAY)))

    def test_thin_report_with_report_level_evidence_passes(self):
        item = copy.deepcopy(GOOD["top_signals"][0]["evidence_items"][0])
        d = bad(lambda d: d.update(top_signals=[], evidence_items=[item]))
        validate_report(d)
        self.assertEqual(publish_gate_errors(d, TODAY), [])

    def test_report_level_homepage_fails(self):
        d = bad(lambda d: d.update(evidence_items=[{"url": "https://wwd.com/", "published_at": "2026-09-18",
                                                    "retrieved_at": "2026-09-20"}]))
        self.assertTrue(any("homepage" in e for e in publish_gate_errors(d, TODAY)))

    def test_main_fails_on_bad_archive_and_passes_on_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(report_schema, "REPORTS_DIR", tmp):
                path = os.path.join(tmp, "2026-09-21.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(GOOD, f)
                self.assertEqual(validate_all_reports.main(), 0)

                d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(url="https://vogue.com"))
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f)
                self.assertEqual(validate_all_reports.main(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
