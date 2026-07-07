# Nav/build regression sweep — run 94

Branch: ari3lla-index-loop-improvements
Method: clean wipe practice (since run 72) — stray-process check, `rm -rf .next out`,
tsc, eslint, full build, then grep built `web/out` output for prior fixes.

## 1. Stray process check
`wmic process where "name='node.exe'"` and `python.exe` both returned "No Instance(s)
Available." No processes to kill.

## 2. Clean wipe + typecheck
`rm -rf .next out && npx tsc --noEmit` — clean, no output, no errors.

## 3. ESLint
`npx eslint .` — clean, no output, no errors/warnings.

## 4. Build
`npm run build` — succeeded, fully completed (no Pagefind race this run, unlike run 93's
transient failure; no concurrent processes were running per step 1).

- `prebuild`/`next.config.ts` copy-reports: copied 86 report(s) into
  `public/data/reports/`.
- Next.js 16.2.4 (Turbopack), compiled successfully in 1868ms, TypeScript finished in
  2.6s, 207 static pages generated (7 workers), no build warnings.
- Route summary: `/reports/[date]` — 86 paths; `/signals/[slug]` — 104 paths; plus
  `/`, `/about`, `/archive`, `/case-study`, `/glossary`, `/icon`, `/methodology`,
  `/robots.txt`, `/rss.xml`, `/search`, `/sitemap.xml`, `/sources`, `/taxonomy`,
  `/timeline`, `/_not-found`.
- `postbuild` Pagefind: indexed 202 pages, 1 language (en), 6262 words, 0 filters,
  0 sorts, finished in 6.335s. No indexing errors.

## 5. Grep of built `web/out` output (post-build, using `<route>.html` filenames per
static export convention, not `<route>/index.html`)

| Check | Result |
|---|---|
| Signal-anchor deep-linking permalinks (`id="signal-…"` in report pages) | present, 83 report pages |
| Dark mode CSS (`prefers-color-scheme`) | present in built CSS chunk |
| Skip-link (`#main-content`) | present in `index.html` |
| Open Graph meta tags | `og:title`, `og:description`, `og:type`, `og:url`, `og:site` all present |
| RSS `atom:link` self-reference | present, exactly 1 |
| RSS `<item>` count | exactly 50 |
| Corrections banner | renders on reports with corrections (e.g. 2026-05-07, 2026-07-20, 2026-08-03) |
| Signal titles as real `<h3>` | confirmed real `<h3>` elements in report pages |
| `/signals/[slug]` recency status line | confirmed, e.g. "Last appeared 2026-07-06 — 84 published reports since, with no further occurrence on file." |
| JSON-LD structured data | present on report pages (1 `application/ld+json` block), correctly absent on signal pages (by design) |
| Sources / Taxonomy page content | both present |
| Archive year-grouping headers | 2026, 2027, 2028 all present |

## 6. Report-page count vs data
`data/reports/*.json` = 86, built `web/out/reports/*.html` = 86. Match.

## 7. Other agents' concurrent work
No conflicting edits observed; `web/app/timeline/page.tsx` and `src/taxonomy.py` not
touched by this sweep. Build succeeded regardless of any concurrent in-progress work
from other agents.

## Conclusion
No regression found. All checks pass. No code changes made this run.
