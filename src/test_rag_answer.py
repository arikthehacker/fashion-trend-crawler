"""Tests for ask_ari3 (src/rag_answer.py) with a scripted provider. No network, no key.

usage: python src/test_rag_answer.py
"""

import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import item_store as store  # noqa: E402
import rag_answer as ra  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_index as ri  # noqa: E402
from llm_provider import ProviderError, ScriptedProvider  # noqa: E402
from rag_schema import Filters  # noqa: E402
from test_rag import ITEMS, fake_encoder  # noqa: E402


def claims(*ids, text="Ballet flats were shown in soft leather."):
    return json.dumps({"insufficient_evidence": False, "claims": [{"text": text, "supporting_item_ids": list(ids)}],
                       "limitations": ["Excerpts only."]})


class AskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.db = os.path.join(cls.tmp, "store.db")
        con = store.connect(cls.db)
        store.migrate(con)
        cls.ids = [store.upsert_item(con, url=u, published_at=p, source_method="rss", title=t, fetched_at=f,
                                     text_excerpt=e, lang=lang)[0] for u, p, f, t, e, lang in ITEMS]
        con.commit()
        con.close()
        cls.corpus = rc.open_corpus(cls.db)
        ri.build_index(cls.corpus, os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        cls.index = ri.Index(os.path.join(cls.tmp, "index"), encoder=fake_encoder)
        with open(cls.db, "rb") as f:
            cls.db_bytes = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def ask(self, provider, query="ballet flats", **kw):
        return ra.ask_ari3(query, provider=provider, corpus=self.corpus, index=self.index, **kw)

    def test_grounded_answer_cites_context_with_store_provenance(self):
        a = self.ids[0]
        provider = ScriptedProvider([claims(a)])
        r = self.ask(provider)
        self.assertEqual(r.status, "answered")
        self.assertEqual([c.item_id for c in r.citations], [a])
        self.assertEqual(r.citations[0].url, ITEMS[0][0])  # from the store, not the model
        self.assertEqual(r.temporal_scope.evidence_published_from, ITEMS[0][1])
        prompt = json.loads(provider.calls[0][1]["content"])
        self.assertLessEqual(len(prompt["CONTEXT"]), ra.MAX_CONTEXT_ITEMS)
        self.assertTrue(all(len(c["excerpt"]) <= ra.MAX_EXCERPT_CHARS for c in prompt["CONTEXT"]))
        self.assertNotIn("debug", r.public())
        self.assertEqual(r.debug["prompt_version"], ra.PROMPT_VERSION)

    def test_citation_outside_context_is_rejected_and_withheld(self):
        shop = self.ids[3]
        r = self.ask(ScriptedProvider([claims(shop)]), filters=Filters(languages=["en"]))
        self.assertEqual(r.status, "rejected")
        self.assertEqual(r.claims, [])
        self.assertEqual(r.validation["violations"][0]["reason"], "not_in_context")

    def test_invented_id_is_rejected(self):
        r = self.ask(ScriptedProvider([claims(999999)]))
        self.assertEqual(r.status, "rejected")
        self.assertEqual(r.validation["violations"][0]["reason"], "nonexistent")

    def test_replay_context_never_holds_later_evidence(self):
        a, b, old, shop, ja = self.ids
        provider = ScriptedProvider([claims(a)])
        r = self.ask(provider, as_of="2026-09-24T23:00:00Z", filters=Filters(temporal_mode="replay",
                                                                              as_of="2026-09-24T23:00:00Z"))
        context_ids = [c["item_id"] for c in json.loads(provider.calls[0][1]["content"])["CONTEXT"]]
        self.assertEqual(context_ids, [a])  # the 2021 article was first seen on 2026-09-27
        self.assertEqual(r.status, "answered")
        leak = self.ask(ScriptedProvider([claims(old)]), filters=Filters(temporal_mode="replay",
                                                                          as_of="2026-09-24T23:00:00Z"))
        self.assertEqual(leak.status, "rejected")

    def test_no_evidence_means_no_provider_call(self):
        provider = ScriptedProvider([])
        r = self.ask(provider, filters=Filters(end_date="2010-01-01"))
        self.assertEqual(r.status, "insufficient_evidence")
        self.assertEqual(provider.calls, [])

    def test_model_can_decline(self):
        refusal = json.dumps({"insufficient_evidence": True, "claims": [], "limitations": ["No item covers this."]})
        r = self.ask(ScriptedProvider([refusal]), query="cashmere")
        self.assertEqual(r.status, "insufficient_evidence")
        self.assertEqual(r.limitations, ["No item covers this."])

    def test_schema_failure_gets_one_retry_then_rejects(self):
        a = self.ids[0]
        provider = ScriptedProvider(["not json", claims(a)])
        self.assertEqual(self.ask(provider).status, "answered")
        self.assertEqual(len(provider.calls), 2)
        self.assertIn("did not match", provider.calls[1][-1]["content"])
        r = self.ask(ScriptedProvider(["not json", '{"claims": "x"}']))
        self.assertEqual(r.status, "rejected")
        self.assertFalse(r.validation["schema_valid"])

    def test_provider_error_is_reported_without_answer(self):
        r = self.ask(ScriptedProvider([ProviderError("DeepSeek HTTP 503")]))
        self.assertEqual((r.status, r.message, r.claims), ("error", "DeepSeek HTTP 503", []))

    def test_conflicting_as_of_is_refused(self):
        with self.assertRaises(ValueError):
            self.ask(ScriptedProvider([]), as_of="2026-09-24", filters=Filters(as_of="2026-09-25"))

    def test_nothing_is_written_to_the_store(self):
        self.ask(ScriptedProvider([claims(self.ids[0])]))
        with self.assertRaises(sqlite3.OperationalError):
            self.corpus.execute("INSERT INTO labels (item_id, task, label, source, labeler, split, created_at) "
                                "VALUES (1, 't', 'x', 'human', 'x', 'train', 'x')")
        with open(self.db, "rb") as f:
            self.assertEqual(f.read(), self.db_bytes)


if __name__ == "__main__":
    unittest.main()
