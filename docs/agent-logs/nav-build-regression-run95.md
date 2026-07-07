# Run 95 — Full regression sweep (clean wipe)

2026-07-06 17:51 PDT

## Process check
Before starting, one stray `npm run build` and its `pagefind` postbuild child (PIDs 22668,
19200) were running — evidently a concurrent agent's own rebuild, per run instructions.
Waited (no kill) rather than treating as a conflict; both exited on their own within ~20s.
No python.exe processes found. No processes killed.

## Checks

1. **Clean wipe**: `rm -rf .next out` — done.
2. **`npx tsc --noEmit`**: PASS, no errors.
3. **`npx eslint .`**: PASS, no warnings/errors.
4. **`npm run build`**: PASS, fully completed from clean state.
   - `copy-reports`: 87 reports copied.
   - Next.js 16.2.4 (Turbopack) build succeeded, no warnings.
   - 210 static routes generated (87 `/reports/[date]`, 106 `/signals/[slug]`, plus fixed
     routes: `/`, `/about`, `/archive`, `/case-study`, `/glossary`, `/icon`, `/methodology`,
     `/robots.txt`, `/rss.xml`, `/search`, `/sitemap.xml`, `/sources`, `/taxonomy`,
     `/timeline`, `/_not-found`).
   - `postbuild` Pagefind indexing succeeded: 205 pages, 6289 words, 0 errors.
5. **Report count parity**: `data/reports/*.json` = 87, built `web/out/reports/` dirs = 87.
   Exact match.

## Prior-fix spot checks against built `web/out`

All confirmed intact:

- Signal-anchor deep-linking permalinks: `id="signal-<slug>"` present in
  `reports/2026-07-06.html` (e.g. `signal-sheer-layering`, `signal-soft-tailoring`).
- Dark mode CSS: `prefers-color-scheme` present in built CSS chunk.
- Skip-link: `#main-content` present (href + target) sitewide, checked on `index.html`.
- Open Graph meta tags: `og:title`, `og:description`, `og:type`, `og:url` all present on
  homepage.
- RSS: `atom:link` self-reference present, exactly 50 `<item>` elements in `rss.xml`.
- Corrections banner: renders on `reports/2026-05-07.html` (a report with a correction).
- Signal titles: real `<h3>` elements confirmed in `reports/2026-07-06.html` (not styled
  `<p>` tags).
- `/signals/[slug]` recency status line: confirmed present, e.g. on
  `signals/1990s-minimalism-revival.html`: "Last appeared 2026-07-06 — 85 published
  reports since, with no further occurrence on file."
- JSON-LD structured data: present on report pages (`reports/2026-07-06.html`, count 1),
  correctly absent on homepage (count 0) — matches by-design report-only scope.
- Sources/Taxonomy pages: both built (`sources.html`, `taxonomy.html`) with content.
- Archive year-grouping headers: `2026`, `2027`, `2028` all present in `archive.html`.
- `/timeline` page: renders correctly, 84 report links found linking to `/reports/*`
  (run 94's comment-only fix, frontend-invisible as expected — page itself unaffected
  and working).

## Regressions found

None. No code changes made, no commit made.
