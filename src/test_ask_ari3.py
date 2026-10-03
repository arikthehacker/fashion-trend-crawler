"""Tests for the aligned ask_ari3 (src/rag_answer.py): it must run the Prompt v2 pipeline
evaluated in EXP-005, fail closed on any identity mismatch, and make no live call.
Scripted provider, throwaway corpus, no network.

usage: python src/test_ask_ari3.py
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exp005 as v1  # noqa: E402
import exp005_v2 as v2  # noqa: E402
import item_store as store  # noqa: E402
import rag_answer as ra  # noqa: E402
import rag_answer_exp004 as legacy  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
import rag_select as rs  # noqa: E402
from llm_provider import LiveCallNotAllowed, ScriptedProvider  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402

with open(rs.RETRIEVER_PATH, encoding="utf-8") as _f:
    _FROZEN = json.load(_f)
# The frozen index lives only on the owner's machine. Unit tests stand in its recorded
# fingerprints. test_verify_identity_on_the_real_index checks the real files when present.
FROZEN_FINGERPRINTS = (_FROZEN["code_sha256"], _FROZEN["index_files_sha256"])
QUESTION = "What is said about ballet flats?"


def answer(claims, lims=(), abstain=False, n_claims=None):
    if abstain:
        return json.dumps({"insufficient_evidence": True, "claims": [],
                           "limitations": [{"text": "Nothing in the evidence covers this.", "supporting_item_ids": []}]})
    cl = [{"text": f"Finding {k}.", "supporting_item_ids": list(ids)} for k, ids in enumerate(claims)]
    return json.dumps({"insufficient_evidence": False, "claims": cl,
                       "limitations": [{"text": t, "supporting_item_ids": list(ids)} for t, ids in lims]})


class AskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        db = os.path.join(cls.tmp, "store.db")
        con = store.connect(db)
        store.migrate(con)
        cls.ids = [store.upsert_item(con, url=u, published_at=p, source_method="rss", title=t, fetched_at=f,
                                     text_excerpt=e, lang=lang)[0] for u, p, f, t, e, lang in ITEMS]
        con.commit()
        con.close()
        cls.corpus = rc.open_corpus(db)
        ri.build_index(cls.corpus, os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.index = ri.Index(os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        with open(v2.PROMPT_V2, encoding="utf-8") as f:
            cls.prompt = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.patch = mock.patch.object(ra, "_index_fingerprints", lambda: FROZEN_FINGERPRINTS)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def ask(self, provider, filters=None, query="ballet flats", **kw):
        return ra.ask_ari3(QUESTION, filters, provider=provider, corpus=self.corpus, index=self.index,
                           retrieval_query=query, **kw)

    # 1
    def test_answerable_question_runs_prompt_v2_and_renders_claims(self):
        a = self.ids[0]
        p = ScriptedProvider([answer([[a]])])
        r = self.ask(p)
        self.assertEqual(r["status"], "answered")
        self.assertEqual(p.calls[0][0], {"role": "system", "content": self.prompt})
        self.assertTrue(r["retrieval"]["item_ids"])
        self.assertEqual(r["rendered_answer"], "Finding 0.")
        self.assertEqual([c["item_id"] for c in r["citations"]], [a])
        self.assertEqual(r["pipeline"]["prompt_v2_sha256"], ra.EXPECTED["prompt_v2_sha256"])
        self.assertTrue(r["validation"]["valid"])

    # 2
    def test_abstention_keeps_the_evaluated_structure(self):
        p = ScriptedProvider([answer([], abstain=True)])
        r = self.ask(p)
        self.assertEqual((r["status"], r["abstained"], r["rendered_answer"]), ("model_abstention", True, ""))
        self.assertTrue(r["answer"]["insufficient_evidence"])
        self.assertEqual(r["answer"]["claims"], [])
        self.assertEqual(len(p.calls), 1)  # an abstention is never retried

    # 3
    def test_citation_outside_the_packet_is_rejected_and_withheld(self):
        r = self.ask(ScriptedProvider([answer([[self.ids[3]]])]), filters={"languages": ["en"]})
        self.assertEqual(r["status"], "rejected_citation")
        self.assertIsNone(r["answer"])
        self.assertEqual(r["rendered_answer"], "")

    # 4
    def test_nonexistent_item_id_is_rejected(self):
        r = self.ask(ScriptedProvider([answer([[99999]])]))
        self.assertEqual(r["status"], "rejected_citation")
        reasons = {v["reason"] for v in r["audit"]["validation"]["violations"]}
        self.assertIn("nonexistent", reasons)

    # 5
    def test_filter_violation_cannot_be_cited(self):
        r = self.ask(ScriptedProvider([answer([[self.ids[0]], [self.ids[4]]])]), filters={"languages": ["en"]})
        self.assertNotIn(self.ids[4], r["retrieval"]["item_ids"])  # the Japanese item is outside the packet
        self.assertEqual(r["status"], "rejected_citation")

    # 6
    def test_too_many_claims_follow_the_frozen_schema_and_retry(self):
        five = answer([[self.ids[0]]] * 5)
        p = ScriptedProvider([five, five])
        r = self.ask(p)
        self.assertEqual((r["status"], r["attempts"], r["schema_retries"]), ("rejected_schema", 2, 1))
        self.assertIsNone(r["answer"])

    # 7
    def test_limitations_follow_frozen_v2_validation(self):
        a, shop = self.ids[0], self.ids[3]
        # An uncited limitation is allowed by schema v2. Whether it states an item-specific fact
        # is a human-review judgment in the evaluated pipeline, not a deterministic check.
        ok = self.ask(ScriptedProvider([answer([[a]], lims=[("Evidence is sparse.", [])])]))
        self.assertEqual(ok["status"], "answered")
        # A limitation that cites an item outside the packet fails deterministic validation.
        bad = self.ask(ScriptedProvider([answer([[a]], lims=[("Item note.", [shop])])]), filters={"languages": ["en"]})
        self.assertEqual(bad["status"], "rejected_citation")
        self.assertIn("limitation 0", {v["where"] for v in bad["audit"]["validation"]["violations"]})

    # 8
    def test_malformed_output_gets_one_retry_with_the_parser_error(self):
        p = ScriptedProvider(["not json", answer([[self.ids[0]]])])
        r = self.ask(p)
        self.assertEqual((r["status"], len(p.calls)), ("answered", 2))
        self.assertIn("did not match the required JSON format", p.calls[1][-1]["content"])

    # 9
    def test_identity_mismatch_fails_closed_before_retrieval_or_any_call(self):
        p = ScriptedProvider([answer([[self.ids[0]]])])
        bad = os.path.join(self.tmp, "prompt_v2_modified.txt")
        with open(bad, "w", encoding="utf-8") as f:
            f.write(self.prompt + "\nBe helpful.")
        with mock.patch.object(v2, "PROMPT_V2", bad), mock.patch("rag_eval.run_method") as retrieval:
            with self.assertRaises(ra.PipelineIdentityError):
                self.ask(p)
        retrieval.assert_not_called()
        self.assertEqual(p.calls, [])
        with mock.patch.object(ra, "_index_fingerprints",
                               lambda: (FROZEN_FINGERPRINTS[0], dict(FROZEN_FINGERPRINTS[1], **{"fts.db": "0" * 64}))):
            with self.assertRaises(ra.PipelineIdentityError) as e:
                self.ask(p)
        self.assertIn("index", str(e.exception))
        with mock.patch.object(ra, "_schema_sha", lambda: "1" * 64):
            with self.assertRaises(ra.PipelineIdentityError):
                self.ask(p)
        self.assertEqual(p.calls, [])

    # 10
    def test_renderer_writes_no_summary_of_its_own(self):
        a, b = self.ids[0], self.ids[2]
        r = self.ask(ScriptedProvider([answer([[a], [b]])]))
        self.assertEqual(r["rendered_answer"], "Finding 0. Finding 1.")
        self.assertNotIn("answer_summary", r["answer"])
        with_summary = json.dumps({"insufficient_evidence": False, "answer_summary": {"text": "s", "supporting_item_ids": [a]},
                                   "claims": [{"text": "x", "supporting_item_ids": [a]}]})
        self.assertEqual(self.ask(ScriptedProvider([with_summary, with_summary]))["status"], "rejected_schema")

    # 11
    def test_context_packet_is_the_evaluated_serializer_output(self):
        p = ScriptedProvider([answer([[self.ids[0]]])])
        r = self.ask(p)
        payload = json.loads(p.calls[0][1]["content"])
        from rag_schema import Filters
        expected = v1.serialize_context(rc.get_items(self.corpus, r["retrieval"]["item_ids"]),
                                        Filters(**r["audit"]["filters"]))
        self.assertEqual(payload["evidence"], expected)
        self.assertEqual(r["context_sha256"], hashlib.sha256(json.dumps(expected, ensure_ascii=False).encode()).hexdigest())
        self.assertEqual(set(payload), {"question", "constraints", "evidence"})
        self.assertEqual(payload["question"], QUESTION)
        self.assertEqual(list(expected[0]), ["item_id", "outlet", "sector_group", "published_at", "language",
                                             "headline", "excerpt", "url"])

    # 12
    def test_the_old_exp004_path_is_not_reachable(self):
        with open(ra.__file__, encoding="utf-8") as f:
            src = f.read()
        for marker in ("SYSTEM_PROMPT", "GroundedAnswer", "validate_answer", "exp004-prompt-v1", "import rag_answer_exp004"):
            self.assertNotIn(marker, src)
        p = ScriptedProvider([answer([[self.ids[0]]])])
        self.ask(p)
        self.assertNotEqual(p.calls[0][0]["content"], legacy.SYSTEM_PROMPT)
        self.assertNotIn("CONTEXT", json.loads(p.calls[0][1]["content"]))

    # live-call guard
    def test_default_path_makes_no_live_call(self):
        with self.assertRaises(LiveCallNotAllowed):
            ra.ask_ari3(QUESTION, corpus=self.corpus, index=self.index)

    def test_a_non_scripted_provider_needs_allow_live(self):
        class Live:
            name = "deepseek"

            def generate_json(self, messages):
                raise AssertionError("a live provider was called")
        with self.assertRaises(LiveCallNotAllowed):
            self.ask(Live())

    def test_allow_live_still_needs_the_adapter_gate(self):
        with mock.patch.dict(os.environ, {}, clear=False), mock.patch("requests.Session.post") as post:
            os.environ.pop("ARI3_LIVE_LLM", None)
            r = ra.ask_ari3(QUESTION, corpus=self.corpus, index=self.index, retrieval_query="ballet flats",
                            allow_live=True)
        post.assert_not_called()
        self.assertEqual(r["status"], "provider_error")
        self.assertIn("LiveCallNotAllowed", r["audit"]["error"])

    def test_identity_is_checked_before_a_live_call(self):
        with mock.patch.object(ra, "_schema_sha", lambda: "1" * 64), mock.patch("requests.Session.post") as post:
            with self.assertRaises(ra.PipelineIdentityError):
                ra.ask_ari3(QUESTION, corpus=self.corpus, index=self.index, allow_live=True)
        post.assert_not_called()


class RealIdentityTests(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(os.path.join(rs.INDEX_DIR, "fts.db")), "the frozen index is local only")
    def test_verify_identity_on_the_real_index(self):
        identity = ra.verify_identity()
        self.assertEqual(identity["index_cutoff_first_seen_at"], "2026-09-30T08:00:00Z")
        self.assertEqual(identity["limits"]["claims"], 4)

    def test_code_and_settings_identity_in_any_checkout(self):
        with mock.patch.object(ra, "_index_fingerprints", lambda: FROZEN_FINGERPRINTS):
            identity = ra.verify_identity()
        self.assertEqual(identity["limits"], {"context_items": 10, "headline_chars": 300, "excerpt_chars": 500,
                                              "context_chars": 12000, "claims": 4, "attempts": 2})


if __name__ == "__main__":
    unittest.main()
