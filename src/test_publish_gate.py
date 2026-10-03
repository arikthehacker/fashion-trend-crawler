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
    "review_status": "reviewed",
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
            "human_editor_note": "Fixture editor note.",
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


# The fixture's evidence item "in the item store", and its committed evidence manifest.
STORED = {"item_id": 7, "url": "https://example.com/2026/09/18/fixture-article", "published_at": "2026-09-18T09:00:00Z",
          "retrieved_at": "2026-09-20T10:00:00Z", "first_seen_at": "2026-09-20T10:00:00Z",
          "first_seen_basis": "live_insert", "content_hash": "abc"}
STORE = {STORED["url"]: dict(STORED)}
MANIFEST = {"manifest_version": "evidence-manifest-v1", "report_date": "2026-09-21",
            "collection_window": {"start": "2026-09-15", "end": "2026-09-21"}, "items": [dict(STORED)]}


import evidence_manifest as em  # noqa: E402

SNAPSHOT = em.build_snapshot(GOOD, STORE, frozen_at="2026-09-22T00:00:00Z")
GOOD["evidence_snapshot_sha256"] = SNAPSHOT["snapshot_sha256"]


def bad(mutate):
    d = copy.deepcopy(GOOD)
    mutate(d)
    return d


class PublishGateTests(unittest.TestCase):
    def test_good_fixture_passes_schema_and_gate(self):
        validate_report(GOOD)
        self.assertEqual(publish_gate_errors(GOOD, TODAY, STORE, SNAPSHOT), [])

    def test_future_report_date_fails(self):
        d = bad(lambda d: d.update(report_date="2028-04-17"))
        self.assertTrue(any("after today" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_signal_without_evidence_fails(self):
        d = bad(lambda d: d["top_signals"][0].pop("evidence_items"))
        self.assertTrue(any("no evidence_items" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_empty_evidence_list_fails(self):
        d = bad(lambda d: d["top_signals"][0].update(evidence_items=[]))
        self.assertTrue(publish_gate_errors(d, TODAY, STORE, SNAPSHOT))

    def test_homepage_url_fails(self):
        for url in ("https://vogue.com", "https://www.vogue.com/"):
            d = bad(lambda d, u=url: d["top_signals"][0]["evidence_items"][0].update(url=u))
            self.assertTrue(any("homepage" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)), url)

    def test_bare_domain_url_fails_schema(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(url="vogue.com"))
        with self.assertRaises(SchemaValidationError):
            validate_report(d)

    def test_evidence_published_after_report_fails(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(
            published_at="2026-09-22", retrieved_at="2026-09-22"))
        self.assertTrue(any("after the report date" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

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
        self.assertTrue(any("no signals" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_thin_report_with_report_level_evidence_passes(self):
        item = copy.deepcopy(GOOD["top_signals"][0]["evidence_items"][0])
        d = bad(lambda d: d.update(top_signals=[], evidence_items=[item]))
        validate_report(d)
        self.assertEqual(publish_gate_errors(d, TODAY, STORE, SNAPSHOT), [])

    def test_report_level_homepage_fails(self):
        d = bad(lambda d: d.update(evidence_items=[{"url": "https://wwd.com/", "published_at": "2026-09-18",
                                                    "retrieved_at": "2026-09-20"}]))
        self.assertTrue(any("homepage" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_ai_assistance_is_optional_but_never_empty(self):
        validate_report(dict(GOOD, ai_assistance="Software collected the items and matched the terms."))
        for value in ("", "   ", 3):
            with self.assertRaises(SchemaValidationError):
                validate_report(dict(GOOD, ai_assistance=value))

    def test_main_fails_on_bad_archive_and_passes_on_good(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(report_schema, "REPORTS_DIR", tmp),                     mock.patch.object(validate_all_reports, "load_store_index", lambda: STORE),                     mock.patch.object(validate_all_reports, "load_snapshot", lambda date: SNAPSHOT):
                path = os.path.join(tmp, "2026-09-21.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(GOOD, f)
                self.assertEqual(validate_all_reports.main([]), 0)

                d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(url="https://vogue.com"))
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f)
                self.assertEqual(validate_all_reports.main([]), 1)



class NewReportGateTests(unittest.TestCase):
    """Owner decision Q21: reports dated after HISTORICAL_CUTOFF."""

    def test_historical_report_keeps_its_rules(self):
        old = bad(lambda d: d.update(report_date="2026-05-18",
                                     collection_window={"start": "2026-05-12", "end": "2026-05-18"}))
        old["top_signals"][0].update(human_editor_note="")
        old["top_signals"][0]["evidence_items"][0].update(published_at="2026-05-14", retrieved_at="2026-09-23")
        old.pop("review_status")
        self.assertEqual(publish_gate_errors(old, TODAY, None), [])
        real = report_schema.load_report("2026-05-18")
        validate_report(real)
        self.assertEqual(publish_gate_errors(real, "2026-10-03", None), [])

    def test_draft_fails_for_the_expected_reasons(self):
        d = bad(lambda d: d.update(review_status="draft"))
        d["top_signals"][0]["human_editor_note"] = ""
        errors = publish_gate_errors(d, TODAY, STORE, SNAPSHOT)
        self.assertTrue(any("review_status" in e for e in errors))
        self.assertTrue(any("human_editor_note" in e for e in errors))
        self.assertEqual(len(errors), 2)

    def test_missing_review_status_fails(self):
        d = bad(lambda d: d.pop("review_status"))
        self.assertTrue(any("review_status" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_reviewed_report_with_note_and_stored_evidence_passes(self):
        self.assertEqual(publish_gate_errors(GOOD, TODAY, STORE, SNAPSHOT), [])

    # ---- frozen evidence review snapshot (evidence-review-snapshot-v1) ----

    def test_1_snapshot_records_the_store_state_at_build_time(self):
        entry = SNAPSHOT["items"][0]
        self.assertEqual((entry["retrieved_at"], entry["content_hash"]), (STORED["retrieved_at"], STORED["content_hash"]))
        self.assertEqual(entry, STORED)
        self.assertEqual(SNAPSHOT["snapshot_version"], "evidence-review-snapshot-v1")

    def test_2_snapshot_fingerprint_is_deterministic(self):
        again = em.build_snapshot(GOOD, STORE, frozen_at="2030-01-01T00:00:00Z")  # build time is not fingerprinted
        self.assertEqual(again["snapshot_sha256"], SNAPSHOT["snapshot_sha256"])
        self.assertEqual(em.snapshot_fingerprint(SNAPSHOT), SNAPSHOT["snapshot_sha256"])

    def test_3_changing_a_frozen_snapshot_breaks_its_fingerprint(self):
        tampered = copy.deepcopy(SNAPSHOT)
        tampered["items"][0]["retrieved_at"] = "2026-09-21T00:00:00Z"
        self.assertNotEqual(em.snapshot_fingerprint(tampered), SNAPSHOT["snapshot_sha256"])
        self.assertTrue(any("own fingerprint" in e for e in publish_gate_errors(GOOD, TODAY, STORE, tampered)))

    def test_4_report_bound_to_another_snapshot_fails(self):
        d = bad(lambda d: d.update(evidence_snapshot_sha256="0" * 64))
        self.assertTrue(any("not bound" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))
        d = bad(lambda d: d.pop("evidence_snapshot_sha256"))
        self.assertTrue(any("not bound" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_5_missing_snapshot_fails_even_when_the_store_check_is_skipped(self):
        for store in (STORE, validate_all_reports.SKIP_STORE):
            self.assertTrue(any("snapshot missing" in e for e in publish_gate_errors(GOOD, TODAY, store, None)))

    def _resealed(self, mutate):
        snap = copy.deepcopy(SNAPSHOT)
        mutate(snap)
        snap["snapshot_sha256"] = em.snapshot_fingerprint(snap)
        return snap, dict(GOOD, evidence_snapshot_sha256=snap["snapshot_sha256"])

    def test_6_duplicate_item_ids_fail(self):
        snap, report = self._resealed(lambda s: s["items"].append(dict(STORED, url="https://example.com/other")))
        self.assertTrue(any("repeats" in e for e in publish_gate_errors(report, TODAY, validate_all_reports.SKIP_STORE, snap)))

    def test_7_duplicate_canonical_urls_fail(self):
        snap, report = self._resealed(lambda s: s["items"].append(dict(STORED, item_id=99)))
        self.assertTrue(any("repeats" in e for e in publish_gate_errors(report, TODAY, validate_all_reports.SKIP_STORE, snap)))

    def test_8_report_evidence_absent_from_the_snapshot_fails(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(url="https://example.com/2026/09/18/other"))
        self.assertTrue(any("not in the evidence manifest" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_9_later_store_refresh_does_not_rewrite_or_invalidate_the_snapshot(self):
        frozen = copy.deepcopy(SNAPSHOT)
        refreshed_store = {STORED["url"]: dict(STORED, retrieved_at="2026-10-01T00:00:00Z", content_hash="changed")}
        self.assertEqual(publish_gate_errors(GOOD, TODAY, refreshed_store, SNAPSHOT), [])
        self.assertEqual(SNAPSHOT, frozen)  # the frozen record is untouched by the check
        self.assertEqual(SNAPSHOT["items"][0]["content_hash"], "abc")

    def test_10_historical_report_needs_no_snapshot(self):
        real = report_schema.load_report("2026-05-18")
        validate_report(real)
        self.assertNotIn("evidence_snapshot_sha256", real)
        for store in (None, validate_all_reports.SKIP_STORE, STORE):
            self.assertEqual(publish_gate_errors(real, "2026-10-03", store, None), [])

    def test_identity_change_in_the_live_store_still_fails(self):
        moved = {STORED["url"]: dict(STORED, first_seen_at="2026-09-21T00:00:00Z")}
        self.assertTrue(any("differs from the item store" in e for e in publish_gate_errors(GOOD, TODAY, moved, SNAPSHOT)))
        self.assertTrue(any("not in the item store" in e for e in publish_gate_errors(GOOD, TODAY, {}, SNAPSHOT)))

    def test_window_disagreement_fails(self):
        snap, report = self._resealed(lambda s: s.update(collection_window={"start": "2026-09-14", "end": "2026-09-21"}))
        self.assertTrue(any("collection window" in e for e in publish_gate_errors(report, TODAY, STORE, snap)))

    def test_snapshot_build_refuses_a_store_that_drifted_since_the_draft(self):
        draft = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(
            item_id=7, retrieved_at="2026-09-20T10:00:00Z", content_hash="abc"))
        drifted = {STORED["url"]: dict(STORED, content_hash="new")}
        with self.assertRaises(ValueError):
            em.build_snapshot(draft, drifted)
        self.assertEqual(em.build_snapshot(draft, STORE)["snapshot_sha256"], SNAPSHOT["snapshot_sha256"])

    def test_v1_membership_manifest_keeps_its_meaning(self):
        self.assertEqual(em.build_manifest(GOOD, STORE)["manifest_version"], "evidence-manifest-v1")
        self.assertEqual(em.shape_errors(MANIFEST, GOOD), [])
        self.assertTrue(any("version" in e for e in em.shape_errors(SNAPSHOT, GOOD)))  # versions are not interchangeable

    def test_report_and_snapshot_disagreeing_on_the_item_fails(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(item_id=8))
        self.assertTrue(any("disagree on the item" in e for e in publish_gate_errors(d, TODAY, STORE, SNAPSHOT)))

    def test_store_url_matching_uses_the_store_canonical_form(self):
        d = bad(lambda d: d["top_signals"][0]["evidence_items"][0].update(
            url="https://EXAMPLE.com/2026/09/18/fixture-article/?utm_source=x"))
        self.assertEqual(publish_gate_errors(d, TODAY, STORE, SNAPSHOT), [])

    def test_unavailable_store_fails_locally(self):
        self.assertTrue(any("item store is not available" in e for e in publish_gate_errors(GOOD, TODAY, None, SNAPSHOT)))

    def test_ci_mode_passes_with_the_bound_snapshot(self):
        self.assertEqual(publish_gate_errors(GOOD, TODAY, validate_all_reports.SKIP_STORE, SNAPSHOT), [])

    def test_main_in_ci_mode_requires_the_committed_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(report_schema, "REPORTS_DIR", tmp), \
                    mock.patch.object(validate_all_reports, "load_store_index", lambda: None):
                with open(os.path.join(tmp, "2026-09-21.json"), "w", encoding="utf-8") as f:
                    json.dump(GOOD, f)
                with mock.patch.object(validate_all_reports, "load_snapshot", lambda date: None):
                    self.assertEqual(validate_all_reports.main(["--store-optional"]), 1)
                with mock.patch.object(validate_all_reports, "load_snapshot", lambda date: SNAPSHOT):
                    self.assertEqual(validate_all_reports.main(["--store-optional"]), 0)

    def test_schema_checks_the_binding_field_format(self):
        validate_report(GOOD)
        with self.assertRaises(SchemaValidationError):
            validate_report(dict(GOOD, evidence_snapshot_sha256="not-a-hash"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
