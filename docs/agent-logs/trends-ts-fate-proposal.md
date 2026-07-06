# `web/lib/trends.ts` fate — migrate vs. retire (PENDING HUMAN DECISION)

## Findings

- `getTrends()` (`web/lib/trends.ts`) is imported in exactly one place: `web/app/page.tsx`
  — the **homepage**, not a peripheral page. It reads root-level `trends_raw.json` /
  `trends_summary.json` directly (both files currently exist on disk, from the run-8
  live-crawl output referenced in `docs/agent-logs/live-crawl-2026-07-06-real-output.json`).
- The homepage's "Observed Signals," "Trend summary," "Source Notes," and "Collected
  Items" sections are built entirely from this one-off live-crawl snapshot — a different
  data source from every other page (`archive/`, `reports/[date]/`, `timeline/`,
  `signals/[slug]/`), which all read `data/reports/*.json` via `web/lib/reports.ts`.
- `docs/ARI3LLA INDEX.txt` has no section describing a "live/current" view distinct from
  the weekly report — grepped for live-crawl/current-crawl/real-time/getTrends, no hits.
  The concept doc only describes the dated, source-linked archive.
- `CHANGELOG.md`'s earliest entries and `PROJECT_STRUCTURE.md` both label `trends.ts` as
  "existing — ORIGINAL data layer," i.e. pre-rebrand prototype code (crawler smoke-test
  UI), kept alive by inertia rather than by design intent.
- Net effect: the site's front door currently shows an un-versioned, non-archived,
  possibly stale one-off crawl, while the actual product (dated weekly reports) lives one
  click away at `/archive`. This is a real inconsistency, not just leftover cruft.

## Option A — Migrate

Rewrite `getTrends()` to read the latest entry from `data/reports/` via
`report_schema`-equivalent logic in `web/lib/reports.ts`, then update `page.tsx` to render
the latest `Report`'s fields instead of `TrendsData`.
- Touches: `web/lib/trends.ts` (rewritten or deleted), `web/app/page.tsx` (rewired to
  `reports.ts`), possibly a new `getLatestReport()` helper in `reports.ts`.
- Pros: homepage becomes consistent with the rest of the site; one data model; no legacy
  file dependency.
- Cons: `trends.ts`'s shape (`pages`, raw headlines, `sources_summary`) doesn't map
  cleanly onto the `Report`/`Signal` schema — this is a rewrite of the homepage, not a
  data-layer swap.

## Option B — Retire

Delete `web/lib/trends.ts`, rewrite `page.tsx` to be a pure landing/masthead page (tagline
+ nav + "latest report" teaser pulled from `reports.ts`, linking to `/archive` or
`/reports/[date]`), then delete the four legacy files (`trends_raw.json`,
`trends_summary.json`, and their `src/`-level copies) per migration steps 1-4.
- Touches: `web/lib/trends.ts` (deleted), `web/app/page.tsx` (simplified), 4 legacy JSON
  files (deleted), unblocks migration step 5.
- Pros: matches what the project actually is now — an archival weekly report index, not a
  live-crawl dashboard. Removes an entire parallel, un-versioned data path.
- Cons: loses the "raw headlines" transparency view; would need a small design decision on
  what replaces it on the homepage (a teaser pulled from `reports.ts` is the natural fit,
  scoped separately).

## Recommendation

**Option B (retire), scoped as a homepage rewrite + migration-step-5 cleanup.** The
project's current shape is an archival weekly report site (per the skill doc and every
other page's data source); a live, un-dated crawl snapshot on the homepage contradicts
that and creates a second, inconsistent front door into the product. Nothing in the
concept doc calls for a distinct live view. Migrating `trends.ts` onto the report schema
(Option A) would just reinvent `reports.ts` under a different name.

**TODO (not to be executed unilaterally — needs explicit sign-off):** add to `TODO.md` —
"Decide + implement: retire `web/lib/trends.ts`, rewrite `page.tsx` to pull a latest-report
teaser from `reports.ts`, then delete the 4 legacy `trends_raw.json`/`trends_summary.json`
files (completes migration step 5)."
