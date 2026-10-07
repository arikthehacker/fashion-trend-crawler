"""Tests for the weekly report workflow: src/report_review.py, src/report_finalize.py and the window
and readiness rules of src/report_prepare.py. Synthetic draft, temp folder, no store, no network.

usage: python src/test_report_finalize.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_finalize as rf  # noqa: E402
import report_prepare as rp  # noqa: E402
import report_review as rr  # noqa: E402


def item(i, outlet, sector="editorial", day="2026-10-05", title=None):
    return {"item_id": i, "url": f"https://{outlet}/a/{i}", "title": title or f"Headline {i}", "outlet_domain": outlet,
            "sector": sector, "sector_group": "retail" if sector == "retail" else "editorial", "published_at": f"{day}T10:00:00Z",
            "retrieved_at": f"{day}T12:00:00Z", "first_seen_at": f"{day}T12:00:00Z", "first_seen_basis": "live_insert",
            "content_hash": f"h{i}", "lang": "en", "style_set": ["yes"], "p_style": 0.9, "terms": []}


def signal(sid, items, kind="material"):
    sectors = sorted({e["sector"] for e in items})
    return {"signal_id": sid, "name": sid, "type": kind, "source_sectors": sectors,
            "source_domains": sorted({e["outlet_domain"] for e in items}),
            "source_corroboration_count": len({e["outlet_domain"] for e in items}), "confidence": "high" if len(sectors) > 1 else "medium",
            "confidence_source": "derived", "volatility": "", "origin_classification": "unclear", "evidence": "", "index_note": "",
            "human_editor_note": "", "evidence_items": items,
            "draft_audit": {"dates": ["2026-10-05"], "items_by_sector": {}, "sector_groups": [], "cross_sector": len(sectors) > 1,
                            "cross_sector_group": False, "reconstructed_first_seen_items": 0, "not_sure_items_with_term": [],
                            "not_style_items_with_term": [], "max_items_from_one_outlet": 1}}


def draft():
    a = [item(1, "a.com"), item(2, "b.com", "retail"), item(3, "pub.com", title="Same story"), item(4, "pub.uk", title="Same story")]
    b = [item(2, "b.com", "retail"), item(5, "c.com")]
    c = [item(6, "vogue.com", day="2026-10-06"), item(7, "vogue.de", day="2026-10-07"), item(8, "d.com", day="2026-10-08")]
    return {"report_date": "2026-10-11", "collection_window": {"start": "2026-10-05", "end": "2026-10-11"}, "sources_scanned": 9,
            "items_collected": 1234, "source_sector_breakdown": {"editorial": 1200, "retail": 34}, "executive_summary": "",
            "top_signals": [signal("alpha", a), signal("beta", b), signal("gamma", c)], "repeated_keywords": [], "garments": [],
            "silhouettes": [], "materials": [], "colors": [], "aesthetic_terms": [], "cultural_references": [],
            "limitations": ["A drafter limitation."], "archive_tags": [], "collection_status": "normal", "review_status": "draft",
            "evidence_snapshot_sha256": "s" * 64, "draft_meta": {}}


AUDIT = {"exact": [{"why": "identical headline and feed excerpt, one publisher on two domains",
                    "items": [{"item_id": 3, "outlet": "pub.com", "published": "2026-10-05T10:00:00Z", "title": "Same story", "signals": ["alpha"]},
                              {"item_id": 4, "outlet": "pub.uk", "published": "2026-10-05T10:00:00Z", "title": "Same story", "signals": ["alpha"]}]}],
         "possible": [{"why": "one publisher brand on two domains",
                       "items": [{"item_id": 6, "outlet": "vogue.com", "published": "2026-10-06T10:00:00Z", "title": "Headline 6", "signals": ["gamma"]},
                                 {"item_id": 7, "outlet": "vogue.de", "published": "2026-10-07T10:00:00Z", "title": "Headline 7", "signals": ["gamma"]}]}]}
KEEP = {"decision": "keep", "volatility": "recurring", "thoughts": "A note."}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.queue = rr.build_decision_queue(draft(), AUDIT, os.path.join(self.tmp, "decisions.jsonl"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def decide(self, **by_card):
        for card_id, payload in by_card.items():
            rr.record(self.queue, card_id.replace("__", ":"), payload)
        return rr.latest(self.queue)

    def test_deck_has_a_card_per_candidate_and_possible_duplicate(self):
        self.assertEqual([c["card_id"] for c in self.queue["cards"]], ["signal:alpha", "signal:beta", "signal:gamma", "duplicate:1", "report"])
        self.assertEqual(rr.left(self.queue), (4, 4))
        self.assertIn("EVIDENCE", rr.card_text(self.queue["cards"][0]))

    def test_incomplete_or_invalid_decisions_are_refused(self):
        bad = [{"decision": "keep"}, {"decision": "keep", "volatility": "Medium", "thoughts": "x"},
               {"decision": "keep", "volatility": "recurring", "thoughts": " "}, {"decision": "merge"},
               {"decision": "merge", "merge_into": "alpha"}, {"decision": "drop", "remove_item_ids": [99]}, {"decision": "maybe"}]
        for payload in bad:
            with self.assertRaises(ValueError, msg=payload):
                rr.record(self.queue, "signal:alpha", payload)
        with self.assertRaises(ValueError):
            rr.record(self.queue, "duplicate:1", {"thoughts": "unsure"})
        self.assertEqual(rr.left(self.queue), (4, 4))

    def test_latest_answer_wins(self):
        self.decide(signal__alpha={"decision": "drop"})
        d = self.decide(signal__alpha=dict(KEEP))
        self.assertEqual(d["signal:alpha"]["decision"], "keep")

    def test_apply_needs_every_decision(self):
        d = self.decide(signal__alpha=dict(KEEP))
        with self.assertRaises(ValueError) as ctx:
            rf.apply_decisions(draft(), self.queue, d, AUDIT)
        self.assertIn("beta: no decision yet", str(ctx.exception))

    def test_merge_dedupes_prunes_and_collapses(self):
        d = self.decide(signal__alpha=dict(KEEP, name="Alpha framing", confidence="medium", remove_item_ids=[1]),
                        signal__beta={"decision": "merge", "merge_into": "alpha"}, signal__gamma=dict(KEEP, volatility="seasonal"),
                        duplicate__1={"collapse": True})
        r = rf.apply_decisions(draft(), self.queue, d, AUDIT, draft_sha="x")
        alpha, gamma = r["top_signals"]
        self.assertEqual([e["item_id"] for e in alpha["evidence_items"]], [2, 3, 5])  # 1 pruned, 2 not doubled, mirror 4 collapsed
        self.assertEqual((alpha["name"], alpha["confidence"], alpha["confidence_source"]), ("Alpha framing", "medium", "manual"))
        self.assertEqual(alpha["source_domains"], ["b.com", "c.com", "pub.com"])  # the mirror domain adds no outlet
        self.assertEqual(alpha["draft_audit"]["merged_terms"]["beta"], {"items": 2, "already_in_signal": [2], "added": 1})
        self.assertEqual([c["collapsed_item_id"] for c in alpha["draft_audit"]["collapsed_duplicates"]], [4])
        self.assertEqual([e["item_id"] for e in gamma["evidence_items"]], [6, 8])  # the earliest published edition is kept
        self.assertEqual(gamma["volatility"], "seasonal")
        self.assertEqual(r["limitations"], ["A drafter limitation.", rf.DEDUP_LIMITATION])
        self.assertTrue(all(s["human_editor_note"] == s["evidence"] == "" for s in r["top_signals"]))
        self.assertEqual(r["draft_meta"]["editor_decisions"]["editor_thoughts"]["alpha"], "A note.")

    def test_a_signal_that_falls_below_the_rule_stops_the_apply(self):
        d = self.decide(signal__alpha=dict(KEEP), signal__beta={"decision": "drop"}, signal__gamma=dict(KEEP, remove_item_ids=[8]),
                        duplicate__1={"collapse": True})
        with self.assertRaises(ValueError) as ctx:
            rf.apply_decisions(draft(), self.queue, d, AUDIT)
        self.assertIn("gamma", str(ctx.exception))
        self.assertIn("below the report rule", str(ctx.exception))

    def report(self):
        d = self.decide(signal__alpha=dict(KEEP), signal__beta={"decision": "drop"}, signal__gamma={"decision": "watchlist"},
                        duplicate__1={"collapse": False})
        return rf.apply_decisions(draft(), self.queue, d, AUDIT, draft_sha="x")

    def text(self, **over):
        t = {"executive_summary": "ARI3 collected 1,234 raw source records from 9 outlet domains. The largest signal is alpha (3 items from 3 outlets).",
             "signals": {"alpha": {"evidence": "Headlines cover the term.", "index_note": "The signal has 3 items from 3 outlets.",
                                   "human_editor_note": "Editorial view: this reads as seasonal."}}}
        t["signals"]["alpha"].update(over)
        return t

    def test_text_goes_in_only_when_counts_and_voice_hold(self):
        r = self.report()
        self.assertEqual(rf.text_errors(r, self.text()), [])
        out = rf.set_text(r, self.text())
        self.assertEqual(rf.sha_obj(rf.structure(out)), rf.sha_obj(rf.structure(r)))
        self.assertEqual(out["top_signals"][0]["human_editor_note"], "Editorial view: this reads as seasonal.")
        for over, expect in (({"index_note": "The signal has 4 items from 3 outlets."}, "exact count"),
                             ({"human_editor_note": "I think this is seasonal."}, "first person"),
                             ({"evidence": "Sneakers are rising."}, "rising"), ({"evidence": "One; two."}, "semicolon"),
                             ({"human_editor_note": ""}, "empty")):
            errors = rf.text_errors(r, self.text(**over))
            self.assertTrue(any(expect in e for e in errors), (over, errors))
        self.assertEqual(rf.text_errors(r, self.text(evidence="A surprising and comprising mix.")), [])  # whole words only
        bad_summary = self.text()
        bad_summary["executive_summary"] = "ARI3 collected 1,234 raw source records from 9 outlet domains. Alpha (5 items from 3 outlets)."
        self.assertTrue(any("matches no signal" in e for e in rf.text_errors(r, bad_summary)))

    def test_approval_cards_change_id_when_their_text_changes(self):
        r = rf.set_text(self.report(), self.text())
        q1 = rf.approval_queue(r, os.path.join(self.tmp, "approvals.jsonl"))
        self.assertEqual([t["question_id"] for t in q1["tasks"]], ["summary", "signal:alpha", "duplicates", "limitations"])
        self.assertIn("YOUR THOUGHTS AS YOU WROTE THEM\nA note.", q1["tasks"][1]["body"])
        import exp005_review
        for t in q1["tasks"]:
            exp005_review.record(q1, t, "APPROVE")
        self.assertEqual(len(rf.approval_status(q1)["approved"]), 4)
        r2 = rf.set_text(self.report(), self.text(evidence="Headlines cover the term in two contexts."))
        q2 = rf.approval_queue(r2, os.path.join(self.tmp, "approvals.jsonl"))
        status = rf.approval_status(q2)
        self.assertEqual(len(status["approved"]), 3)  # the unchanged cards stay approved
        self.assertEqual(len(status["open"]), 1)      # the changed signal needs a fresh look

    def test_published_form_is_approved_and_has_no_draft_sections(self):
        pub = rf.published_form(rf.set_text(self.report(), self.text()))
        self.assertEqual((pub["review_status"], pub["ai_assistance"]), ("reviewed", rf.AI_FINAL))
        self.assertNotIn("draft_meta", pub)
        self.assertNotIn("draft_audit", pub["top_signals"][0])


class PrepareRuleTests(unittest.TestCase):
    def test_default_window_is_the_last_closed_monday_to_sunday(self):
        at = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
        self.assertEqual(rp.default_window(at("2026-10-12T04:45:00")), ("2026-10-05", "2026-10-11"))  # Sunday 9:45 pm Pacific
        self.assertEqual(rp.default_window(at("2026-10-11T23:59:00")), ("2026-09-28", "2026-10-04"))  # still open
        self.assertEqual(rp.default_window(at("2026-10-14T12:00:00")), ("2026-10-05", "2026-10-11"))

    def test_not_ready_until_the_window_closes_and_an_ingest_follows(self):
        tmp = tempfile.mkdtemp()
        try:
            paths = rr.Paths(tmp)
            at = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
            self.assertFalse(rp.readiness(paths, "2026-10-05", "2026-10-11", at("2026-10-11T22:00:00"))[0])
            self.assertFalse(rp.readiness(paths, "2026-10-05", "2026-10-11", at("2026-10-12T04:45:00"))[0])  # no ingest log
            with open(paths.ingest_log, "w", encoding="utf-8") as f:
                f.write(json.dumps({"started_at": "2026-10-11T20:30:02Z", "finished_at": "2026-10-11T20:34:00Z"}) + "\n")
            self.assertFalse(rp.readiness(paths, "2026-10-05", "2026-10-11", at("2026-10-12T04:45:00"))[0])  # ingest before the close
            with open(paths.ingest_log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"started_at": "2026-10-12T04:30:02Z", "finished_at": "2026-10-12T04:34:00Z"}) + "\n")
            self.assertTrue(rp.readiness(paths, "2026-10-05", "2026-10-11", at("2026-10-12T04:45:00"))[0])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
