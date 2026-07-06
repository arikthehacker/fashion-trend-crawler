# Agent log: manual sampling workflow design

Scope: design/document only, no scraping code, per doc §31 and the prior research in
`docs/agent-logs/social-ingestion-research.md` (recommendation #1: manual sampling as
the immediate compliant path for TikTok/Pinterest).

## What was created

1. `docs/manual-sampling-template.md` — weekly fill-out template for a human observer.
   Fields map 1:1 onto `Signal` (`src/report_schema.py`): name, platform(s)/hashtag
   (feeds `source_sectors: ["social"]` per `taxonomy.py`), date observed, approximate
   volume/reach (or "unknown"), public source URL(s), observer notes
   (`human_editor_note`/`index_note`), corroboration count, and suggested
   confidence/volatility/origin_classification values drawn from the controlled
   vocabularies. Includes a filled-out example.
2. `src/manual_sample.py` — new, minimal (single function). `build_manual_signal(...)`
   takes the template's fields and returns a valid `Signal` with
   `source_sectors=["social"]`. Validates confidence/volatility/origin_classification
   against `taxonomy.py`'s vocabularies and raises `ValueError` if `human_editor_note` is
   empty, so a manually sampled signal can't skip the required human-judgment field.
   Deliberately does not touch `report_schema.py` itself — no schema changes were needed,
   `Signal` already supported everything required.
3. `docs/manual-sampling-workflow.md` — explains the why (ties back to the ingestion
   research's recommendation) and the four-step workflow (observe -> log -> transcribe ->
   fold into report), plus the guardrails it preserves (no scraping, human judgment
   required, no confidence inflation from editorial pickup, explicit corroboration
   counting).

## Verification

`python -m py_compile src/*.py` run from `src/` — passed clean (no errors).

## Not done (out of scope / left for later)

No changes to `report_schema.py`, `taxonomy.py`, `summarize.py`, or any frontend files.
No CHANGELOG.md entry added — leaving that to whoever consolidates, per this project's
convention of coordinator-driven consolidation.
