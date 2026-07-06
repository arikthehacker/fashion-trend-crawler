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

from taxonomy import CONFIDENCE_LEVELS, VOLATILITY_LABELS, ORIGIN_CLASSIFICATIONS, SOURCE_SECTORS

# sectors treated as "high-reliability" for the medium-confidence single-source
# gate in derive_confidence() (see docs/agent-logs/confidence-scoring-research.md).
# only includes names that actually exist in taxonomy.SOURCE_SECTORS.
HIGH_RELIABILITY_SECTORS = [
    s for s in ("editorial", "designer_origin", "institutional") if s in SOURCE_SECTORS
]

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
    # URL-safe slug identifying this signal across reports for recurrence
    # tracking (e.g. "sheer-layering"), assigned by summarize.py or a human
    # editor note — see docs/agent-logs/signals-timeline-design.md. optional/
    # backward compatible: empty string until assigned; old reports without
    # it still validate.
    signal_id: str = ""
    # whether `confidence` was hand-set by the LLM/editor ("manual", default)
    # or computed by derive_confidence() ("derived"). optional/backward
    # compatible: old reports without it are treated as "manual" since they
    # predate the derivation formula — see
    # docs/agent-logs/confidence-derivation-impl.md.
    confidence_source: str = "manual"


CONFIDENCE_SOURCE_VALUES = ["manual", "derived"]

# valid values for Report.collection_status — see
# docs/agent-logs/thin-week-fallback.md and gap-analysis-run6.md #4 (Nieman
# Lab burnout research: an honest low-signal report state should exist
# instead of inflating weak signals to fill a quota every week).
COLLECTION_STATUS_VALUES = ["normal", "thin"]


def derive_confidence(signal) -> str:
    """
    compute a confidence tier from a signal's corroboration count and
    source-sector diversity, per the formula researched in
    docs/agent-logs/confidence-scoring-research.md (ICD 203 / CTI /
    commercial-forecasting convergence: cross-sector corroboration, not
    raw mention count, is the real confidence signal).

    accepts either a Signal instance or a plain dict with the same keys
    (source_corroboration_count, source_sectors, confidence).

    - "archival" is never derived: if the signal's existing confidence is
      already "archival" (a manually-flagged tier), it is returned
      unchanged.
    - "high": corroboration_count >= 2 AND >= 2 distinct source_sectors.
    - "medium": corroboration_count >= 2 from a single sector, OR
      corroboration_count == 1 from a high-reliability sector
      (HIGH_RELIABILITY_SECTORS).
    - "low": everything else (typically count == 1, non-high-reliability
      sector, e.g. a lone social mention).

    this is a standalone helper — it does not mutate the signal or get
    called automatically by save_report()/validate_report(). summarize.py
    or a human editor can call it to cross-check or override the LLM's
    confidence assignment, setting confidence_source="derived" if they
    adopt the result.
    """
    if isinstance(signal, dict):
        existing_confidence = signal.get("confidence", "")
        corroboration_count = signal.get("source_corroboration_count", 1)
        source_sectors = signal.get("source_sectors", []) or []
    else:
        existing_confidence = getattr(signal, "confidence", "")
        corroboration_count = getattr(signal, "source_corroboration_count", 1)
        source_sectors = getattr(signal, "source_sectors", []) or []

    if existing_confidence == "archival":
        return "archival"

    distinct_sectors = set(source_sectors)

    if corroboration_count >= 2 and len(distinct_sectors) >= 2:
        return "high"

    if corroboration_count >= 2 and len(distinct_sectors) == 1:
        return "medium"

    if corroboration_count == 1 and distinct_sectors & set(HIGH_RELIABILITY_SECTORS):
        return "medium"

    return "low"


