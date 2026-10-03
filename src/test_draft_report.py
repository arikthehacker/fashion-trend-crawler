"""Tests for the deterministic report drafter (src/draft_report.py). Throwaway store, no
network, no model.

usage: python src/test_draft_report.py
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import draft_report as dr  # noqa: E402
import item_store as store  # noqa: E402
import lexicon  # noqa: E402
from validate_all_reports import publish_gate_errors  # noqa: E402

YES, NO, UNSURE = '["yes"]', '["no"]', '["yes", "no"]'


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "s.db")
        con = store.connect(self.db)
        store.migrate(con)
        con.execute("INSERT INTO lexicon_versions (lexicon_version, created_at, note) VALUES (1, 'x', 'v1')")
        for term, kind, flag in (("corset", "garment_silhouette", 0), ("lace", "material", 1), ("boho", "aesthetic_term", 0)):
            con.execute("INSERT INTO terms (term_id, canonical, signal_type, introduced_in) VALUES (?,?,?,1)", (term, term, kind))
            con.execute("INSERT INTO term_variants (term_id, variant, lexicon_version) VALUES (?,?,1)", (term, term))
            con.execute("INSERT INTO term_rules (term_id, needs_sense_check, decided_at) VALUES (?,?,'x')", (term, flag))
        rows = [  # url, published, title, prediction set
            ("https://a.example/1", "2026-09-29T10:00:00Z", "A corset and lace look", YES),
            ("https://b.example/2", "2026-09-30T10:00:00Z", "Corset dresses return", YES),
            ("https://b.example/3", "2026-10-01T10:00:00Z", "Another corset", UNSURE),
            ("https://c.example/4", "2026-10-01T11:00:00Z", "Corset earnings", NO),
            ("https://a.example/5", "2026-10-02T10:00:00Z", "Boho at one outlet", YES),
            ("https://a.example/6", "2026-10-02T11:00:00Z", "More boho at the same outlet", YES),
            ("https://d.example/7", "2026-09-20T10:00:00Z", "Corset outside the window", YES),
            ("https://d.example/8", "2026-10-03T10:00:00Z", "Lace everywhere", YES),
            ("https://e.example/9", "2026-10-03T12:00:00Z", "Lace again", YES),
        ]
        for url, pub, title, cset in rows:
            item_id, _ = store.upsert_item(con, url=url, published_at=pub, source_method="rss", title=title,
                                           fetched_at="2026-10-03T13:00:00Z", text_excerpt="", lang="en")
            con.execute("INSERT INTO label_predictions (item_id, task, model_version, predicted_label, probability, "
                        "calibrated_probability, conformal_set, created_at) VALUES (?,?,?,?,?,?,?,?)",
                        (item_id, "is_style_signal", "ari3-v0.0.2", "yes", None, 0.9, cset, "2026-10-03T14:00:00Z"))
        con.commit()
        with contextlib.redirect_stdout(io.StringIO()):
            lexicon.cmd_extract(con)
        con.close()
        from rag_corpus import open_corpus
        self.con = open_corpus(self.db)

    def tearDown(self):
        self.con.close()
        shutil.rmtree(self.tmp)

    def draft(self, now="2026-10-05T01:00:00Z"):
        return dr.build_draft(self.con, "2026-09-28", "2026-10-04", now=now)

    def test_only_confident_yes_counts_and_ambiguous_terms_stay_out(self):
        r = self.draft()
        ids = [s["signal_id"] for s in r["top_signals"]]
        self.assertEqual(ids, ["corset"])  # boho: one outlet only; lace: held out for a sense check
        corset = r["top_signals"][0]
        self.assertEqual(sorted(e["item_id"] for e in corset["evidence_items"]), [1, 2])
        audit = corset["draft_audit"]
        self.assertEqual((audit["not_sure_items_with_term"], audit["not_style_items_with_term"]), ([3], [4]))
        self.assertEqual(sum(audit["items_by_sector"].values()), 2)
        table = {t["term_id"]: t for t in r["draft_meta"]["term_table"]}
        self.assertTrue(table["lace"]["excluded_by_sense_check"])
        self.assertFalse(table["lace"]["meets_candidate_rule"])
        self.assertFalse(table["boho"]["meets_candidate_rule"])
        self.assertEqual(r["items_collected"], 8)  # item 7 is outside the window

    def test_evidence_comes_from_the_store_with_provenance(self):
        e = self.draft()["top_signals"][0]["evidence_items"][0]
        for k in ("item_id", "url", "title", "outlet_domain", "sector", "published_at", "retrieved_at",
                  "first_seen_at", "first_seen_basis", "content_hash", "style_set", "p_style", "terms"):
            self.assertIn(k, e)
        self.assertEqual(e["style_set"], ["yes"])
        self.assertEqual(e["first_seen_basis"], "live_insert")

    def test_no_prose_and_draft_status(self):
        r = self.draft()
        self.assertEqual((r["review_status"], r["executive_summary"]), ("draft", ""))
        s = r["top_signals"][0]
        self.assertEqual((s["evidence"], s["index_note"], s["human_editor_note"], s["volatility"]), ("", "", "", ""))
        self.assertNotIn("ai_assistance", r)
        text = json.dumps(r).lower()
        for word in ("rising", "emerging", "dominant", "breakout"):
            self.assertNotIn(word, text)

    def test_limitations_state_the_exp003a_result_precisely(self):
        lims = " ".join(self.draft()["limitations"])
        self.assertIn("prospective holdout", lims)
        self.assertIn("0.833", lims)
        self.assertIn("0.85", lims)
        self.assertIn("editor reviews every evidence item", lims)

    def test_not_sure_share_is_disclosed_from_the_window(self):
        lims = self.draft()["limitations"]
        self.assertIn("In this window, 1 of 8 items (12.5%) received a not-sure prediction set and were excluded "
                      "from style-positive counts.", lims)

    def test_window_completion_uses_the_half_open_end(self):
        self.assertFalse(self.draft(now="2026-10-04T23:59:59Z")["draft_meta"]["window_complete"])
        self.assertTrue(self.draft(now="2026-10-05T00:00:00Z")["draft_meta"]["window_complete"])

    def test_incomplete_window_is_marked(self):
        r = self.draft(now="2026-10-03T07:00:00Z")
        self.assertFalse(r["draft_meta"]["window_complete"])
        self.assertTrue(any("DRAFT ONLY" in l for l in r["limitations"]))

    def test_draft_fails_the_publication_gate(self):
        r = self.draft()
        errors = publish_gate_errors(r, "2026-10-05", None, None)
        self.assertTrue(any("review_status" in e for e in errors))
        self.assertTrue(any("human_editor_note" in e for e in errors))
        self.assertTrue(any("evidence review snapshot missing" in e for e in errors))

    def test_drafter_never_writes_to_the_store(self):
        before = os.path.getmtime(self.db), os.path.getsize(self.db)
        self.draft()
        self.assertEqual(before, (os.path.getmtime(self.db), os.path.getsize(self.db)))

    def test_review_markdown_lists_every_candidate_and_held_out_term(self):
        md = dr.review_markdown(self.draft())
        self.assertIn("corset", md)
        self.assertIn("| lace |", md)
        self.assertIn("Editor decision: [ ] keep", md)


if __name__ == "__main__":
    unittest.main()
