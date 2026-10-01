"""Tests for the EXP-004 retrieval layer (rag_*.py). No network, no model download and
no API key: a small hashing encoder stands in for the sentence encoder.

usage: python src/test_rag.py
"""

import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import item_store as store  # noqa: E402
import rag_corpus as rc  # noqa: E402
import rag_eval as ev  # noqa: E402
import rag_index as ri  # noqa: E402
import rag_retrieve as rr  # noqa: E402
import rag_tools as rt  # noqa: E402
import rag_validate as rv  # noqa: E402
from rag_schema import Filters, GroundedAnswer, SearchArgs  # noqa: E402


def fake_encoder(texts):
    """Bag of words hashed into 64 dimensions, L2-normalized. Deterministic."""
    out = np.zeros((len(texts), 64), dtype="float32")
    for n, text in enumerate(texts):
        for word in re.findall(r"\w+", text.lower()):
            out[n, int(hashlib.md5(word.encode()).hexdigest(), 16) % 64] += 1.0
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.where(norms == 0, 1, norms)


ITEMS = [  # (url, published_at, fetched_at, title, excerpt, lang)
    ("https://www.vogue.com/article/ballet-flats-return", "2026-09-24T10:00:00Z", "2026-09-24T12:00:00Z",
     "Ballet flats return", "Designers showed ballet flats in soft leather.", "en-us"),
    ("https://www.vogue.com/article/quiet-luxury-cashmere", "2026-09-25T10:00:00Z", "2026-09-25T12:00:00Z",
     "Quiet luxury and cashmere", "Quiet luxury tailoring in cashmere.", "en"),
    ("https://www.vogue.com/article/old-ballet-flats", "2021-03-01T10:00:00Z", "2026-09-27T12:00:00Z",
     "Ballet flats in 2021", "An older article about ballet flats, collected later.", "en"),
    ("https://fixture-shop.example/news/cashmere-sale", "2026-09-26T10:00:00Z", "2026-09-26T12:00:00Z",
     "Cashmere knitwear arrives", "Cashmere knitwear in store.", None),
    ("https://www.vogue.co.jp/article/ballet-shoes", "2026-09-26T09:00:00Z", "2026-09-26T12:00:00Z",
     "バレエシューズの人気", "バレエシューズが再び注目されている。", "ja"),
]


class RagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.db = os.path.join(cls.tmp, "store.db")
        con = store.connect(cls.db)
        store.migrate(con)
        cls.ids = []
        for url, pub, fet, title, ex, lang in ITEMS:
            cls.ids.append(store.upsert_item(con, url=url, published_at=pub, source_method="rss", title=title,
                                             fetched_at=fet, text_excerpt=ex, lang=lang)[0])
        con.execute("UPDATE outlet_sector_history SET sector_id='retail' WHERE outlet_id="
                    "(SELECT outlet_id FROM outlets WHERE domain='fixture-shop.example')")
        con.commit()
        con.close()
        cls.corpus = rc.open_corpus(cls.db)
        cls.index_dir = os.path.join(cls.tmp, "index")
        cls.manifest = ri.build_index(cls.corpus, cls.index_dir, encoder=fake_encoder)
        cls.index = ri.Index(cls.index_dir, encoder=fake_encoder)

    @classmethod
    def tearDownClass(cls):
        cls.corpus.close()
        cls.index.fts.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def search(self, query, method="hybrid", k=10, lexical="auto", **filters):
        args = SearchArgs(query=query, method=method, k=k, filters=Filters(**filters))
        return [h.evidence.item_id for h in rr.search(self.corpus, self.index, args, lexical).hits]

    # ---- the store stays read-only ----

    def test_corpus_connection_is_read_only(self):
        with self.assertRaises(sqlite3.OperationalError):
            self.corpus.execute("UPDATE items SET title='x'")
        with self.assertRaises(sqlite3.OperationalError):
            self.corpus.execute("CREATE TABLE scratch (x)")

    # ---- deterministic filters ----

    def test_date_filters(self):
        a, b, old, shop, ja = self.ids
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(start_date="2026-09-25", end_date="2026-09-25")), [b])
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(start_date="2026-09-26")), [shop, ja])

    def test_publication_and_replay_cutoffs(self):
        a, b, old, shop, ja = self.ids
        pub = rc.eligible_ids(self.corpus, Filters(as_of="2026-09-24T23:00:00Z"))
        replay = rc.eligible_ids(self.corpus, Filters(as_of="2026-09-24T23:00:00Z", temporal_mode="replay"))
        self.assertEqual(pub, [a, old])  # the 2021 article was published by then
        self.assertEqual(replay, [a])  # but ARI3 first saw it on 2026-09-27
        with self.assertRaises(ValueError):
            Filters(temporal_mode="replay")

    def test_language_sector_and_outlet_filters(self):
        a, b, old, shop, ja = self.ids
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(languages=["ja"])), [ja])
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(coarse_groups=["retail"])), [shop])
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(sectors=["retail"])), [shop])
        self.assertEqual(rc.eligible_ids(self.corpus, Filters(outlets=["vogue.co.jp"])), [ja])

    def test_filters_override_similarity(self):
        a, b, old, shop, ja = self.ids
        for method in ("bm25", "dense", "hybrid"):
            got = self.search("ballet flats", method=method, start_date="2026-09-01", end_date="2026-09-23")
            self.assertEqual(got, [], method)
            got = self.search("ballet flats", method=method, start_date="2026-09-01", languages=["en"])
            self.assertNotIn(old, got, method)

    def test_sql_is_parameterized(self):
        hostile = "x' OR '1'='1"
        with self.assertRaises(ValueError):
            Filters(outlets=[hostile])
        f = Filters(start_date="2026-09-25", outlets=["vogue.com"], languages=["en"])
        sql, params = rc.where_clause(f)
        for value in ("2026-09-25T00:00:00Z", "vogue.com", "en"):
            self.assertNotIn(value, sql)
            self.assertIn(value, params)
        for query in (hostile, '"NEAR(ballet flats) OR *', "flats; DROP TABLE items; --", "   ?!  "):
            self.search(query, method="bm25")  # never raises, never treated as syntax
        self.assertEqual(rc.eligible_ids(self.corpus, Filters()), self.ids)

    # ---- ranking ----

    def test_methods_rank_relevant_items_first_and_deterministically(self):
        a, b, old, shop, ja = self.ids
        self.assertEqual(self.search("quiet luxury", method="bm25")[0], b)
        self.assertEqual(self.search("quiet luxury cashmere", method="dense")[0], b)
        self.assertEqual(set(self.search("ballet flats", method="bm25")[:2]), {a, old})
        self.assertEqual(self.search("cashmere"), self.search("cashmere"))
        self.assertEqual(rr.rrf([[(1, 9.0), (2, 8.0)], [(2, 0.9), (3, 0.8)]], 3)[0][0], 2)

    def test_japanese_query_uses_trigrams(self):
        a, b, old, shop, ja = self.ids
        self.assertEqual(rr.lexical_mode("バレエシューズ"), "trigram")
        self.assertEqual(self.search("バレエシューズ", method="bm25"), [ja])
        self.assertEqual(self.search("バレエシューズ", method="bm25", lexical="words"), [])

    def test_search_result_carries_provenance(self):
        args = SearchArgs(query="cashmere", k=3)
        result = rr.search(self.corpus, self.index, args)
        hit = result.hits[0]
        self.assertTrue(hit.evidence.url.startswith("https://"))
        self.assertEqual(hit.evidence.first_seen_basis, "live_insert")
        self.assertEqual(result.corpus_fingerprint, self.manifest["corpus_fingerprint"])
        self.assertIn("bm25", hit.ranks_by_method)

    def test_index_reuses_cached_embeddings(self):
        copy = os.path.join(self.tmp, "index-copy")  # the loaded index keeps fts.db open
        shutil.copytree(self.index_dir, copy)
        again = ri.build_index(self.corpus, copy, encoder=fake_encoder)
        self.assertEqual(again["encoded_this_build"], 0)
        self.assertEqual(again["corpus_fingerprint"], self.manifest["corpus_fingerprint"])
        cut = ri.build_index(self.corpus, os.path.join(self.tmp, "cut"), encoder=fake_encoder,
                             cutoff="2026-09-25T23:00:00Z")
        self.assertEqual(cut["items"], 2)

    # ---- tools ----

    def test_tools_validate_arguments(self):
        tools = rt.Tools(self.db, self.index_dir, encoder=fake_encoder)
        self.assertTrue(tools.search_articles({"query": "cashmere", "k": 2}).hits)
        bad = [{"query": "x", "k": 0}, {"query": "x", "k": 51}, {"query": "x", "k": "5"},
               {"query": "", "k": 5}, {"query": "x", "limit": 5}, {"query": "x", "filters": {"as_of": "yesterday"}},
               {"query": "x", "filters": {"temporal_mode": "replay"}}, {"query": "x", "method": "sql"},
               {"query": "x", "filters": {"sectors": ["editorial'; --"]}}, ["not", "an", "object"]]
        for arguments in bad:
            with self.assertRaises(rt.ToolError, msg=str(arguments)):
                tools.search_articles(arguments)
        self.assertEqual(tools.get_article({"item_id": self.ids[0]}).item_id, self.ids[0])
        for arguments in ({"item_id": 999999}, {"item_id": "1"}, {"item_id": 0}):
            with self.assertRaises(rt.ToolError):
                tools.get_article(arguments)
        with self.assertRaises(rt.ToolError):
            tools.call("run_sql", {"sql": "SELECT 1"})
        self.assertEqual([t["name"] for t in rt.TOOL_DEFINITIONS], ["search_articles", "get_article"])

    def test_retrieval_needs_no_api_key(self):
        saved = {k: os.environ.pop(k) for k in list(os.environ) if k.endswith("_API_KEY")}
        try:
            self.assertTrue(self.search("cashmere"))
        finally:
            os.environ.update(saved)

    # ---- citation validation ----

    def answer(self, *cited, refuse=False):
        if refuse:
            return json.dumps({"insufficient_evidence": True, "claims": [], "limitations": ["Nothing on this."]})
        return json.dumps({"insufficient_evidence": False,
                           "claims": [{"text": "A claim.", "supporting_item_ids": list(cited)}]})

    def test_citation_checks(self):
        a, b, old, shop, ja = self.ids
        f = Filters(as_of="2026-09-25T23:00:00Z", temporal_mode="replay")
        context = [a, b, old]
        self.assertTrue(rv.validate_answer(self.corpus, self.answer(a, b), context, f)["valid"])
        cases = {999999: "nonexistent", shop: "not_in_context", old: "first_seen_after_as_of"}
        for item_id, reason in cases.items():
            report = rv.validate_answer(self.corpus, self.answer(a, item_id), context, f)
            self.assertFalse(report["valid"])
            self.assertEqual(report["violations"], [{"claim": 0, "item_id": item_id, "reason": reason}])
        self.assertEqual(rv.validate_answer(self.corpus, self.answer(old), context, f)["temporal_leaks"], [old])
        lang = Filters(languages=["en"])
        self.assertEqual(rv.validate_answer(self.corpus, self.answer(ja), [ja], lang)["violations"],
                         [{"claim": 0, "item_id": ja, "reason": "fails_filters"}])
        pub = Filters(as_of="2026-09-24T23:00:00Z")
        self.assertEqual(rv.validate_answer(self.corpus, self.answer(b), [b], pub)["violations"][0]["reason"],
                         "published_after_as_of")

    def test_context_validation_catches_future_and_filtered_items(self):
        a, b, old, shop, ja = self.ids
        f = Filters(as_of="2026-09-24T23:00:00Z", temporal_mode="replay")
        self.assertEqual(rv.validate_context(self.corpus, [a], f), [])
        self.assertEqual({v["reason"] for v in rv.validate_context(self.corpus, [b, old, 999999], f)},
                         {"published_after_as_of", "first_seen_after_as_of", "nonexistent"})

    def test_malformed_answers_are_rejected(self):
        for raw in ("not json",
                    json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": []}]}),
                    json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": ["1"]}]}),
                    json.dumps({"insufficient_evidence": True, "claims": [{"text": "x", "supporting_item_ids": [1]}]}),
                    json.dumps({"insufficient_evidence": False, "claims": []}),
                    json.dumps({"insufficient_evidence": True, "claims": [], "answer": "free prose"}),
                    json.dumps({"insufficient_evidence": False, "claims": [{"text": "x", "supporting_item_ids": [1],
                                                                            "url": "https://made.up"}]}),
                    json.dumps({"insufficient_evidence": True, "limitations": ["x" * 301]})):
            report = rv.validate_answer(self.corpus, raw, self.ids, Filters())
            self.assertFalse(report["valid"], raw)
            self.assertFalse(report["schema_valid"], raw)
        refusal = rv.validate_answer(self.corpus, self.answer(refuse=True), self.ids, Filters())
        self.assertTrue(refusal["valid"])
        self.assertTrue(refusal["insufficient_evidence"])
        self.assertIsInstance(GroundedAnswer.model_validate_json(self.answer(refuse=True)), GroundedAnswer)


