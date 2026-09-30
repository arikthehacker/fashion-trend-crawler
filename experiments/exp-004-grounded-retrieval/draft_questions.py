"""Writes questions_v1.jsonl: 60 draft evaluation questions for EXP-004.

The questions were drafted from the corpus inventory on 2026-09-30 (lexicon terms with
style events, outlets, sectors and languages present in the store). They are drafts
(drafted_by "machine_draft") until the editor reviews them. answerable_expected is the
drafter's expectation only. Whether a question is answerable is decided by the editor's
relevance judgments.

usage: python experiments/exp-004-grounded-retrieval/draft_questions.py
"""

import json
import os

REF = "2026-09-30T08:00:00Z"
VERSION = "v1"
HERE = os.path.dirname(os.path.abspath(__file__))

# (question, query, answerable_expected, language, query_type, filters, notes)
Q = [
    # ---- terms ----
    ("What are outlets saying about ballet flats?", "ballet flats", True, "en", "term", {}, ""),
    ("What are outlets saying about quiet luxury?", "quiet luxury", True, "en", "term", {}, ""),
    ("How is Y2K fashion being described?", "Y2K fashion", True, "en", "term", {}, ""),
    ("What coverage mentions Mary Jane shoes?", "Mary Jane shoes", True, "en", "term", {}, ""),
    ("What are outlets saying about barrel-leg jeans?", "barrel leg jeans", True, "en", "term", {}, ""),
    ("How is suede being written about?", "suede", True, "en", "term", {}, ""),
    ("What coverage names leopard print?", "leopard print", True, "en", "term", {}, ""),
    ("What are outlets saying about trench coats?", "trench coat", True, "en", "term", {}, ""),
    ("How is fringe described in recent coverage?", "fringe", True, "en", "term", {}, ""),
    ("What are outlets saying about corsets?", "corset", True, "en", "term", {}, ""),
    ("What coverage mentions boho style?", "boho", True, "en", "term", {}, ""),
    ("What are outlets saying about kitten heels?", "kitten heels", True, "en", "term", {}, ""),
    ("Which items name chocolate brown or burgundy as colors?", "chocolate brown burgundy", True, "en", "term",
     {}, ""),
    ("What coverage mentions indie sleaze?", "indie sleaze", True, "en", "term", {}, ""),
    ("What are outlets saying about lunar-inspired spacesuit fashion?", "lunar spacesuit fashion", False, "en",
     "term", {}, "topic not seen in the corpus inventory"),

    # ---- temporal ----
    ("What was published about sheer dresses between 20 and 25 September 2026?", "sheer dresses", True, "en",
     "temporal", {"start_date": "2026-09-20", "end_date": "2026-09-25"}, ""),
    ("What had been published about loafers by 15 September 2026?", "loafers", True, "en", "temporal",
     {"as_of": "2026-09-15"}, "publication mode"),
    ("What was published about minimalism in the week of 21 September 2026?", "minimalism", True, "en",
     "temporal", {"start_date": "2026-09-21", "end_date": "2026-09-27"}, ""),
    ("What evidence about Y2K fashion was published before 2025?", "Y2K", True, "en", "temporal",
     {"end_date": "2024-12-31"}, "older items collected later by feed backlog"),
    ("Which articles about tailoring were published in the last two weeks?", "tailoring", True, "en", "temporal",
     {"start_date": "2026-09-16", "end_date": "2026-09-30"}, "two weeks before the reference time"),
    ("What was written about grunge before 2020?", "grunge", True, "en", "temporal", {"end_date": "2019-12-31"},
     ""),
    ("What was published about workwear in 2024?", "workwear", True, "en", "temporal",
     {"start_date": "2024-01-01", "end_date": "2024-12-31"}, ""),
    ("What had been published about ballet flats before 2020?", "ballet flats", False, "en", "temporal",
     {"end_date": "2019-12-31"}, ""),
    ("What did outlets report about the Met Gala in 1998?", "Met Gala", False, "en", "temporal",
     {"start_date": "1998-01-01", "end_date": "1998-12-31"}, "the store has nothing published before 2015"),
    ("What could ARI3 have known about ballet flats on 24 September 2026?", "ballet flats", True, "en", "temporal",
     {"as_of": "2026-09-24T23:59:59Z", "temporal_mode": "replay"}, "replay mode"),
    ("What could ARI3 have known about quiet luxury on 20 September 2026?", "quiet luxury", False, "en",
     "temporal", {"as_of": "2026-09-20", "temporal_mode": "replay"},
     "replay before collection began on 2026-09-23"),
    ("What could ARI3 have known about denim on 22 September 2026?", "denim", False, "en", "temporal",
     {"as_of": "2026-09-22", "temporal_mode": "replay"}, "replay before collection began on 2026-09-23"),
    ("What could ARI3 have known about sneakers by 26 September 2026?", "sneakers", True, "en", "temporal",
     {"as_of": "2026-09-26", "temporal_mode": "replay"}, "replay mode"),

    # ---- source filters ----
    ("What has Who What Wear published about loafers?", "loafers", True, "en", "source_filter",
     {"outlets": ["whowhatwear.com"]}, ""),
    ("What has the Poshmark blog said about resale?", "resale", True, "en", "source_filter",
     {"outlets": ["blog.poshmark.com"]}, ""),
    ("What has Vogue published about cowboy boots?", "cowboy boots", True, "en", "source_filter",
     {"outlets": ["vogue.com"]}, ""),
    ("What has the V&A published about fashion exhibitions?", "fashion exhibition", True, "en", "source_filter",
     {"outlets": ["vam.ac.uk"]}, ""),
    ("What has WWD reported about quiet luxury?", "quiet luxury", True, "en", "source_filter",
     {"outlets": ["wwd.com"]}, ""),
    ("What has the Business of Fashion said about secondhand clothing?", "secondhand", True, "en", "source_filter",
     {"outlets": ["businessoffashion.com"]}, ""),
    ("What has the Poshmark blog said about quiet luxury?", "quiet luxury", False, "en", "source_filter",
     {"outlets": ["blog.poshmark.com"]}, ""),

    # ---- sector filters ----
    ("What are retail sources saying about knitwear?", "knitwear", True, "en", "sector_filter",
     {"coarse_groups": ["retail"]}, ""),
    ("What do designer and runway sources say about spring 2027 collections?", "spring 2027 collection", True,
     "en", "sector_filter", {"coarse_groups": ["designer_runway"]}, ""),
    ("What does resale coverage say about handbags?", "handbags", True, "en", "sector_filter",
     {"coarse_groups": ["resale"]}, "resale holds 10 items"),
    ("What exhibitions do museum and institutional sources describe?", "exhibition", True, "en", "sector_filter",
     {"coarse_groups": ["other"]}, ""),
    ("What are social sources saying about the clean girl aesthetic?", "clean girl", False, "en", "sector_filter",
     {"coarse_groups": ["social"]}, "the social sector holds no items"),
    ("What do editorial outlets say about chocolate brown?", "chocolate brown", True, "en", "sector_filter",
     {"coarse_groups": ["editorial"]}, ""),
    ("What have runway sources said about indie sleaze?", "indie sleaze", False, "en", "sector_filter",
     {"coarse_groups": ["designer_runway"]}, ""),

    # ---- multilingual ----
    ("バレエシューズについて何が書かれていますか？", "バレエシューズ", True, "ja", "multilingual",
     {"languages": ["ja"]}, ""),
    ("スニーカーの新作について何が報じられていますか？", "スニーカー 新作", True, "ja", "multilingual",
     {"languages": ["ja"]}, ""),
    ("東京のファッションウィークについて何が書かれていますか？", "東京 ファッションウィーク", True, "ja",
     "multilingual", {"languages": ["ja"]}, ""),
    ("Quali tendenze moda descrive la stampa italiana per l'autunno?", "tendenze moda autunno", True, "it",
     "multilingual", {"languages": ["it"]}, ""),
    ("Cosa scrive la stampa italiana sugli stivali?", "stivali", True, "it", "multilingual", {"languages": ["it"]},
     ""),
    ("Que disent les sources françaises des défilés de la Fashion Week de Paris ?", "défilés Fashion Week Paris",
     True, "fr", "multilingual", {"languages": ["fr"]}, ""),
    ("Que disent les sources françaises de la haute couture ?", "haute couture", True, "fr", "multilingual",
     {"languages": ["fr"]}, ""),
    ("Quais tendências de moda a imprensa brasileira descreve?", "tendências de moda", True, "pt", "multilingual",
     {"languages": ["pt"]}, ""),
    ("What do Japanese-language sources say about sneakers?", "sneakers", True, "en", "multilingual",
     {"languages": ["ja"]}, "English query over Japanese items"),
    ("What do Italian-language sources say about tailoring?", "tailoring", True, "en", "multilingual",
     {"languages": ["it"]}, "English query over Italian items"),
    ("日本語の記事はインディースリーズについて何を書いていますか？", "インディースリーズ", False, "ja", "multilingual",
     {"languages": ["ja"]}, ""),
    ("O que a imprensa brasileira diz sobre kitten heels?", "kitten heels", False, "pt", "multilingual",
     {"languages": ["pt"]}, ""),

    # ---- general ----
    ("Which colors are outlets naming for autumn 2026?", "autumn colors 2026", True, "en", "general", {}, ""),
    ("What are outlets saying about men's tailoring?", "men's tailoring suits", True, "en", "general", {}, ""),
    ("What collaborations between brands are being reported?", "collaboration collection", True, "en", "general",
     {}, ""),
    ("How are outlets describing the return of 1990s minimalism?", "90s minimalism", True, "en", "general", {},
     ""),
    ("What are outlets saying about underwater couture for divers?", "underwater couture divers", False, "en",
     "general", {}, "topic not seen in the corpus inventory"),
    ("What was reported about fashion shows held on Mars?", "fashion show Mars", False, "en", "general", {},
     "topic not seen in the corpus inventory"),
]


def main():
    assert len(Q) == 60, len(Q)
    path = os.path.join(HERE, "questions_v1.jsonl")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for n, (question, query, answerable, lang, qtype, filters, notes) in enumerate(Q, 1):
            f.write(json.dumps({"question_id": f"q{n:03d}", "question": question, "query": query,
                                "answerable_expected": answerable, "language": lang, "query_type": qtype,
                                "filters": filters, "reference_time": REF, "dataset_version": VERSION,
                                "drafted_by": "machine_draft", "notes": notes}, ensure_ascii=False) + "\n")
    print(f"wrote {len(Q)} questions to {path}")


if __name__ == "__main__":
    main()
