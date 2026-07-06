# Schema convention audit (run 31)

Systematic check for other instances of the run-30 `human_editor_note` failure
mode: a key that "looks consistently populated because most instances happen
to have it, but isn't a real dataclass field with validation behind it."

## Method

Read `src/report_schema.py` in full and enumerated every actual field:

- `Signal`: `name`, `type`, `source_sectors`, `confidence`, `volatility`,
  `origin_classification`, `evidence`, `index_note`,
  `source_corroboration_count`, `signal_id`, `confidence_source`,
  `human_editor_note` (the last one added in run 30).
- `Report`: `report_date`, `collection_window`, `sources_scanned`,
  `items_collected`, `source_sector_breakdown`, `executive_summary`,
  `top_signals`, `repeated_keywords`, `garments`, `silhouettes`, `materials`,
  `colors`, `aesthetic_terms`, `cultural_references`, `limitations`,
  `archive_tags`, `content_hash`, `collection_status`, `thin_week_note`,
  `revision_history`, `review_status`, `reviewed_by`.

Then scripted a scan of all 23 files in `data/reports/*.json`, collecting
every top-level key and every `top_signals[]` key, and diffed against the two
field lists above.

## Result: no other genuine instance of the pattern

- Every key in every `top_signals[]` entry across all 23 reports is already
  a real `Signal` field. No stray per-signal keys anywhere.
- Exactly one report, `data/reports/2026-05-07.json`, has extra top-level
  keys not in the `Report` dataclass: `source_links` (`[]`), `confidence_notes`,
  `volatility_notes`, `incentive_notes`, and `human_editor_note` (a top-level
  key here, distinct from the per-signal field added in run 30). Read the
  file directly — its own `human_editor_note` value says: *"Placeholder
  example report used to scaffold the archive and report page templates."*
  This is a single leftover scaffold/placeholder file, not a convention that
  spread across the corpus (1 of 23 reports, not "most"). It fails the
  defining criterion of the run-30 bug (looks consistently populated because
  many/most instances have it) — it's the opposite: an isolated one-off. Not
  promoting these to real fields; if anything they're candidates for cleanup
  of the placeholder file itself, out of scope here.

## Cross-check: REQUIRED_SIGNAL_KEYS / REQUIRED_TOP_LEVEL_KEYS

Every entry in both lists (`report_schema.py` lines 34-63) maps to an actual
dataclass field on `Report` or `Signal` respectively. No inconsistency found
in the other direction (a required-key list naming something that isn't a
real field).

## Conclusion

`human_editor_note` (per-signal) appears to have been the one real gap.
No changes made to `src/report_schema.py`, `manual_sample.py`, or any report
JSON this run.

## Verification

`python -m py_compile src/*.py` — passed.
`python src/validate_all_reports.py` — `OK: all 23 report(s) ... passed
schema validation.`

No commit made (per instructions).
