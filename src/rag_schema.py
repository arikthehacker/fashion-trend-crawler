"""Typed inputs and outputs for EXP-004 grounded retrieval.

Every tool argument and every generated answer passes through one of these models.
Unknown fields, wrong types, out-of-range values and malformed dates are rejected,
never coerced. Nothing here touches the database.
"""

import re
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "exp004-schema-v1"

TS = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
DAY = re.compile(r"^\d{4}-\d\d-\d\d$")

# Closed vocabularies. Sectors and coarse groups mirror the `sectors` table (migration 0001).
LANGUAGES = ("en", "ja", "it", "fr", "pt")
SECTORS = ("designer_origin", "runway", "editorial", "independent_criticism", "trade_intelligence", "social",
           "street_ugc", "retail", "resale", "institutional", "visual_archive", "unclear")
COARSE_GROUPS = ("designer_runway", "editorial", "social", "retail", "resale", "other")
METHODS = ("bm25", "dense", "hybrid")
MAX_K = 50

Strict = ConfigDict(extra="forbid", strict=True, frozen=True)


def _check_time(value, name):
    """UTC timestamps as YYYY-MM-DDTHH:MM:SSZ. A bare day means the end of that day for
    upper bounds and the start of it for lower bounds; callers pass `bound`."""
    if value is None:
        return None
    if not isinstance(value, str) or not (TS.match(value) or DAY.match(value)):
        raise ValueError(f"{name} must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ")
    return value


def lower_bound(value):
    return None if value is None else value if TS.match(value) else value + "T00:00:00Z"


def upper_bound(value):
    return None if value is None else value if TS.match(value) else value + "T23:59:59Z"


class Filters(BaseModel):
    """Deterministic constraints. They are applied in SQL before any ranking, so a
    similarity score can never admit an item that fails them."""
    model_config = Strict

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    as_of: Optional[str] = None
    temporal_mode: Literal["publication", "replay"] = "publication"
    languages: Optional[List[Literal[LANGUAGES]]] = Field(default=None, min_length=1, max_length=len(LANGUAGES))
    sectors: Optional[List[Literal[SECTORS]]] = Field(default=None, min_length=1, max_length=len(SECTORS))
    coarse_groups: Optional[List[Literal[COARSE_GROUPS]]] = Field(default=None, min_length=1,
                                                                  max_length=len(COARSE_GROUPS))
    outlets: Optional[List[str]] = Field(default=None, min_length=1, max_length=20)

    @field_validator("start_date", "end_date", "as_of")
    @classmethod
    def _times(cls, v, info):
        return _check_time(v, info.field_name)

    @field_validator("outlets")
    @classmethod
    def _domains(cls, v):
        for d in v or []:
            if not re.fullmatch(r"[a-z0-9.-]{3,100}", d):
                raise ValueError("outlets must be lowercase domain names")
        return v

    @model_validator(mode="after")
    def _consistent(self):
        if self.temporal_mode == "replay" and self.as_of is None:
            raise ValueError("replay mode needs as_of: the moment whose knowledge is being replayed")
        lo, hi = lower_bound(self.start_date), upper_bound(self.end_date)
        if lo and hi and lo > hi:
            raise ValueError("start_date is after end_date")
        return self


class SearchArgs(BaseModel):
    model_config = Strict

    query: str = Field(min_length=1, max_length=500)
    filters: Filters = Filters()
    method: Literal[METHODS] = "hybrid"
    k: int = Field(default=10, ge=1, le=MAX_K)

    @field_validator("query")
    @classmethod
    def _query(cls, v):
        if not v.strip():
            raise ValueError("query is blank")
        return v


class GetArticleArgs(BaseModel):
    model_config = Strict

    item_id: int = Field(ge=1)


class Evidence(BaseModel):
    """One stored ARI3 record with its provenance. `excerpt` is the stored feed summary
    (at most 500 characters), not the full article."""
    model_config = Strict

    item_id: int
    url: str
    title: Optional[str]
    excerpt: Optional[str]
    outlet: str
    sector: Optional[str]
    coarse_group: Optional[str]
    lang: Optional[str]
    published_at: str
    first_seen_at: str
    first_seen_basis: Literal["live_insert", "reconstructed"]
    fetched_at: str


class Hit(BaseModel):
    model_config = Strict

    rank: int = Field(ge=1)
    score: float
    evidence: Evidence
    ranks_by_method: dict


class SearchResult(BaseModel):
    model_config = Strict

    query: str
    filters: Filters
    method: Literal[METHODS]
    k: int
    eligible_items: int
    hits: List[Hit]
    corpus_fingerprint: str
    index_manifest: dict
    schema_version: str = SCHEMA_VERSION


class Claim(BaseModel):
    """One factual statement and the context items that support it."""
    model_config = Strict

    text: str = Field(min_length=1, max_length=600)
    supporting_item_ids: List[int] = Field(min_length=1, max_length=10)


class GroundedAnswer(BaseModel):
    """What a language model must return. There is no free prose field: every factual
    statement is a claim with at least one supporting item from the supplied context.
    Limitations describe what the evidence cannot show. URLs, dates and outlets are never
    taken from the model; code fills them from the store."""
    model_config = Strict

    insufficient_evidence: bool
    claims: List[Claim] = Field(default_factory=list, max_length=12)
    limitations: List[str] = Field(default_factory=list, max_length=5)

    @field_validator("limitations")
    @classmethod
    def _short(cls, v):
        for text in v:
            if not 1 <= len(text) <= 300:
                raise ValueError("each limitation is 1 to 300 characters")
        return v

    @model_validator(mode="after")
    def _refusal_is_empty(self):
        if self.insufficient_evidence and self.claims:
            raise ValueError("an insufficient-evidence answer carries no claims")
        if not self.insufficient_evidence and not self.claims:
            raise ValueError("an answer without claims must set insufficient_evidence")
        return self


class Citation(BaseModel):
    """A cited item as stored in ARI3, never as described by the model."""
    model_config = Strict

    item_id: int
    url: str
    outlet: str
    title: Optional[str]
    published_at: str
    first_seen_at: str
    first_seen_basis: Literal["live_insert", "reconstructed"]


class TemporalScope(BaseModel):
    model_config = Strict

    temporal_mode: Literal["publication", "replay"]
    as_of: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    evidence_published_from: Optional[str]
    evidence_published_to: Optional[str]


class AskResponse(BaseModel):
    """The result of ask_ari3. `public()` drops the debug block, which is for
    developers and evaluation, not for end users."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["answered", "insufficient_evidence", "rejected", "error"]
    query: str
    filters: Filters
    claims: List[Claim] = []
    citations: List[Citation] = []
    limitations: List[str] = []
    temporal_scope: TemporalScope
    message: str = ""
    validation: dict = {}
    debug: dict = {}

    def public(self):
        return self.model_dump(mode="json", exclude={"debug"})
