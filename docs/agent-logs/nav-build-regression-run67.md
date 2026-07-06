# Run 67 — build/regression re-check (no changes made)

**Scope:** full build verification, RSS `atom:link rel="self"` output check,
newest-2-report spot-check, internal link scan. Last swept run 66 (1 run
ago) — the RSS `atom:link` fix has since landed.

## Verification

`cd web && npx tsc --noEmit && npx eslint . && npm run build` — all three
clean. tsc: 0 errors. eslint: 0 errors/warnings. Build: compiled
successfully, static export generated 146 pages (up from 144 at run 66),
Pagefind indexed 141 pages. Only output was the pre-existing, expected
`[glossary] no DEFINITIONS entry for term "..."` notices for newly-added
terms — unrelated, same known pattern as prior runs.

## RSS atom:link check (built output, not source)

Read `web/out/rss.xml` directly: the channel element contains
`<atom:link href="https://ari3lla-index.example.com/rss.xml" rel="self" type="application/rss+xml" />`
correctly rendered as a self-closing element with the `xmlns:atom`
namespace declared on `<rss>`. Confirmed in the actual static-export
output, not just `route.ts` source.

## Spot-check: newest 2 report pages (2027-08-16, 2027-08-09)

Grepped built HTML in `web/out/reports/`:
- **Signal-anchor permalinks:** `id="signal-chanel-acquires-charvet"` and
  `id="signal-ragebait-runway-casting"` present on their respective pages.
- **Dark mode:** `globals.css` still has the `@media (prefers-color-scheme:
  dark)` block.
- **Skip-link:** `skip-link` class and `id="main-content"` both present on
  both pages.
- **Open Graph:** `og:title`, `og:description`, `og:url`, `og:site_name`,
  `og:type` all present on both pages.

## Internal link scan

Grepped every full `href="/..."` match across all `.tsx` files in
`web/app/**`. All targets (`/archive`, `/search`, `/timeline`, `/taxonomy`,
`/glossary`, `/methodology`) correspond to real routes per SKILL.md's file
map. No broken internal links found.

## Outcome

No regressions, nothing fixed because nothing was broken. Archive grew
from 144 to 146 static pages since run 66 (new reports 2027-08-09 and
2027-08-16 added). Everything held.
