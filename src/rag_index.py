"""Derived retrieval index for EXP-004. Rebuildable from the evidence store at any time.

Layout of the index folder (default data/index/rag/, local and git-ignored):
  fts.db          SQLite FTS5: `words` (unicode61 tokenizer, diacritics folded) and
                  `trigram` (character trigrams, for text without spaces such as
                  Japanese). rowid = item_id.
  embeddings.npz  item_ids, content hashes and L2-normalized float32 vectors from the
                  frozen ARI3 encoder. Rows whose content hash is unchanged are reused on
                  the next build instead of being re-encoded.
  manifest.json   what was indexed: corpus fingerprint, cutoff, encoder and revision,
                  build times and sizes.

Usage:
  python src/rag_index.py build [--cutoff 2026-09-30T08:00:00Z] [--out DIR]
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

from item_store import DEFAULT_DB, ROOT
from rag_corpus import corpus_texts, fingerprint, open_corpus

EMBEDDER = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDER_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"  # same revision as ari3_freeze.py
DEFAULT_DIR = os.path.join(ROOT, "data", "index", "rag")
INDEX_VERSION = "exp004-index-v1"


def default_encoder():
    """The frozen ARI3 sentence encoder, loaded on first use."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDER, revision=EMBEDDER_REVISION)

    def encode(texts):
        return model.encode(list(texts), normalize_embeddings=True, batch_size=64).astype("float32")
    encode.info = {"name": EMBEDDER, "revision": EMBEDDER_REVISION, "max_seq_length": model.max_seq_length}
    return encode


def _write_fts(path, rows):
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.execute("CREATE VIRTUAL TABLE words USING fts5(text, tokenize = 'unicode61 remove_diacritics 2')")
    con.execute("CREATE VIRTUAL TABLE trigram USING fts5(text, tokenize = 'trigram')")
    con.executemany("INSERT INTO words (rowid, text) VALUES (?, ?)", [(i, t) for i, _, t in rows])
    con.executemany("INSERT INTO trigram (rowid, text) VALUES (?, ?)", [(i, t) for i, _, t in rows])
    con.commit()
    con.close()
    os.replace(tmp, path)


def build_index(corpus_con, out_dir=DEFAULT_DIR, encoder=None, cutoff=None):
    """Build or refresh the index for every original item first seen by `cutoff`."""
    import numpy as np
    os.makedirs(out_dir, exist_ok=True)
    rows = corpus_texts(corpus_con, cutoff)
    t0 = time.perf_counter()
    _write_fts(os.path.join(out_dir, "fts.db"), rows)
    t_fts = time.perf_counter() - t0

    emb_path = os.path.join(out_dir, "embeddings.npz")
    cached = {}
    if os.path.exists(emb_path):
        with np.load(emb_path, allow_pickle=False) as old:
            if str(old["encoder"]) == EMBEDDER_REVISION:
                cached = {(int(i), str(h)): v for i, h, v in zip(old["item_ids"], old["hashes"], old["vectors"])}
    todo = [(i, h, t) for i, h, t in rows if (i, h) not in cached]
    t0 = time.perf_counter()
    encoder = encoder or (default_encoder() if todo else None)
    fresh = dict(zip([(i, h) for i, h, _ in todo], encoder([t for _, _, t in todo]))) if todo else {}
    t_emb = time.perf_counter() - t0
    vectors = np.stack([fresh.get((i, h), cached.get((i, h))) for i, h, _ in rows]).astype("float32") if rows \
        else np.zeros((0, 384), dtype="float32")
    np.savez(emb_path + ".tmp.npz", item_ids=np.array([i for i, _, _ in rows], dtype="int64"),
             hashes=np.array([h for _, h, _ in rows]), vectors=vectors, encoder=np.array(EMBEDDER_REVISION))
    os.replace(emb_path + ".tmp.npz", emb_path)

    manifest = {
        "index_version": INDEX_VERSION,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cutoff_first_seen_at": cutoff,
        "items": len(rows),
        "corpus_fingerprint": fingerprint(rows),
        "text": "title + '. ' + stored excerpt, first 1,000 characters (jev_spike.text)",
        "chunking": "none",
        "encoder": getattr(encoder, "info", {"name": EMBEDDER, "revision": EMBEDDER_REVISION}),
        "dim": int(vectors.shape[1]),
        "encoded_this_build": len(todo),
        "reused_from_cache": len(rows) - len(todo),
        "lexical_tokenizers": {"words": "unicode61 remove_diacritics 2", "trigram": "trigram"},
        "build_seconds": {"fts": round(t_fts, 3), "embeddings": round(t_emb, 3)},
        "bytes": {"fts.db": os.path.getsize(os.path.join(out_dir, "fts.db")),
                  "embeddings.npz": os.path.getsize(emb_path)},
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    return manifest


class Index:
    """A loaded index: FTS connection (read-only), vectors, and an encoder for queries."""

    def __init__(self, out_dir=DEFAULT_DIR, encoder=None):
        import numpy as np
        with open(os.path.join(out_dir, "manifest.json"), encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.fts = sqlite3.connect(f"file:{os.path.abspath(os.path.join(out_dir, 'fts.db'))}?mode=ro", uri=True)
        with np.load(os.path.join(out_dir, "embeddings.npz"), allow_pickle=False) as data:
            self.item_ids = [int(i) for i in data["item_ids"]]
            self.vectors = data["vectors"]
        self.row = {i: n for n, i in enumerate(self.item_ids)}
        self._encoder = encoder

    def encode_query(self, text):
        if self._encoder is None:
            self._encoder = default_encoder()
        return self._encoder([text])[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build"])
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--out", default=DEFAULT_DIR)
    ap.add_argument("--cutoff", help="index only items first seen at or before this UTC time")
    args = ap.parse_args(argv)
    manifest = build_index(open_corpus(args.db), args.out, cutoff=args.cutoff)
    print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
