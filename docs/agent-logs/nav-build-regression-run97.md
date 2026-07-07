# Nav/build regression sweep — run 97

Branch: ari3lla-index-loop-improvements. Clean-wipe regression sweep per established
practice (since run 72).

## Pre-flight

No stray node.exe/python.exe processes found (`wmic process where "name='node.exe'"` and
`name='python.exe'` both returned "No Instance(s) Available"). No concurrent build to wait on.

## Checks

1. `rm -rf .next out` then `npx tsc --noEmit` — **clean**, no output/errors.
2. `npx eslint .` — **clean**, no output/errors.
3. `npm run build` — **succeeded, fully completed.** 216 routes total: 89 `/reports/[date]`
   pages, 110 `/signals/[slug]` pages, plus static pages (home, archive, about, case-study,
   glossary, methodology, search, sources, taxonomy, timeline, sitemap.xml, robots.txt,
   rss.xml, icon). No warnings emitted by Next/tsc during build. `copy-reports.mjs`
   (prebuild + next.config.ts) copied 89 reports as expected. Pagefind postbuild indexed
   211 pages / 6342 words / 0 errors.
4. Report-page count vs `data/reports/*.json`: **89 = 89, exact match.**

## Built-output verification (web/out)

- Signal-anchor deep-linking permalinks (`id="signal-*"`): present, 86/89 report pages
  (some reports legitimately have fewer/no top_signals blocks — not a regression).
- Dark mode CSS (`prefers-color-scheme`): present in built CSS chunk.
- Skip-link (`#main-content`): present on homepage.
- Open Graph meta (`og:title`): present.
- RSS: `atom:link` self-reference present, exactly 50 `<item>` elements — matches spec.
- Corrections banner (revision_history/correction rendering): present, 37 report pages.
- Signal titles wrapped in real `<h3>`: confirmed on report page.
- `/signals/[slug]` recency status line: confirmed present (recurrence/"since" wording).
- JSON-LD structured data: present on report pages only (1 script tag), absent on
  homepage — correct, by design.
- Sources/Taxonomy page content: confirmed present on both.
- Archive year-grouping headers: 2026, 2027, 2028 all present.
- `/timeline` page: renders correctly, 86 unique `/reports/<date>` links found.

Static export confirmed to emit `<route>.html` files (not `<route>/index.html>`) — all
greps above targeted flat `.html` paths accordingly.

## Regressions found

None. All prior fixes remain intact. No code changes were made.

## Other agents' concurrent work

No other agents' report-file changes observed during this sweep's window; build reflects
current committed `data/reports/` (89 files) cleanly.
