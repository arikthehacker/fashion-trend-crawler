# Archival standards audit — run 82

## Dimension chosen and why

Three dimensions were on the table: (a) archival permanence/link-rot resistance, (b)
versioning/provenance metadata (reconstructing exactly what changed in a correction),
(c) editorial transparency about AI/automation involvement.

(c) was checked first and found already unusually thorough: `web/app/methodology/page.tsx`
("How AI Is Used," "AI Involvement," "Review Process" sections) and
`web/app/about/page.tsx` ("Independence, Corrections, AI Use") both explicitly disclose
that the same automated process that drafts a report also performs the nominal "human
review" step, that `crawler.py` is run directly for only a minority of windows (AI-directed
research substitutes for it otherwise), and that there is no separate named human editor —
stated as "a known limitation of the current process, not a claim this page makes
otherwise." This is a materially honest disclosure, not boilerplate, and no gap was found.
Confirmed clean; no changes made to (c).

(b) — versioning/provenance metadata — was chosen as the audited dimension, because it is
the most load-bearing for this project's stated identity as an *archival record*
(doc section 2/18/19: preserve what was published, corrections appended not silently
edited) and because `report_schema.py`'s `revision_history` mechanism is exactly the kind
of structural claim (not just prose) that this project's own SKILL.md workflow note #9
warns is easy to half-build: "a documented instruction is not the same as it actually
working."

## Research (with citations)

- IPTC News Architecture / NewsML-G2 and its provenance work (built on Project Origin)
  establish that professional news-archive provenance metadata should let a consumer
  verify not just that content is authentic at a point in time, but trace its history —
  the IPTC's cryptographic provenance layer exists specifically so downstream readers can
  confirm what changed and that nothing was tampered with since original publication.
  [News Architecture](https://iptc.org/standards/news-architecture/),
  [Media Provenance](https://iptc.org/media-provenance/)
- Poynter's corrections-policy guidance (Craig Silverman, cited via Poynter/IFCN
  materials) holds that a sound corrections policy needs three elements: a stated
  commitment to accuracy, a channel for correction requests, and a clear account of how
  corrections are *expressed and delivered* — not just that a correction exists, but what
  it actually says changed.
  [IFCN Code of Principles](https://ifcncodeofprinciples.poynter.org/the-commitments),
  [How news organizations are preparing to handle corrections today](https://www.poynter.org/news/how-news-organizations-are-preparing-handle-corrections-today)
- ONA Ethics on corrections: organizations should map a correction to the original error
  and make it possible for readers to actually see what was wrong and what replaced it,
  not merely that "an update was made."
  [ONA Ethics — Corrections](https://ethics.journalists.org/topics/corrections/)

Distilled standard: a correction record should let a reader reconstruct **what changed**,
not just confirm **that something changed**.

## Audit finding

Read `src/report_schema.py`'s `revision_history` mechanism end to end and cross-checked
against every report on disk (`data/reports/*.json`, 75 reports, ~40 revision_history
entries across ~25 files).

Each existing `revision_history` entry has exactly three fields: `previous_content_hash`
(a bare sha256 hex digest — a fixity checksum, not dereferenceable to any content),
`corrected_at`, and `reason` (free prose). The site (`web/app/reports/[date]/page.tsx`,
"Correction History" section) rendered only `corrected_at` and `reason`.

This is a genuine, concrete gap against the researched standard: the hash proves *that*
the report's `top_signals` content changed (tamper-evidence), and the prose `reason`
field is often good in this archive (spot-checked ~15 entries — most are specific, e.g.
"restored peplum skirt/peplum trouser... originally silently replaced with peplum jacket
with no note"), but nothing in the schema *structurally* required or verified precision.
A reader has no way to confirm the prose against the actual data — they must trust the
editor's prose summary rather than being able to see the diff itself. This is exactly the
"documented instruction ≠ actually working" pattern SKILL.md note #9 already flags as a
recurring bug class in this project (human_editor_note, revision_history, thin_week_note
were all previously found populated-but-unrendered; this is a sibling bug — rendered, but
without the underlying structural guarantee of completeness).

## Fix made

Added an automatic, structural per-signal diff to the correction pipeline so
completeness no longer depends solely on an editor's prose accuracy:

- `src/report_schema.py`: new `diff_signal_changes(old_signals, new_signals)` — compares
  two `top_signals` lists by `signal_id` and returns `{"added": [...], "removed": [...],
  "modified": {signal_id: [changed_field_name, ...]}}`.
- `save_report()` now calls this automatically whenever it detects a correction (differing
  content_hash) and stores the result as an optional `changed_signals` key on the new
  `revision_history` entry — computed from the actual old/new data, not caller-supplied,
  so it can't drift from what the reason prose claims.
- `validate_report()` type-checks `changed_signals` when present (dict; `added`/`removed`
  lists; `modified` dict) but treats it as optional, so all 75 existing reports (whose
  historical revision entries predate this field) remain valid without modification —
  confirmed via `python src/validate_all_reports.py` (all 75 pass, one pre-existing
  unrelated non-blocking confidence warning on 2027-05-17.json, not touched here).
- `web/lib/reports.ts`: typed `RevisionEntry.changed_signals`.
- `web/app/reports/[date]/page.tsx`: Correction History now renders Added/Removed/Modified
  signal_ids and field names beneath the existing prose reason, when present.
- `web/app/methodology/page.tsx`: Corrections section now states plainly that a correction
  records which signal_ids and fields changed, not just a prose explanation.

No existing `data/reports/*.json` files were modified — this only changes what
`save_report()` writes going forward. Adding `changed_signals` retroactively to the ~25
historical entries was considered and rejected: reconstructing the diff would require the
actual prior JSON content, which was overwritten in place (only its hash survives), so a
retroactive value would be either fabricated from the prose (unverifiable) or impossible;
better to leave historical entries as prose-only than manufacture false precision.

## Verification

- `python -m py_compile src/*.py` — passed.
- `python src/validate_all_reports.py` — all 75 reports pass; one pre-existing unrelated
  confidence warning, unchanged by this fix.
- `cd web && npx tsc --noEmit` — no errors.
- `cd web && npx eslint .` — no errors.
- `cd web && npm run build` — succeeded, all 179 pages (including all `/reports/[date]`
  and `/signals/[slug]` static paths) generated, Pagefind index rebuilt.

No data files, TODO.md, or CHANGELOG.md were touched, per instructions. This log is the
record of the change; a future consolidation pass should add a CHANGELOG.md entry.
