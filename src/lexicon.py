"""Lexicon v1: load the editor's terms, score items for style, extract mentions.

Commands (run in order the first time):
    python src/lexicon.py load <terms_v1_review.json>   # terms, variants, editor rules
    python src/lexicon.py score                         # ARI3 v0.0.2 on every unscored item
    python src/lexicon.py extract                       # lexicon-match mentions
    python src/lexicon.py report                        # counts per term

Extraction is deterministic word matching, not a model. A variant matches at a
word boundary, case-insensitive, with spaces and hyphens interchangeable and an
optional plural ending on the last word. "lace" matches "lace" and "laces" but
not "necklace" or "laced".
"""

import argparse
import json
import os
import re
import sys

from item_store import DEFAULT_DB, ROOT, connect, migrate, utc_now

LEXICON_VERSION = 1
EXTRACTOR_VERSION = "lexicon-match-v1"
STYLE_MODEL = "ari3-v0.0.2"

SIGNAL_TYPES = {
    "Aesthetic and style names": "aesthetic_term",
    "Garments and silhouettes": "garment_silhouette",
    "Footwear": "footwear",
    "Materials and surface": "material",
    "Color and print": "color_print",
    "Details": "detail",
    "Market and commerce language": "commerce_language",
}

# The editor's usage notes, turned into the phrases that are counted.
NOTE_VARIANTS = {
    "capri": ["capri pants", "capri trousers", "capris"],               # "only capri pants"
    "platform": ["platform shoe", "platform heel", "platform sneaker",  # "only platform shoe,
                 "platform sandal", "platform boot", "platform loafer"],  #  heel, or sneaker"
    "trench": ["trench", "trench coat"],                                # "trench coat"
    "bow": ["bow detail", "hair bow", "bows"],                          # "count bow detail, hair bow, bows"
}


