"""Tests for lexicon-match-v1 (src/lexicon.py)."""

import re

import lexicon
from lexicon import find_mentions, slug, variant_pattern


def lex(**terms):
    return [(t, re.compile("|".join(variant_pattern(v) for v in vs), re.I)) for t, vs in terms.items()]


def hits(text, lexicon):
    return sorted(t for t, _ in find_mentions(text, lexicon))


def test_word_boundaries():
    L = lex(lace=["lace"])
    assert hits("A lace dress", L) == ["lace"]
    assert hits("Lace trims and laces", L) == ["lace", "lace"]
    assert hits("a gold necklace", L) == []
    assert hits("she laced her boots", L) == []


def test_plural_on_last_word_only():
    L = lex(**{"mary-jane": ["mary jane"]})
    assert hits("Mary Janes are back", L) == ["mary-jane"]
    assert hits("Mary's Jane", L) == []


def test_space_and_hyphen_interchangeable():
    L = lex(**{"wide-leg": ["wide-leg"]})
    assert hits("wide leg jeans", L) == ["wide-leg"]
    assert hits("Wide-leg trousers", L) == ["wide-leg"]


def test_note_phrases_exclude_other_meanings():
    L = lex(platform=["platform heel", "platform sneaker"], capri=["capri pants", "capris"])
    assert hits("a resale platform grows", L) == []
    assert hits("platform heels and capri pants", L) == ["capri", "platform"]
    assert hits("Capri Holdings reports earnings", L) == []


def test_spans_are_distinct():
    L = lex(sheer=["sheer"])
    spans = [s for _, s in find_mentions("sheer top, sheer skirt", L)]
    assert spans == [0, 11]


def test_slug():
    assert slug("Mary Jane") == "mary-jane"
    assert slug("Gen Z") == "gen-z"
    assert slug("Y2K") == "y2k"


def test_window_clause():
    assert lexicon.window_clause() == ("", ())
    assert lexicon.window_clause("2026-09-28", "2026-10-04")[1] == ("2026-09-28T00:00:00Z", "2026-10-05T00:00:00Z")
    try:
        lexicon.window_clause("2026-09-28", None)
        raise AssertionError("a half-open window must be refused")
    except ValueError:
        pass


def test_windowed_extract_touches_only_window_items_and_is_idempotent(tmp_path):
    import contextlib
    import io
    import item_store as store
    con = store.connect(str(tmp_path / "s.db"))
    store.migrate(con)
    con.execute("INSERT INTO lexicon_versions (lexicon_version, created_at, note) VALUES (1, 'x', 'v1')")
    con.execute("INSERT INTO terms (term_id, canonical, signal_type, introduced_in) VALUES ('corset', 'corset', 'garment_silhouette', 1)")
    con.execute("INSERT INTO term_variants (term_id, variant, lexicon_version) VALUES ('corset', 'corset', 1)")
    con.execute("INSERT INTO term_rules (term_id, needs_sense_check, decided_at) VALUES ('corset', 0, 'x')")
    for url, pub in (("https://a.example/in", "2026-09-29T10:00:00Z"), ("https://a.example/out", "2026-09-20T10:00:00Z")):
        store.upsert_item(con, url=url, published_at=pub, source_method="rss", title="A corset dress",
                          fetched_at="2026-10-01T00:00:00Z", text_excerpt="Corset.", lang="en")
    con.commit()
    with contextlib.redirect_stdout(io.StringIO()):
        lexicon.cmd_extract(con, "2026-09-28", "2026-10-04")
        first = con.execute("SELECT count(*), count(DISTINCT item_id) FROM mentions").fetchone()
        lexicon.cmd_extract(con, "2026-09-28", "2026-10-04")
    assert first == (2, 1)  # two matches in the one in-window item, none in the other
    assert con.execute("SELECT count(*) FROM mentions").fetchone()[0] == 2


def _boundary_store(tmp_path):
    import item_store as store
    con = store.connect(str(tmp_path / "b.db"))
    store.migrate(con)
    con.execute("INSERT INTO lexicon_versions (lexicon_version, created_at, note) VALUES (1, 'x', 'v1')")
    con.execute("INSERT INTO terms (term_id, canonical, signal_type, introduced_in) VALUES ('corset', 'corset', 'garment_silhouette', 1)")
    con.execute("INSERT INTO term_variants (term_id, variant, lexicon_version) VALUES ('corset', 'corset', 1)")
    con.execute("INSERT INTO term_rules (term_id, needs_sense_check, decided_at) VALUES ('corset', 0, 'x')")
    ids = {}
    for pub in ("2026-09-27T23:59:59Z", "2026-09-28T00:00:00Z", "2026-10-04T23:59:59Z", "2026-10-05T00:00:00Z"):
        ids[pub], _ = store.upsert_item(con, url=f"https://a.example/{pub[:10]}-{pub[11:13]}", published_at=pub,
                                        source_method="rss", title="A corset", fetched_at="2026-10-06T00:00:00Z",
                                        text_excerpt="", lang="en")
    con.commit()
    return con, ids


def test_window_bounds_are_half_open_utc():
    assert lexicon.window_bounds("2026-09-28", "2026-10-04") == ("2026-09-28T00:00:00Z", "2026-10-05T00:00:00Z")


def test_score_window_boundaries(tmp_path):
    con, ids = _boundary_store(tmp_path)
    picked = {r[0] for r in lexicon.unscored_items(con, "2026-09-28", "2026-10-04")}
    assert ids["2026-09-28T00:00:00Z"] in picked
    assert ids["2026-10-04T23:59:59Z"] in picked
    assert ids["2026-10-05T00:00:00Z"] not in picked
    assert ids["2026-09-27T23:59:59Z"] not in picked
    assert {r[0] for r in lexicon.unscored_items(con)} == set(ids.values())  # no window: every item


def test_extract_window_boundaries(tmp_path):
    import contextlib
    import io
    con, ids = _boundary_store(tmp_path)
    with contextlib.redirect_stdout(io.StringIO()):
        lexicon.cmd_extract(con, "2026-09-28", "2026-10-04")
    got = {r[0] for r in con.execute("SELECT DISTINCT item_id FROM mentions")}
    assert got == {ids["2026-09-28T00:00:00Z"], ids["2026-10-04T23:59:59Z"]}
