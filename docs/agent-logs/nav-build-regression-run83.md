# Full regression sweep — run 83 (clean wipe, since run 72 practice)

## 1. Stray process check
`wmic process where "name='node.exe'"` and `"name='python.exe'"` both returned
"No Instance(s) Available." — no stray serve/crawler/test processes to kill.

## 2. Clean wipe + typecheck
`cd web && rm -rf .next out && npx tsc --noEmit` — clean, no output, exit 0.

## 3. ESLint
`cd web && npx eslint .` — clean, no output, exit 0.

## 4. Production build
`cd web && npm run build` — succeeded from clean state (first attempt hit
"Another next build process is already running" — a concurrent agent's build,
not a regression; retried ~20s later and it completed normally).

- 75 reports copied by `scripts/copy-reports.mjs` (both prebuild hook and
  next.config.ts invocation, as expected).
- 184 total static params/routes generated (75 `/reports/[date]` + 92
  `/signals/[slug]` + 17 static top-level routes incl. `/`, `/archive`,
  `/search`, `/sitemap.xml`, `/rss.xml`, `/robots.txt`, `/icon`, etc.).
- No build warnings.
- Postbuild Pagefind indexing succeeded: 179 pages, 6001 words, 0 errors.

## 6. Report-page count vs data/reports
`data/reports/*.json` = 75. Built `web/out/reports/*/` directories = 75.
Exact match.

## 5. Built-output grep verification

| Check | Result |
|---|---|
| Signal-anchor deep-linking permalinks (`id="signal-..."`) | present, e.g. `reports/2026-07-06.html` |
| Dark mode (`prefers-color-scheme` block in globals.css) | present |
| Skip-link (`#main-content`) | present on homepage and report pages |
| Open Graph meta (`og:title`, `og:description`) | present |
| RSS `atom:link rel="self"` | present, points at SITE_URL/rss.xml |
| RSS `<item>` count | exactly 50 |
| Corrections banner | renders on reports that have corrections (2026-05-07, 2026-07-20, 2026-08-03, ...) |
| Signal titles as real `<h3>` | confirmed real `<h3>` elements, not styled `<p>` |
| `/signals/[slug]` recency status line | present (e.g. "recorded"/"since" language on signals/1990s-minimalism-revival.html) |
| JSON-LD structured data | `application/ld+json` present on report pages |
| Sources page recent-domain coverage | Sources page content reflects the expanded/non-Western-only outlet list (Nataal, OkayAfrica, FashionUnited India, Tokyo Fashion, etc.) plus Street/User-Generated and Resale/Secondhand sectors — intact |
| Taxonomy page Origin Classification section | present |

### New for run 83: `changed_signals` rendering check
`web/app/reports/[date]/page.tsx` (lines ~92-94, 612-639) does render
`revision_history[].changed_signals` (added/removed/modified) when populated —
code path confirmed present and structurally correct. However, checked all 75
reports in `data/reports/` programmatically: **no report has `changed_signals`
populated yet** (e.g. `2026-07-20.json` has 4 revision_history entries, all
with `changed_signals: null`). So this cannot yet be end-to-end verified
against real rendered output — noting per task instructions as "not yet
populated in any report," not a bug.

## 7. Concurrent work observed
`web/app/archive/page.tsx` shows uncommitted modifications (71 insertions/49
deletions) at time of this sweep — consistent with the UX-audit agent's
concurrent filtering/pagination work on that file. Untouched by this sweep,
per instructions. `web/app/search/page.tsx` showed no diff at time of check.
Two other agents' untracked log files also present
(`archive-search-ux-audit-run83.md`, `periodic-audit-run83.md`) — not touched.

## Regressions found
None. No fixes were necessary this run.
