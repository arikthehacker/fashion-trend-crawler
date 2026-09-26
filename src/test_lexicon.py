"""Tests for lexicon-match-v1 (src/lexicon.py)."""

import re

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
