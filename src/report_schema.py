#############################################################
# report_schema.py
# defines the ARI3LLA INDEX report JSON structure (docs/ARI3LLA
# INDEX.txt section 41) as a dataclass, plus helpers to validate
# a dict against that shape and to write a dated report file to
# data/reports/<date>.json (instead of overwriting a single
# trends_summary.json).
#############################################################

from dataclasses import dataclass, field, asdict
import hashlib
import json
import os

from taxonomy import CONFIDENCE_LEVELS, VOLATILITY_LABELS, ORIGIN_CLASSIFICATIONS

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "reports"
)

# top-level keys required in every report (section 41)
REQUIRED_TOP_LEVEL_KEYS = [
    "report_date",
    "collection_window",
    "sources_scanned",
    "items_collected",
    "source_sector_breakdown",
    "executive_summary",
    "top_signals",
    "repeated_keywords",
    "garments",
    "silhouettes",
    "materials",
    "colors",
    "aesthetic_terms",
    "cultural_references",
    "limitations",
    "archive_tags",
]

# required keys within each entry of top_signals
REQUIRED_SIGNAL_KEYS = [
    "name",
    "type",
    "source_sectors",
    "confidence",
    "volatility",
    "origin_classification",
    "evidence",
    "index_note",
]


@dataclass
class CollectionWindow:
    start: str = ""
    end: str = ""


@dataclass
class Signal:
    name: str = ""
    type: str = ""
    source_sectors: list = field(default_factory=list)
    confidence: str = ""
    volatility: str = ""
    origin_classification: str = ""
    evidence: str = ""
    index_note: str = ""
    # number of independent sources reporting this signal. defaults to 1
    # (single-source, unconfirmed) per AP/Reuters attribution norms —
    # see docs/agent-logs/journalism-research.md #1. optional/backward
    # compatible: old reports missing this field are treated as single-source.
    source_corroboration_count: int = 1


@dataclass
class Report:
    report_date: str = ""
    collection_window: CollectionWindow = field(default_factory=CollectionWindow)
    sources_scanned: int = 0
    items_collected: int = 0
    source_sector_breakdown: dict = field(default_factory=dict)
    executive_summary: str = ""
    top_signals: list = field(default_factory=list)
    repeated_keywords: list = field(default_factory=list)
    garments: list = field(default_factory=list)
    silhouettes: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    colors: list = field(default_factory=list)
    aesthetic_terms: list = field(default_factory=list)
    cultural_references: list = field(default_factory=list)
    limitations: list = field(default_factory=list)
    archive_tags: list = field(default_factory=list)
    # sha256 of the report's serialized signal content, computed at save
    # time by save_report() for fixity/integrity verification (DPC/NDSA
    # checksum guidance — see docs/agent-logs/journalism-research.md #3).
    # empty string until save_report() populates it; optional/backward
    # compatible with reports saved before this field existed.
    content_hash: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


class SchemaValidationError(ValueError):
    pass


SHA256_HEX_LENGTH = 64


def compute_content_hash(data: dict) -> str:
    """
    sha256 hex digest of the report's serialized signal content
    (top_signals), used as a fixity checksum. computed over a
    canonical (sorted-key) JSON encoding so it's stable regardless
    of dict key ordering.
    """
    signals = data.get("top_signals", [])
    canonical = json.dumps(signals, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_report(data: dict) -> None:
    """
    raise SchemaValidationError if `data` is missing required
    fields or uses an out-of-vocabulary confidence/volatility/
    origin_classification value on any signal. does not mutate.
    """
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
    if missing:
        raise SchemaValidationError(f"report missing top-level keys: {missing}")

    window = data.get("collection_window", {})
    if not isinstance(window, dict) or "start" not in window or "end" not in window:
        raise SchemaValidationError("collection_window must have 'start' and 'end'")

    for i, signal in enumerate(data.get("top_signals", [])):
        missing_signal_keys = [k for k in REQUIRED_SIGNAL_KEYS if k not in signal]
        if missing_signal_keys:
            raise SchemaValidationError(
                f"top_signals[{i}] missing keys: {missing_signal_keys}"
            )
        if signal["confidence"] not in CONFIDENCE_LEVELS:
            raise SchemaValidationError(
                f"top_signals[{i}].confidence '{signal['confidence']}' not in {CONFIDENCE_LEVELS}"
            )
        if signal["volatility"] not in VOLATILITY_LABELS:
            raise SchemaValidationError(
                f"top_signals[{i}].volatility '{signal['volatility']}' not in {VOLATILITY_LABELS}"
            )
        if signal["origin_classification"] not in ORIGIN_CLASSIFICATIONS:
            raise SchemaValidationError(
                f"top_signals[{i}].origin_classification "
                f"'{signal['origin_classification']}' not in {ORIGIN_CLASSIFICATIONS}"
            )
        # optional field: default to 1 (single-source) if absent so old
        # reports remain valid.
        corroboration_count = signal.get("source_corroboration_count", 1)
        if not isinstance(corroboration_count, int) or corroboration_count < 1:
            raise SchemaValidationError(
                f"top_signals[{i}].source_corroboration_count must be an int >= 1, "
                f"got {corroboration_count!r}"
            )

    # optional field: only checked if present, so old reports without a
    # content_hash still validate.
    content_hash = data.get("content_hash", "")
    if content_hash:
        is_valid_hex = (
            isinstance(content_hash, str)
            and len(content_hash) == SHA256_HEX_LENGTH
            and all(c in "0123456789abcdef" for c in content_hash.lower())
        )
        if not is_valid_hex:
            raise SchemaValidationError(
                f"content_hash must be a {SHA256_HEX_LENGTH}-char hex sha256 digest, "
                f"got {content_hash!r}"
            )


def report_path(report_date: str) -> str:
    """path to data/reports/<report_date>.json (report_date = YYYY-MM-DD)"""
    return os.path.join(REPORTS_DIR, f"{report_date}.json")


def save_report(data: dict, validate: bool = True) -> str:
    """
    validate (optional) and write a report dict to
    data/reports/<report_date>.json. returns the path written.
    """
    # compute fixity checksum before validation so a bad hash the caller
    # supplied gets overwritten with the correct one rather than rejected.
    data["content_hash"] = compute_content_hash(data)

    if validate:
        validate_report(data)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = report_path(data["report_date"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def load_report(report_date: str) -> dict:
    """load a previously saved report by date (YYYY-MM-DD). raises FileNotFoundError if missing."""
    path = report_path(report_date)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_report_dates() -> list:
    """return sorted list of report dates (YYYY-MM-DD) available in data/reports/"""
    if not os.path.isdir(REPORTS_DIR):
        return []
    dates = [
        fname[:-5]
        for fname in os.listdir(REPORTS_DIR)
        if fname.endswith(".json")
    ]
    return sorted(dates)
