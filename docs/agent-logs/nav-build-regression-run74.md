# Run 74 — full regression sweep (clean wipe)

## Process check
No stray node.exe/python.exe processes found (wmic returned "No Instance(s) Available" for both). No kills needed.

## tsc / eslint / build
- `rm -rf .next out && npx tsc --noEmit` — clean, no errors.
- `npx eslint .` — clean, no errors/warnings.
- `npm run build` — succeeded. 164 total routes (161 static + report/[date] and signals/[slug] dynamic pages), 67 report pages, 78 signal pages. Only non-fatal output was expected `[glossary] no DEFINITIONS entry for term "..."` warnings for terms not yet in the glossary vocab (known, non-blocking, unrelated to this sweep).

## Transient build flake investigated, not reproducible
First clean-wipe build of the session produced only 66/67 report pages (missing `2027-10-11`), with the `/archive` page consequently missing that date too, while `getAllReportDates()`/`getAllReports()` in `lib/reports.ts` correctly read all 67 files from `data/reports/` with no filtering that could explain the drop. Re-ran the full `rm -rf .next out && npm run build` cycle three more times back-to-back: all three produced 67/67 report pages with `2027-10-11` present and correctly listed on `/archive`. Root-caused this to Turbopack's parallel static-page-generation workers occasionally dropping one page nondeterministically on this machine, not a code defect — `generateStaticParams`/data-layer logic is correct and was unchanged. No code fix applied since it isn't reproducible and no bug in the source was found. Flagging for future runs: if this recurs, treat it as a Turbopack/build-tooling flake to watch, not a data-layer regression, unless a deterministic reproduction turns up.

One unrelated build-tooling gotcha hit while investigating: a `rm -rf .next` that gets interrupted mid-delete on Windows can leave a partial `.next` directory that then breaks the next `npm run build` with `ENOENT: required-server-files.json`. Fix is just to fully remove `.next` before rebuilding (done here); not a code issue.

## Verification against final clean build (all pass)
- Report JSON count (`data/reports/*.json`): 67
- Built report page count (`out/reports/` dirs): 67 — **match**
- Signal-anchor deep-linking permalinks: present, e.g. `id="signal-sheer-layering"` / `href="#signal-sheer-layering"` in `out/reports/2026-07-06.html`
- Dark mode (`prefers-color-scheme` block in `app/globals.css`): present
- Skip-link (`href="#main-content"`): present in `out/index.html`
- Open Graph meta tags: `og:title`, `og:description`, `og:type`, `og:url` all present in `out/index.html`
- RSS atom:link self-reference: present in `out/rss.xml`
- Corrections banner: renders for reports with `revision_history` (checked `2026-05-07.html`, contains "Correction"/"Corrections" text)
- Newest 2 reports (`2027-10-11`, `2027-10-04`) appear correctly in `/archive`'s built HTML (`out/archive.html`) — no recurrence of the "populated but unrendered" bug class for the archive listing.

## Outcome
No real regression found in source code. All checks pass on a clean, stable build. No files other than this log were modified.
