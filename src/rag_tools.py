"""Typed tools over the ARI3 evidence store: search_articles and get_article.

Each tool validates its arguments with rag_schema (unknown fields, wrong types and
out-of-range values are rejected), runs deterministic code, and returns records with
provenance. The tools work without any language model or API key. TOOL_DEFINITIONS
gives their JSON schemas for a model that calls them later.
"""

import json

from pydantic import ValidationError

from item_store import DEFAULT_DB
from rag_corpus import get_items, open_corpus
from rag_index import DEFAULT_DIR, Index
from rag_retrieve import search
from rag_schema import GetArticleArgs, SearchArgs


class ToolError(ValueError):
    """A tool call was rejected. The message says why, and nothing was run."""


def _validate(model, arguments):
    if not isinstance(arguments, dict):
        raise ToolError(f"{model.__name__}: arguments must be a JSON object")
    try:
        return model.model_validate_json(json.dumps(arguments))
    except ValidationError as e:
        problems = "; ".join(f"{'.'.join(map(str, err['loc'])) or 'arguments'}: {err['msg']}" for err in e.errors())
        raise ToolError(f"{model.__name__}: {problems}") from None


class Tools:
    def __init__(self, db=DEFAULT_DB, index_dir=DEFAULT_DIR, encoder=None, lexical="auto"):
        self.corpus = open_corpus(db)
        self.index = Index(index_dir, encoder=encoder)
        self.lexical = lexical

    def search_articles(self, arguments):
        args = _validate(SearchArgs, arguments)
        return search(self.corpus, self.index, args, self.lexical)

    def get_article(self, arguments):
        args = _validate(GetArticleArgs, arguments)
        found = get_items(self.corpus, [args.item_id])
        if not found:
            raise ToolError(f"get_article: item {args.item_id} does not exist")
        return found[0]

    def call(self, name, arguments):
        if name not in ("search_articles", "get_article"):
            raise ToolError(f"unknown tool {name!r}")
        return getattr(self, name)(arguments)


TOOL_DEFINITIONS = [
    {"name": "search_articles",
     "description": ("Search ARI3's stored evidence (headline plus a feed excerpt of at most 500 characters per "
                     "item, not full articles). Filters are applied before ranking. temporal_mode 'publication' "
                     "admits items published by as_of. 'replay' also requires that ARI3 had first seen the item "
                     "by as_of."),
     "parameters": SearchArgs.model_json_schema()},
    {"name": "get_article",
     "description": "Return one stored ARI3 item with its provenance (URL, publication, first-seen and fetch times).",
     "parameters": GetArticleArgs.model_json_schema()},
]
