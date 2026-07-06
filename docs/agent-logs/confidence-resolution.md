# Confidence resolution: Resale/secondhand retail growth (2026-07-13)

Per `docs/agent-logs/confidence-audit.md`, this signal was flagged as the one
genuinely concerning mismatch: assigned "high" confidence with
`source_corroboration_count=1`, where the derived formula says "medium" —
a single aggregated source (BoF/ThredUp coverage spanning three sectors)
being promoted past what independent corroboration actually supports.

## Path taken: found genuine second source, upgraded corroboration count

WebSearched for independent secondhand/resale market research for the
mid-2026 window. Found that GlobalData — a market-research firm — publishes
its own apparel resale market analysis directly (globaldata.com), separate
from the ThredUp-commissioned "2026 Resale Report" that BoF's State of
Fashion 2026 coverage cites. GlobalData's independently published figure
(global apparel resale market +85.5% from 2022–2026, to $338.4B) corroborates
the same growth trend as the BoF/ThredUp figures but is a distinct data
source and distinct outlet from a distinct market-research house — genuine
independent corroboration, not just the same aggregated source restated.

Changes to `data/reports/2026-07-13.json`, `resale-growth` signal only:
- `source_corroboration_count`: 1 -> 2
- `evidence`: now names both sources explicitly (BoF/McKinsey State of
  Fashion 2026, and GlobalData's independently published analysis)
- `index_note` and `human_editor_note`: updated to explain the re-review,
  cite `confidence-audit.md` as the reason, note the GlobalData source, and
  ask the editor to verify both sets of figures against primary documents
  before publication.
- `confidence` retained at "high" (now legitimately supported).
- `content_hash` recomputed via `report_schema.save_report()`.

No new `source_sectors` entry was needed — GlobalData's institutional
market-research role was already represented in `source_sectors`
(`institutional`); what was missing was a second independent instance, not
a new sector.

## Verification

- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — all 4 reports pass
- `python src/audit_confidence.py` — mismatches dropped from 14 to 13; the
  `resale-growth` "formula lower than assigned" case no longer appears
  (corroboration_count=2 now derives to "high", matching assigned).

Only `data/reports/2026-07-13.json` was modified. Not committed.
