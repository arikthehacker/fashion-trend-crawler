#############################################################
# manual_sample.py
# minimal helper for the manual social-signal sampling workflow
# (docs/manual-sampling-workflow.md, docs/manual-sampling-template.md).
#
# TikTok/Pinterest ingestion is compliant-path-only per doc §31 —
# no scraping. A human fills out the markdown template, then this
# module turns those fields into a valid Signal (report_schema.py)
# tagged source_sectors=["social"] (taxonomy.py).
#############################################################

from report_schema import Signal
from taxonomy import CONFIDENCE_LEVELS, VOLATILITY_LABELS, ORIGIN_CLASSIFICATIONS


def build_manual_signal(
    name: str,
    human_editor_note: str,
    confidence: str,
    volatility: str,
    origin_classification: str,
    evidence: str = "",
    source_corroboration_count: int = 1,
    signal_type: str = "social_observation",
) -> Signal:
    """
    construct a valid Signal from a filled-out manual sampling
    template entry (docs/manual-sampling-template.md). always tags
    source_sectors as ["social"] since this path exists specifically
    for human-observed TikTok/Pinterest/etc. signals.

    `evidence` should hold the public source URL(s) and any
    volume/reach notes from the template; `human_editor_note` is the
    observer's own judgment (required — this is the human-in-the-loop
    field, not something to auto-fill).

    raises ValueError if confidence/volatility/origin_classification
    aren't in the controlled vocabularies, or if human_editor_note is
    empty (a manually-sampled signal with no observer judgment isn't
    a real entry).
    """
    if not human_editor_note.strip():
        raise ValueError("human_editor_note is required for manually sampled signals")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence '{confidence}' not in {CONFIDENCE_LEVELS}")
    if volatility not in VOLATILITY_LABELS:
        raise ValueError(f"volatility '{volatility}' not in {VOLATILITY_LABELS}")
    if origin_classification not in ORIGIN_CLASSIFICATIONS:
        raise ValueError(
            f"origin_classification '{origin_classification}' not in {ORIGIN_CLASSIFICATIONS}"
        )
    if source_corroboration_count < 1:
        raise ValueError("source_corroboration_count must be >= 1")

    return Signal(
        name=name,
        type=signal_type,
        source_sectors=["social"],
        confidence=confidence,
        volatility=volatility,
        origin_classification=origin_classification,
        evidence=evidence,
        index_note=human_editor_note,
        # also populate the dedicated human_editor_note field (rendered
        # separately on the site as "Editor review: ..."). Two of the three
        # prior manual-sampling exercises only set index_note because this
        # field didn't exist on the Signal dataclass yet, so their entries
        # never showed "Editor review" on the live site even though the
        # workflow's own docs treat human_editor_note as the required
        # human-in-the-loop field — see
        # docs/agent-logs/manual-sampling-quality-check-run30.md.
        human_editor_note=human_editor_note,
        source_corroboration_count=source_corroboration_count,
    )