class EvalTests(unittest.TestCase):
    def test_metrics(self):
        ranked, rel = [5, 3, 9, 1], {3, 1, 7}
        self.assertEqual(ev.hit_at(ranked, rel, 1), 0.0)
        self.assertEqual(ev.hit_at(ranked, rel, 2), 1.0)
        self.assertAlmostEqual(ev.recall_at(ranked, rel, 4), 2 / 3)
        self.assertEqual(ev.mrr(ranked, rel), 0.5)
        self.assertAlmostEqual(ev.ndcg_at([3, 1, 7], rel, 10), 1.0)

    def judgment(self, item, value, at, qid="q001"):
        return ev.Judgment(task="rag_relevance", dataset_version="v1", pool_sha256="a" * 64, question_id=qid,
                           item_id=item, url="https://x.example/a", judgment=value, labeler="ariella", judged_at=at)

    def test_latest_judgment_wins_and_unsure_is_not_negative(self):
        js = [self.judgment(1, "relevant", "2026-10-01T00:00:00Z"), self.judgment(1, "not_relevant", "2026-10-01T00:05:00Z"),
              self.judgment(2, "relevant", "2026-10-01T00:01:00Z"), self.judgment(3, "unsure", "2026-10-01T00:02:00Z")]
        self.assertEqual(ev.gold(js), {"q001": {2}})
        self.assertEqual(ev.judgments_by_question(js), {"q001": {1: "not_relevant", 2: "relevant", 3: "unsure"}})

    def test_gold_freeze_requires_exactly_the_pool(self):
        pool = [{"question_id": "q001", "item_id": 1}, {"question_id": "q001", "item_id": 2}]
        js = [self.judgment(1, "relevant", "2026-10-01T00:00:00Z"), self.judgment(1, "unsure", "2026-10-01T00:03:00Z"),
              self.judgment(2, "not_relevant", "2026-10-01T00:01:00Z")]
        gold = ev.materialize_gold(js, pool, "a" * 64)
        self.assertEqual([(j.item_id, j.judgment) for j in gold], [(1, "unsure"), (2, "not_relevant")])
        with self.assertRaises(RuntimeError):  # a pooled pair is unjudged
            ev.materialize_gold(js[:2], pool, "a" * 64)
        with self.assertRaises(RuntimeError):  # a pair outside the pool
            ev.materialize_gold(js + [self.judgment(3, "relevant", "2026-10-01T00:04:00Z")], pool, "a" * 64)
        with self.assertRaises(RuntimeError):  # judgments for another pool
            ev.materialize_gold(js, pool, "b" * 64)
        with self.assertRaises(RuntimeError):  # two different answers in the same second
            ev.materialize_gold(js + [self.judgment(2, "relevant", "2026-10-01T00:01:00Z")], pool, "a" * 64)

    def test_condensed_lists_drop_unsure_items(self):
        judged = {"q001": {3: "unsure", 1: "not_relevant", 2: "relevant"}, "q002": {9: "not_relevant"}}
        out = ev.score({"q001": [3, 1, 2], "q002": [9]}, judged)
        self.assertEqual(out["questions_scored"], 1)
        self.assertEqual(out["questions_without_relevant"], 1)
        self.assertEqual(out["mrr"], 0.5)  # rank 2 once the unsure item is removed, not rank 3
        self.assertAlmostEqual(out["unresolved_share_top10"], (1 / 3 + 0) / 2, places=3)
        self.assertEqual(out["judged_coverage_top10"], 1.0)

    def test_pool_stats_and_fingerprint(self):
        q = lambda qid: ev.Question(question_id=qid, question="A question?", query="q", answerable_expected=True,
                                    language="en", query_type="term", reference_time="2026-09-30T00:00:00Z",
                                    dataset_version="v1", drafted_by="test")
        rows = [{"question_id": "q001", "item_id": 1, "pool_source": ["bm25:words", "dense"]},
                {"question_id": "q001", "item_id": 2, "pool_source": ["dense"]}]
        stats = ev.pool_stats(rows, [q("q001"), q("q002")], methods=(("bm25", "words"), ("dense", None)))
        self.assertEqual((stats["pairs"], stats["unique_items"], stats["questions_with_zero_candidates"]), (2, 2, 1))
        self.assertEqual(stats["pairs_found_by_n_methods"], {1: 1, 2: 1})
        self.assertEqual(stats["jaccard_overlap"]["bm25:words & dense"], 0.5)
        self.assertEqual(ev.pool_fingerprint(rows), ev.pool_fingerprint(list(reversed(rows))))

    def test_file_fingerprint_ignores_line_endings(self):
        tmp = tempfile.mkdtemp()
        try:
            lf, crlf = os.path.join(tmp, "lf.jsonl"), os.path.join(tmp, "crlf.jsonl")
            with open(lf, "wb") as f:
                f.write(b'{"a": 1}\n{"b": 2}\n')
            with open(crlf, "wb") as f:
                f.write(b'{"a": 1}\r\n{"b": 2}\r\n')
            self.assertEqual(ev.sha256_file(lf), ev.sha256_file(crlf))
        finally:
            shutil.rmtree(tmp)

    def test_split_is_stratified_deterministic_disjoint_and_guarded(self):
        qs = []
        for n in range(60):
            qs.append(ev.Question(question_id=f"q{n:03d}", question="A question?", query="q",
                                  answerable_expected=n % 6 != 0, language="ja" if n % 10 == 0 else "en",
                                  query_type=ev.QUERY_TYPES[n % 3],
                                  filters=Filters(as_of="2026-09-28") if n % 4 == 0 else Filters(),
                                  reference_time="2026-09-30T00:00:00Z", dataset_version="v1", drafted_by="test"))
        first, second = ev.freeze_split(qs, "abc"), ev.freeze_split(qs, "abc")
        self.assertEqual(first, second)
        self.assertEqual((first["n_dev"], first["n_test"]), (40, 20))
        self.assertFalse(set(first["dev"]) & set(first["test"]))
        unanswerable_test = sum(1 for q in qs if q.question_id in first["test"] and not q.answerable_expected)
        self.assertGreaterEqual(unanswerable_test, 3)
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "split.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(first, f)
            self.assertEqual(ev.load_split("abc", path)["test"], first["test"])
            with self.assertRaises(RuntimeError):
                ev.load_split("changed", path)
            tampered = dict(first, test=first["test"][:-1] + [first["dev"][0]])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(tampered, f)
            with self.assertRaises(RuntimeError):
                ev.load_split("abc", path)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
