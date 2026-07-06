# Fixity fields UI display

Surfaced the two schema fields from `docs/agent-logs/schema-fixity-fields.md`
in the per-date report page.

## Changes

1. `web/lib/reports.ts` — added `source_corroboration_count?: number` to
   `TopSignal` and `content_hash?: string` to `Report`, so the new
   `src/report_schema.py` fields type-check when present in JSON.
2. `web/app/reports/[date]/page.tsx`:
   - Per-signal metadata row now appends `Corroborated by N sources` only
     when `source_corroboration_count > 1`, matching the existing
     uppercase/tracked label style. Single-source signals show nothing extra
     (no noise for the default case of 1).
   - Added a small monospace footer line below the nav footer, shown only
     when `content_hash` is present: `Archive checksum: <first 12 chars>`.
     Styled with `var(--gray)` and a small font size to stay unobtrusive —
     archival metadata, not a feature callout.

Both additions are additive/conditional; no existing structure was touched.
Made no changes near the `/signals/[slug]` link work or the new
2026-07-13 signal data being added concurrently by other agents — both
were present in the tree by build time and compiled cleanly alongside
these changes.

## Verification

`cd web && npx tsc --noEmit && npx next build` — passed clean, all routes
(including `/reports/2026-07-13` and `/signals/[slug]` pages from the
concurrent work) generated successfully.

Not committed, per instructions.