def slug(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def variant_pattern(variant: str) -> str:
    words = [re.escape(w) for w in re.split(r"[\s-]+", variant.strip().lower()) if w]
    return r"\b" + r"[\s-]+".join(words) + r"(?:s|es)?\b"


def compile_lexicon(con):
    """Return [(term_id, compiled regex)] for every current, unmerged term."""
    rows = con.execute(
        """SELECT v.term_id, v.variant FROM term_variants v JOIN terms t USING (term_id)
           WHERE t.merged_into IS NULL ORDER BY v.term_id""").fetchall()
    by_term = {}
    for term_id, variant in rows:
        by_term.setdefault(term_id, []).append(variant_pattern(variant))
    return [(t, re.compile("|".join(sorted(p, key=len, reverse=True)), re.I)) for t, p in by_term.items()]


def find_mentions(text: str, lexicon):
    """Yield (term_id, span_start) for every match in text."""
    for term_id, rx in lexicon:
        for m in rx.finditer(text):
            yield term_id, m.start()


def item_text(title, excerpt):
    return f"{title or ''}\n{excerpt or ''}"


def cmd_load(con, path):
    with open(path, encoding="utf-8") as f:
        review = json.load(f)
    now = utc_now()
    con.execute("INSERT OR IGNORE INTO lexicon_versions (lexicon_version, created_at, note) VALUES (?,?,?)",
                (LEXICON_VERSION, now, "Lexicon v1: terms reviewed by the editor, 2026-09-26"))
    n = 0
    for term, d in review["decisions"].items():
        if d["decision"] == "drop":
            continue
        tid = slug(term)
        con.execute("INSERT OR IGNORE INTO terms (term_id, canonical, signal_type, introduced_in) VALUES (?,?,?,?)",
                    (tid, term, SIGNAL_TYPES[d["group"]], LEXICON_VERSION))
        variants = NOTE_VARIANTS.get(term, d["variants"])
        for v in variants:
            con.execute("INSERT OR IGNORE INTO term_variants (term_id, variant, lexicon_version) VALUES (?,?,?)",
                        (tid, v.lower(), LEXICON_VERSION))
        note = d.get("note")
        con.execute("INSERT OR REPLACE INTO term_rules (term_id, editor_note, needs_sense_check, decided_at) VALUES (?,?,?,?)",
                    (tid, note, 1 if note and note.startswith("needs sense check") else 0, d["decided_at"]))
        n += 1
    con.commit()
    print(f"Lexicon v{LEXICON_VERSION}: {n} terms loaded, "
          f"{con.execute('SELECT count(*) FROM term_variants').fetchone()[0]} variants, "
          f"{con.execute('SELECT count(*) FROM term_rules WHERE needs_sense_check=1').fetchone()[0]} flagged for sense checks.")


def cmd_score(con):
    import numpy as np
    import jev_spike as J
    from ari3_freeze import EMBEDDER_REVISION
    from sentence_transformers import SentenceTransformer
    rows = con.execute(
        """SELECT item_id, title, text_excerpt FROM items
           WHERE item_id NOT IN (SELECT item_id FROM label_predictions WHERE model_version=? AND task=?)""",
        (STYLE_MODEL, J.TASK)).fetchall()
    if not rows:
        print("Every item already has an ARI3 v0.0.2 prediction.")
        return
    w = np.load(os.path.join(ROOT, "models", STYLE_MODEL, "weights.npz"))
    T, q = float(w["temperature"][0]), float(w["qhat"][0])
    emb = SentenceTransformer(J.EMBEDDER, revision=EMBEDDER_REVISION)
    X = emb.encode([J.text(r[1], r[2]) for r in rows], normalize_embeddings=True, batch_size=64)
    p = 1 / (1 + np.exp(-(X @ w["coef"][0] + w["intercept"][0]) / T))
    now = utc_now()
    out = []
    for (item_id, _, _), pi in zip(rows, p):
        s = [l for l, ok in (("yes", 1 - pi <= q), ("no", pi <= q)) if ok]
        out.append((item_id, J.TASK, STYLE_MODEL, "yes" if pi >= 0.5 else "no", None, float(pi), json.dumps(s), now))
    con.executemany(
        """INSERT INTO label_predictions (item_id, task, model_version, predicted_label, probability,
             calibrated_probability, conformal_set, created_at) VALUES (?,?,?,?,?,?,?,?)""", out)
    con.commit()
    sets = [o[6] for o in out]
    print(f"Scored {len(out)} items with {STYLE_MODEL}: {sets.count(json.dumps(['yes']))} style, "
          f"{sets.count(json.dumps(['no']))} not style, {sets.count(json.dumps(['yes', 'no']))} not sure.")


def cmd_extract(con):
    lexicon = compile_lexicon(con)
    rows = con.execute("SELECT item_id, title, text_excerpt FROM items").fetchall()
    before = con.execute("SELECT count(*) FROM mentions WHERE extractor_version=?", (EXTRACTOR_VERSION,)).fetchone()[0]
    batch = [(item_id, term_id, start, EXTRACTOR_VERSION)
             for item_id, title, ex in rows for term_id, start in find_mentions(item_text(title, ex), lexicon)]
    con.executemany("INSERT OR IGNORE INTO mentions (item_id, term_id, span_start, extractor_version) VALUES (?,?,?,?)", batch)
    con.commit()
    after = con.execute("SELECT count(*) FROM mentions WHERE extractor_version=?", (EXTRACTOR_VERSION,)).fetchone()[0]
    print(f"{EXTRACTOR_VERSION}: scanned {len(rows)} items, {after - before} new mentions, {after} total.")


def cmd_report(con):
    rows = con.execute(
        """SELECT t.canonical, r.needs_sense_check,
                  (SELECT count(DISTINCT e.item_id) FROM v_events e WHERE e.canonical_id=t.term_id) AS items_all,
                  (SELECT count(DISTINCT s.item_id) FROM v_events_style s
                     WHERE s.canonical_id=t.term_id AND s.model_version=?) AS items_style
           FROM terms t JOIN term_rules r USING (term_id) ORDER BY items_all DESC""", (STYLE_MODEL,)).fetchall()
    print(f"{'term':24} {'all items':>9} {'style items':>11}")
    for name, flag, a, s in rows:
        print(f"{name:24} {a:9} {('sense check' if flag else s):>11}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("load").add_argument("review")
    for c in ("score", "extract", "report"):
        sub.add_parser(c)
    args = ap.parse_args(argv)
    con = connect(args.db)
    migrate(con)
    {"load": lambda: cmd_load(con, args.review), "score": lambda: cmd_score(con),
     "extract": lambda: cmd_extract(con), "report": lambda: cmd_report(con)}[args.cmd]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
