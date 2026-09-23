"""Offline tests for src/ingest_rss.py (no network).

usage: python src/test_ingest_rss.py
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ingest_rss  # noqa: E402
import item_store as store  # noqa: E402

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>
  <item><title>Dated item</title><link>https://www.vogue.com/article/dated-item</link>
        <pubDate>Fri, 18 Sep 2026 14:30:00 -0400</pubDate><description>Summary.</description></item>
  <item><title>dc:date item</title><link>https://www.vogue.com/article/dc-item</link>
        <dc:date>2026-09-17T09:00:00Z</dc:date></item>
  <item><title>Undated item</title><link>https://www.vogue.com/article/undated</link></item>
  <item><title>Future item</title><link>https://www.vogue.com/article/future</link>
        <pubDate>Thu, 01 Jan 2099 00:00:00 +0000</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>Atom entry</title>
    <link rel="alternate" href="/2026/09/atom-entry"/><link rel="replies" href="/comments"/>
    <published>2026-09-16T08:00:00+02:00</published></entry>
  <entry><title>Updated only</title><link href="https://example.org/updated-only"/>
    <updated>2026-09-15T12:00:00Z</updated></entry>
</feed>"""

HTML = """<html><head>
<link rel="alternate" type="application/rss+xml" title="All" href="/feed/">
<link rel="alternate" type="application/rss+xml" title="Comments" href="/comments/feed/">
<link rel="stylesheet" href="/style.css">
</head></html>"""


class FakeResp:
    def __init__(self, text, status=200):
        self.text, self.status_code, self.url = text, status, ""


class IngestTests(unittest.TestCase):
    def test_rss_dates_normalised_to_utc(self):
        e = {x["title"]: x for x in ingest_rss.parse_feed(RSS, "https://www.vogue.com/feed")}
        self.assertEqual(e["Dated item"]["published_at"], "2026-09-18T18:30:00Z")
        self.assertEqual(e["dc:date item"]["published_at"], "2026-09-17T09:00:00Z")
        self.assertIsNone(e["Undated item"]["published_at"])

    def test_atom_links_and_dates(self):
        e = ingest_rss.parse_feed(ATOM, "https://example.org/atom.xml")
        self.assertEqual(e[0]["url"], "https://example.org/2026/09/atom-entry")
        self.assertEqual(e[0]["published_at"], "2026-09-16T06:00:00Z")
        self.assertEqual(e[1]["published_at"], "2026-09-15T12:00:00Z")

    def test_autodiscovery_skips_comment_feeds(self):
        self.assertEqual(ingest_rss.autodiscover(HTML, "https://site.example/"),
                         ["https://site.example/feed/"])

    def test_ingest_skips_undated_and_future_and_is_idempotent(self):
        con = store.connect(":memory:")
        store.migrate(con)
        feed = {"domain": "vogue.com", "feed_url": "https://www.vogue.com/feed"}
        with mock.patch.object(ingest_rss, "polite_get", return_value=FakeResp(RSS)):
            first = ingest_rss.ingest_feed(con, feed, fetched_at="2026-09-20T00:00:00Z")
            second = ingest_rss.ingest_feed(con, feed, fetched_at="2026-09-21T00:00:00Z")
        self.assertEqual((first["inserted"], first["undated"], first["future"]), (2, 1, 1))
        self.assertEqual((second["inserted"], second["unchanged"]), (0, 2))
        self.assertEqual(con.execute("SELECT COUNT(*) FROM items").fetchone()[0], 2)

    def test_robots_disallow_and_http_errors_are_reported(self):
        con = store.connect(":memory:")
        store.migrate(con)
        feed = {"domain": "x.example", "feed_url": "https://x.example/feed"}
        with mock.patch.object(ingest_rss, "polite_get", return_value=None):
            self.assertIn("robots", ingest_rss.ingest_feed(con, feed)["error"])
        with mock.patch.object(ingest_rss, "polite_get", return_value=FakeResp("", 503)):
            self.assertEqual(ingest_rss.ingest_feed(con, feed)["error"], "HTTP 503")
        with mock.patch.object(ingest_rss, "polite_get", return_value=FakeResp("<not xml")):
            self.assertIn("ParseError", ingest_rss.ingest_feed(con, feed)["error"])

    def test_style_share_and_section_choice(self):
        news = [{"title": "Election results", "url": "https://x.example/politics/1"}] * 3
        style = [{"title": "Paris Fashion Week SS27 runway", "url": "https://x.example/fashion/1"},
                 {"title": "La tendance du moment", "url": "https://x.example/mode/2"},
                 {"title": "Défilé Chanel", "url": "https://x.example/mode/3"}]
        self.assertEqual(ingest_rss.style_share(news), 0)
        self.assertEqual(ingest_rss.style_share(style), 1)
        feeds = {"https://x.example/feed": news, "https://x.example/fashion/feed/": style}
        dated = lambda u: [dict(e, published_at="2026-09-20T00:00:00Z") for e in feeds.get(u, [])]
        with (
            mock.patch.object(ingest_rss, "polite_get", return_value=None),
            mock.patch.object(ingest_rss, "feed_entries", side_effect=dated),
        ):
            url, share, before = ingest_rss.find_section_feed("x.example", "https://x.example/feed")
        self.assertEqual((url, share, before), ("https://x.example/fashion/feed/", 1.0, 0.0))

    def test_clean_excerpt(self):
        self.assertEqual(ingest_rss.clean_excerpt("<p>Sheer&nbsp;layers <b>over</b>" + chr(10) + " tailoring.</p>"),
                         "Sheer layers over tailoring.")
        self.assertIsNone(ingest_rss.clean_excerpt("<img src='x.jpg'/>"))
        long = ingest_rss.clean_excerpt("word " * 300)
        self.assertLessEqual(len(long), ingest_rss.EXCERPT_MAX + 1)
        self.assertTrue(long.endswith("…"))

    def test_feed_language_and_excerpt_reach_the_store(self):
        rss = RSS.replace("<channel>", "<channel><language>en-GB</language>", 1)
        e = ingest_rss.parse_feed(rss, "https://www.vogue.com/feed")
        self.assertEqual(e[0]["lang"], "en-gb")
        con = store.connect(":memory:")
        store.migrate(con)
        feed = {"domain": "vogue.com", "feed_url": "https://www.vogue.com/feed"}
        with mock.patch.object(ingest_rss, "polite_get", return_value=FakeResp(rss)):
            ingest_rss.ingest_feed(con, feed, fetched_at="2026-09-20T00:00:00Z")
        row = con.execute("SELECT text_excerpt, lang, feed_url FROM items WHERE url LIKE '%dated-item'").fetchone()
        self.assertEqual(row, ("Summary.", "en-gb", "https://www.vogue.com/feed"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
