# Journalism & archival practices research

Research pass for ARI3LLA INDEX sourcing/confidence conventions, archival integrity, and wire-service tone. Findings only — no code changed.

## 1. Multi-source corroboration raises confidence, single-source lowers it
Standard newsroom practice treats a claim backed by one source as provisional and a claim confirmed by multiple independent sources as more reliable; reporters are trained to seek out all parties/sides before treating a fact as solid, and to make sourcing distinctions visible to the reader rather than flattening them.
Source: AP Stylebook attribution guidance, via Hood College Library Research Guide — https://hood.libguides.com/citation/ap

**Recommendation:** Add a `source_corroboration_count` (or `corroborating_sources: list[str]`) field to `Signal` in `src/report_schema.py`, and derive/display `confidence` partly from that count rather than as a purely manual classification — e.g. single-sector-single-outlet signals default to "low/unconfirmed" unless a second independent outlet corroborates.

## 2. Attribution phrasing should name the source type, not just the outlet
AP guidance requires attributing opinion, other outlets' reporting, and data/graphics explicitly (e.g. "according to X"), so readers can judge the claim by who is speaking, not just what was said.
Source: AP Stylebook attribution guidance, via Hood College Library Research Guide — https://hood.libguides.com/citation/ap

**Recommendation:** In `summarize.py`'s prompt, require every generated Signal's summary text to include an explicit "according to [outlet], a [sector] source" clause pulled from `taxonomy.classify_source(url)`, so the sector classification is legible in the prose itself, not just the JSON metadata.

## 3. Fixity checksums detect silent corruption/tampering of archived files
Digital preservation orgs recommend generating a cryptographic hash (SHA-256 or similar) for each preserved file at ingest time, storing it alongside the file, and periodically re-checking it — this is the core "fixity" practice for proving a file hasn't changed since archival.
Source: Digital Preservation Coalition, "Fixity and checksums," Digital Preservation Handbook — https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums

**Recommendation:** Add a `checksum: str` field (SHA-256 of the canonical JSON body) to the `Report` dataclass in `src/report_schema.py`, computed in `save_report()` at write time, so `data/reports/<date>.json` archives are independently verifiable against tampering or accidental edits.

## 4. Redundant copies in separate locations, not just one canonical file
NDSA/DPC guidance holds that a single stored copy is not preservation — the baseline is multiple copies in at least two separate storage environments, checked against each other periodically.
Source: NDSA Fixity Guidance Report, National Digital Stewardship Alliance / digitalpreservation.gov — https://www.digitalpreservation.gov/documents/NDSA-Fixity-Guidance-Report-final100214.pdf

**Recommendation:** This is a repo-hygiene note rather than a code field: document in `docs/CHANGELOG.md`/README that `data/reports/*.json` should be pushed to the git remote (not left local-only) as its second copy, since git history + remote already gives redundancy and diff-based tamper visibility for free — no new infra needed, just don't skip pushing archived reports.

## 5. Wire-service neutrality: balanced attribution verbs, no editorializing
Reuters' house style frames neutrality as reporting all sides with no agenda beyond factual accuracy, favoring measured, attribution-anchored verbs ("said," "reported," "acknowledged") over evaluative language, and formal/factual tone over color writing.
Source: Reuters Handbook of Journalism, cited via Media Reform Coalition PDF — https://www.mediareform.org.uk/wp-content/uploads/2015/12/Reuters_Handbook_of_Journalism.pdf

**Recommendation:** Add a lint-style check (or a short list in the `summarize.py` prompt) banning evaluative verbs the concept doc's voice rules already gesture at (e.g. "declared," "revealed," "proves") in favor of the AP/Reuters set (said, reported, noted, showed) — enforce this as an explicit constraint in the Claude prompt in `summarize.py`, not just an implicit tone instruction.
