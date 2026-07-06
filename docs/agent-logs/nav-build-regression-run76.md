# Nav/build regression sweep — run 76

Branch: `ari3lla-index-loop-improvements`. Clean-wipe regression sweep per established
practice since run 72.

## 1. Stray process check
`wmic process where "name='node.exe'"` and `python.exe` both returned "No Instance(s)
Available" — no stray leftover processes to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out` then `npx tsc --noEmit` — clean, no output, exit 0.

## 3. ESLint
`npx eslint .` — clean, no output, exit 0.

## 4. Production build
`npm run build` — **succeeded**. 166 routes generated (matches prior counts: static pages
+ 68 `/reports/[date]` + 68 `/signals/[slug]` + fixed routes). Pagefind postbuild indexed
161 pages / 5733 words successfully.

Glossary warnings seen (5): all for term source date **2027-10-18** — "return to
structure", "waist definition", "Inexmoda", "Bogota fashion week", "Vogue". This is a
**different date than run 75's gap** (run 75 left 5 open for the newest report's terms at
that time). This looks like a new report (2027-10-18) was added by a concurrent agent
during this run, with its glossary terms not yet backfilled into DEFINITIONS — consistent
with the task's warning that another agent may be adding a new report + terms this run.
Not treated as a regression; noting only.

## 5. Grep verification of prior fixes (against actual `web/out` build)
All confirmed intact:
- **Signal-anchor deep-linking permalinks**: `id="signal-*"` and matching `href="#signal-*"`
  present in `out/reports/2026-07-06.html` (e.g. `signal-sheer-layering`,
  `signal-soft-tailoring`).
- **Dark mode**: `prefers-color-scheme` present (2 occurrences) in `app/globals.css`.
- **Skip-link**: `<a href="#main-content" class="skip-link">` and `id="main-content"`
  present in `out/index.html`.
- **Open Graph meta tags**: `og:description`, `og:title`, `og:type`, `og:url` all present.
- **RSS atom:link self-reference**: `<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" type="application/rss+xml" />`
  present in `out/rss.xml`.
- **Corrections banner**: "correction" text found rendered in report HTML (checked
  2026-05-07, 2026-07-06, 2026-07-13, others also matched).

Note on build output layout: static export emits both a flat `reports/<date>.html` file
and a `reports/<date>/` directory (containing Next's internal `__next.*` payload files,
no `index.html`) — the actual rendered page content lives in the flat `.html` file, not
under the directory. Grepped the correct location after confirming this.

## 6. Report count match
`data/reports/*.json` = 68. Built output = 68 `reports/<date>.html` files (69 directories
under `out/reports` including the parent) and 68 `/signals/[slug]` — plus `copy-reports.mjs`
confirmed "copied 68 report(s)" during both prebuild and next.config.ts hook. Counts match
exactly.

## 7. Concurrent-work interference
No unexpected build errors. The only signal of concurrent activity was the 5 glossary
warnings for a new 2027-10-18 report — consistent with the task's heads-up that another
agent may be adding a new report + glossary terms this run. Did not touch
`web/app/signals/` or `globals.css`/`layout.tsx` beyond reading them for verification; no
evidence of in-progress edits there causing build issues.

## Regressions found
None. No code changes made this run — nothing to fix.
