# Run 81 — full regression sweep (clean wipe)

Branch: `ari3lla-index-loop-improvements`. Followed established clean-wipe practice (since run 72).

## 1. Stray process check
`wmic process where "name='node.exe'"` and `python.exe` both returned "No Instance(s) Available." — nothing to kill.

## 2. Clean wipe + `npx tsc --noEmit`
`rm -rf .next out` then typecheck. **PASS** — no output, no errors.

## 3. `npx eslint .`
**PASS** — no output, no errors/warnings.

## 4. `npm run build`
**PASS** — succeeded from clean state.
- 181 routes generated (per Next's route table): includes 74 `/reports/[date]` pages and 90 `/signals/[slug]` pages, plus static top-level pages (/, /about, /archive, /case-study, /glossary, /icon, /methodology, /search, /sources, /taxonomy, /timeline, /robots.txt, /rss.xml, /sitemap.xml, /_not-found).
- Non-fatal warning during static generation: `[glossary] no DEFINITIONS entry for term "restraint dressing" (from 2027-11-29) — term will not be shown on /glossary`. This is a data-content gap (a new report introduced a term not yet in the glossary DEFINITIONS map), not a build/regression failure — the build still succeeded and the term is simply omitted from /glossary rather than crashing. Likely tied to the "new report" docs-only work another agent is doing this run; not fixed here since it's a content/copy addition, not a code regression, and outside this run's file scope.
- Pagefind postbuild indexed 176 pages / 5929 words successfully.

## 5. Built-output grep checks (all confirmed present in `web/out`)
- Signal-anchor deep-linking permalinks: found in `reports/2026-07-06.html` (`id="signal-..."` anchors).
- Dark mode: `globals.css` has `@media (prefers-color-scheme: dark)` block — intact.
- Skip-link: `href="#main-content"` present on homepage.
- Open Graph meta: `og:title`, `og:description`, `og:type`, `og:url` all present.
- RSS `atom:link` self-reference present; exactly **50** `<item>` elements in `rss.xml` — matches expected cap.
- Corrections banner: renders on reports that have corrections (confirmed on 2026-05-07, 2026-07-20, 2026-08-03, 2026-08-24, 2026-08-31).
- Signal titles wrapped in real `<h3>` elements: confirmed on `reports/2026-07-06.html`.
- `/signals/[slug]` recency status line ("Last appeared ... — N published reports since ...") confirmed present across multiple signal pages.
- JSON-LD (`application/ld+json`) present on report pages (2 blocks found on `reports/2026-07-06.html`).

## 6. Report-page count vs data
`data/reports/*.json` = **74** files. `web/out/reports/*/ ` directories = **74**. Exact match — no drift.

## 7. Concurrent work / scope
No edits made to `taxonomy/page.tsx`, `sources/page.tsx`, or `check_signal_reuse_claims.py` this run, per instructions. The glossary-definition warning noted above looks like it stems from a new report/term (docs-only work in progress by another agent) rather than a pre-existing code regression, so it was left alone and just documented here.

## Outcome
**No real regression found.** All checks pass. No code changes made this run.