def get_signal_status_history(signal_id: str, all_reports: list) -> list:
    """
    walk `all_reports` (a list of report dicts, e.g. loaded via
    load_report()/list_report_dates()) and return the volatility/confidence
    trend for a given signal_id over time.

    see docs/agent-logs/signal-dormancy-mechanism.md for why this exists
    instead of a static `signal_status` field on Signal: "dormant" isn't a
    property of a single signal entry, it's an observation about a gap in
    recurrence across reports, so it belongs to the cross-report history,
    not the schema of one report's signal. VOLATILITY_LABELS already
    includes "declining", and adding a parallel "dormant"/"retired" status
    field would just be a second, easily-desynced way of saying the same
    thing derive_confidence()-style logic can read off history directly.

    returns a list of entries sorted by report_date ascending, each:
      {
        "report_date": str,
        "volatility": str,
        "confidence": str,
        "confidence_source": str,
      }
    for every report in which a top_signals entry has this signal_id.
    empty list if signal_id never appears (e.g. flagged dormant with no
    corroborating recurrence, or the id is unrecognized).
    """
    history = []
    for report in all_reports:
        report_date = report.get("report_date", "")
        for signal in report.get("top_signals", []):
            if signal.get("signal_id", "") == signal_id:
                history.append({
                    "report_date": report_date,
                    "volatility": signal.get("volatility", ""),
                    "confidence": signal.get("confidence", ""),
                    "confidence_source": signal.get("confidence_source", "manual"),
                })
    history.sort(key=lambda entry: entry["report_date"])
    return history


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
    # "normal" (default) or "thin" — marks a collection window where too few
    # genuinely distinct signals were found to responsibly fill the usual
    # signal quota. optional/backward compatible: old reports without it are
    # treated as "normal". see docs/agent-logs/thin-week-fallback.md.
    collection_status: str = "normal"
    # human/LLM-authored explanation used when collection_status == "thin",
    # e.g. "Fewer than 3 sources returned signals this window; report
    # reflects limited coverage rather than manufactured trends." optional/
    # backward compatible: empty string when not thin.
    thin_week_note: str = ""
    # audit trail of corrections made to this report after initial save.
    # each entry: {"previous_content_hash": str, "corrected_at": str (ISO
    # date string, caller-supplied for determinism/testability), "reason":
    # str (non-empty, required)}. populated by save_report() itself when it
    # detects it's overwriting an existing report file for this date with
    # differing content — see docs/agent-logs/retention-versioning-design.md.
    # optional/backward compatible: old reports without it default to [].
    revision_history: list = field(default_factory=list)

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

        # optional field: only validated when non-empty, so reports without
        # a signal_id (assigned pre-slug-field or never editorially linked)
        # still validate. must be a lowercase-alphanumeric-with-hyphens slug.
        signal_id = signal.get("signal_id", "")
        if signal_id:
            is_valid_slug = (
                isinstance(signal_id, str)
                and all(c.islower() or c.isdigit() or c == "-" for c in signal_id)
                and not signal_id.startswith("-")
                and not signal_id.endswith("-")
                and "--" not in signal_id
            )
            if not is_valid_slug:
                raise SchemaValidationError(
                    f"top_signals[{i}].signal_id must be a lowercase "
                    f"alphanumeric-with-hyphens slug, got {signal_id!r}"
                )

        # optional field: default to "manual" if absent so old reports
        # (predating derive_confidence()) remain valid.
        confidence_source = signal.get("confidence_source", "manual")
        if confidence_source not in CONFIDENCE_SOURCE_VALUES:
            raise SchemaValidationError(
                f"top_signals[{i}].confidence_source '{confidence_source}' "
                f"not in {CONFIDENCE_SOURCE_VALUES}"
            )

    # optional field: default to "normal" if absent so old reports (predating
    # the thin-week fallback) remain valid.
    collection_status = data.get("collection_status", "normal")
    if collection_status not in COLLECTION_STATUS_VALUES:
        raise SchemaValidationError(
            f"collection_status '{collection_status}' not in {COLLECTION_STATUS_VALUES}"
        )

    # optional field: only checked if present, so old reports without a
    # content_hash still validate.
    # optional field: default to [] if absent so old reports (predating
    # revision_history) remain valid.
    revision_history = data.get("revision_history", [])
    if not isinstance(revision_history, list):
        raise SchemaValidationError("revision_history must be a list")
    for i, entry in enumerate(revision_history):
        if not isinstance(entry, dict):
            raise SchemaValidationError(f"revision_history[{i}] must be a dict")
        missing_rev_keys = [
            k for k in ("previous_content_hash", "corrected_at", "reason") if k not in entry
        ]
        if missing_rev_keys:
            raise SchemaValidationError(
                f"revision_history[{i}] missing keys: {missing_rev_keys}"
            )
        prev_hash = entry["previous_content_hash"]
        is_valid_hex = (
            isinstance(prev_hash, str)
            and len(prev_hash) == SHA256_HEX_LENGTH
            and all(c in "0123456789abcdef" for c in prev_hash.lower())
        )
        if not is_valid_hex:
            raise SchemaValidationError(
                f"revision_history[{i}].previous_content_hash must be a "
                f"{SHA256_HEX_LENGTH}-char hex sha256 digest, got {prev_hash!r}"
            )
        if not isinstance(entry["corrected_at"], str) or not entry["corrected_at"]:
            raise SchemaValidationError(
                f"revision_history[{i}].corrected_at must be a non-empty string"
            )
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise SchemaValidationError(
                f"revision_history[{i}].reason must be a non-empty string"
            )

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


def save_report(
    data: dict,
    validate: bool = True,
    revision_reason: str = None,
    corrected_at: str = None,
) -> str:
    """
    validate (optional) and write a report dict to
    data/reports/<report_date>.json. returns the path written.

    if a report already exists for this date and its content differs from
    the new content (by content_hash), this is treated as a correction:
    both `revision_reason` (non-empty string explaining the correction) and
    `corrected_at` (an ISO date string) must be supplied by the caller —
    this function deliberately does not call datetime.now() so behavior
    stays deterministic/testable. An entry recording the OLD content_hash,
    `corrected_at`, and `reason` is appended to `revision_history` before
    the new content_hash is computed and written. See
    docs/agent-logs/retention-versioning-design.md.

    if no existing report exists for this date (first save), no
    revision_history entry is created and `revision_reason`/`corrected_at`
    are not required.
    """
    new_hash = compute_content_hash(data)

    existing_path = report_path(data["report_date"])
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        old_hash = existing_data.get("content_hash", "")
        if old_hash and old_hash != new_hash:
            if not revision_reason or not str(revision_reason).strip():
                raise SchemaValidationError(
                    "save_report() is overwriting an existing report with "
                    "differing content; a non-empty revision_reason is required"
                )
            if not corrected_at or not str(corrected_at).strip():
                raise SchemaValidationError(
                    "save_report() is overwriting an existing report with "
                    "differing content; a non-empty corrected_at (ISO date "
                    "string) is required"
                )
            revision_history = list(existing_data.get("revision_history", []))
            revision_history.append({
                "previous_content_hash": old_hash,
                "corrected_at": corrected_at,
                "reason": revision_reason,
            })
            data["revision_history"] = revision_history
        elif "revision_history" not in data:
            data["revision_history"] = existing_data.get("revision_history", [])
    elif "revision_history" not in data:
        data["revision_history"] = []

    # compute fixity checksum before validation so a bad hash the caller
    # supplied gets overwritten with the correct one rather than rejected.
    data["content_hash"] = new_hash

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
