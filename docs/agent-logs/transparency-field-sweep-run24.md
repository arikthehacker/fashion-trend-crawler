# Transparency field sweep, run 24

Checked every field on `Signal`/`Report` in `src/report_schema.py` against
`web/lib/reports.ts` typing and actual rendering in the report, signal,
timeline, and search pages.

## Gap found and fixed: `thin_week_note`

`Report.thin_week_note` holds a substantive, per-window explanation of why a
report was marked thin (confirmed real content in `data/reports/2026-08-03.json`
— a specific paragraph about Copenhagen Fashion Week timing and recirculated
listicle content). The methodology page's "How Low-Volatility Windows Are
Reported" section makes a specific claim resting on this: "it is checked
against raw source volume for that window." Neither `web/app/page.tsx`
(homepage) nor `web/app/reports/[date]/page.tsx` rendered the field — both
only showed generic hardcoded boilerplate ("This window is classified
thin...") regardless of what the report's own note actually said. Also,
`collection_status`/`thin_week_note` were not in the `Report` TS interface at
all; call sites used inline `as unknown as {...}` casts instead.

**Fix:** added `collection_status?: string` and `thin_week_note?: string` to
`Report` in `web/lib/reports.ts`; removed the two now-unnecessary casts in
`reports.ts` (`getConsecutiveThinWeekCount`) and `web/app/page.tsx`. Appended
the real `thin_week_note` text to the homepage's existing thin-window banner.
Added a new "Collection Status: Thin" section (real `<h2>`, existing
`labelStyle`) to `web/app/reports/[date]/page.tsx`, rendered only when
`collection_status === "thin"`, showing `thin_week_note` with a generic
fallback string for older thin reports that predate the field.

## Everything else checked

- `source_corroboration_count`: typed, rendered ("Corroborated by N sources")
  on the report page. Fine.
- `human_editor_note`, `revision_history`: already fixed by runs 21/23 —
  confirmed still rendered correctly on the report page, no regression.
- `signal_id`: typed, drives links to `/signals/[slug]` on report, timeline,
  and search pages. Fine.
- `confidence_source` ("manual"/"derived"): not typed in `TopSignal`, not
  rendered anywhere. No methodology copy makes a reader-facing claim tied to
  this distinction (it's referenced only in `audit_confidence.py`'s internal
  non-blocking CI check). Left as backend-only bookkeeping — no gap.
- `review_status` / `reviewed_by`: not typed, not rendered. `reviewed_by` does
  hold real values (e.g. `"websearch-run-thin-week"`), and methodology's "AI
  Involvement" section says "a human reviews AI-assisted output before
  publication," but that claim isn't phrased as "and we'll show you who" —
  it's a general editorial-process statement, not a per-report disclosure
  promise the way "corrections are appended" or "checked against raw source
  volume" are. Borderline; flagged here for a future run rather than forced,
  since the sweep instructions say not to force fixes on fields without an
  active claim resting on them.
- `content_hash`: typed, rendered (archive checksum + citation line). Fine.
- `source_links`, `confidence_notes`, `volatility_notes`, `incentive_notes`
  (report-level): typed and rendered in the "Notes" section when present.
  Fine.
- All base `Signal`/`Report` required fields (name, type, source_sectors,
  confidence, volatility, origin_classification, evidence, index_note,
  executive_summary, top_signals, repeated_keywords, garments, silhouettes,
  materials, colors, aesthetic_terms, cultural_references, limitations,
  archive_tags, sources_scanned, items_collected, source_sector_breakdown,
  collection_window): all typed and rendered across report/timeline/search
  pages. No gaps.

**Verification:** `cd web && npx tsc --noEmit && npx next build` — both pass
clean, all 68 pages build.

Not committed per instructions.
